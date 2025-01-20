import asyncio
import datetime
from typing import Optional, List
from model.main_model import Delivery, Return
from sqlalchemy.orm import Session
import aioredis

from schema.dashboard_schema import (
    DashboardParams,
    DashboardResponse,
    DashboardDetail,
    DashboardItem,
)
from repository.mysql_repository import MySQLRepository
from repository.redis_repository import RedisRepository
import logging

logger = logging.getLogger(__name__)


class DashboardService:
    def __init__(self, db: Session, redis: aioredis.Redis):
        self.mysql_repo = MySQLRepository(db)
        self.redis_repo = RedisRepository(redis)
        self.db = db

    async def get_dashboard_items(self, params: DashboardParams) -> DashboardResponse:
        """대시보드 목록 조회"""
        try:
            # 대기 상태 작업 동기화를 명시적으로 호출
            await self.sync_waiting_tasks()

            items = await self.redis_repo.get_all()
            if items is None:
                items = []

            filtered_items = self._filter_items(items, params)

            # 페이지네이션
            total_count = len(filtered_items)
            total_pages = (total_count + params.limit - 1) // params.limit
            start_idx = (params.page - 1) * params.limit
            end_idx = start_idx + params.limit

            return DashboardResponse(
                totalCount=total_count,
                data=filtered_items[start_idx:end_idx],
                currentPage=params.page,
                totalPages=total_pages,
            )
        except Exception as e:
            print(f"Error in get_dashboard_items: {e}")
            raise

    def _filter_items(self, items, params: DashboardParams):
        """아이템 필터링 로직 분리"""
        filtered_items = []
        for item in items:
            if params.status and item["status"] != params.status:
                continue
            if params.driver_id and item.get("driver_id") != params.driver_id:
                continue
            if params.search:
                search_lower = params.search.lower()
                if not any(
                    search_lower in str(item.get(field, "")).lower()
                    for field in ["dps", "customer", "address", "contact"]
                ):
                    continue
            filtered_items.append(DashboardItem(**item))
        return filtered_items

    async def assign_driver(self, driver_id: int, dps_list: List[str]) -> bool:
        """기사 할당"""
        success_count = 0

        for dps in dps_list:
            item = await self._update_task_status(
                dps, status="진행", driver_id=driver_id
            )
            if item:
                success_count += 1

        return success_count > 0

    async def update_status(self, dps: str, new_status: str) -> bool:
        """작업 상태 업데이트"""
        return await self._update_task_status(dps, new_status) is not None

    async def _update_task_status(
        self, dps: str, status: str, driver_id: Optional[int] = None
    ) -> Optional[dict]:
        try:
            # 트랜잭션 시작
            with self.db.begin():
                # MySQL에서 먼저 데이터 조회 및 업데이트
                if status == "delivery":
                    task = self.db.query(Delivery).filter(Delivery.dps == dps).first()
                else:
                    task = self.db.query(Return).filter(Return.dps == dps).first()

                if not task or task.status != "대기":
                    return None

                # 상태 및 기사 정보 업데이트
                task.status = status
                if driver_id is not None:
                    task.driver = driver_id

                # 시간 정보 업데이트
                now = datetime.now()
                if status == "진행":
                    if isinstance(task, Delivery):
                        task.depart_time = now
                    else:
                        task.dispatch_date = now
                elif status in ["완료", "이슈"]:
                    if isinstance(task, Delivery):
                        task.completed_time = now
                    else:
                        # Return 타입에 대한 처리가 필요하다면 여기에 추가
                        pass

                # Redis에 저장할 데이터 준비
                item = self._to_dict(task)
                item["type"] = "delivery" if isinstance(task, Delivery) else "return"
                item["status"] = status

                # 병렬로 Redis와 상태 동기화
                redis_task = asyncio.create_task(
                    self.redis_repo.save_task(item["type"], item)
                )

                # 트랜잭션 종료 (자동 커밋)
                self.db.flush()

                # Redis 저장 대기
                redis_success = await redis_task

                return item if redis_success else None

        except Exception as e:
            # 로깅 및 롤백
            logger.error(f"Task status update failed: {e}")
            self.db.rollback()
            raise

    async def get_dashboard_detail(self, dps: str) -> Optional[DashboardDetail]:
        """작업 상세 정보 조회"""
        item = await self.redis_repo.get_by_dps(dps)
        return DashboardDetail(**item) if item else None

    async def sync_waiting_tasks(self):
        """대기 상태 작업 동기화"""
        try:
            # MySQL에서 대기 상태 작업 조회
            tasks = self.mysql_repo.get_waiting_tasks()
            logger.info(f"Found delivery tasks: {len(tasks['deliveries'])}")
            logger.info(f"Found return tasks: {len(tasks['returns'])}")

            # Redis에 작업들 저장
            await self._save_tasks(tasks["deliveries"], "delivery")
            await self._save_tasks(tasks["returns"], "return")

        except Exception as e:
            logger.error(f"Error syncing waiting tasks: {e}")
            raise

    async def _save_tasks(self, tasks, task_type):
        """공통 태스크 저장 메서드"""
        for task in tasks:
            try:
                # SQLAlchemy 객체를 딕셔너리로 변환
                task_dict = self._to_dict(task)
                task_dict["type"] = task_type

                # Redis에 저장
                await self.redis_repo.save_task(task_type, task_dict)

            except Exception as e:
                logger.error(f"Error saving {task_type} task: {e}")

    def _to_dict(self, obj):
        """SQLAlchemy 객체를 딕셔너리로 변환"""
        columns = obj.__table__.columns
        return {c.name: getattr(obj, c.name) for c in columns}

    async def full_sync_at_midnight(self):
        """전체 재동기화 (2동기화)"""
        await self.redis_repo.clear_all()
        await self.sync_waiting_tasks()
