// dashboardApp.js
import { apiService } from './apiService.js';
import { DashboardController } from './dashboardController.js';
import { DashboardView } from './dashboardView.js';
import { ModalManager } from './modalManager.js';

export default class DashboardApp {
  constructor() {
    this.initialize();
  }

  async initialize() {
    try {
      // 인증 상태 확인
      const isAuthenticated = await apiService.checkAuth();
      if (!isAuthenticated) {
        window.location.href = '/login.html';
        return;
      }

      // 컴포넌트 초기화
      await this.initializeComponents();

      // 이벤트 리스너 설정
      this.setupEventListeners();

      // 초기 데이터 로드
      await this.loadInitialData();
    } catch (error) {
      console.error('DashboardApp 초기화 실패:', error);
      this.handleInitializationError(error);
    }
  }

  async initializeComponents() {
    // View 초기화
    this.view = new DashboardView();

    // Controller 초기화
    this.controller = new DashboardController(this.view, apiService);

    // ModalManager 초기화
    this.modalManager = new ModalManager(this.controller);
    this.view.setModalManager(this.modalManager);

    // View에 이벤트 바인딩
    this.view.bindEvents(this.controller);
  }

  setupEventListeners() {
    // 브라우저 새로고침 이벤트
    window.addEventListener('beforeunload', () => {
      // 필요한 정리 작업 수행
    });

    // 브라우저 뒤로가기/앞으로가기 이벤트
    window.addEventListener('popstate', () => {
      this.handleNavigationChange();
    });

    // 키보드 단축키 설정
    document.addEventListener('keydown', (e) => {
      this.handleKeyboardShortcuts(e);
    });

    // 윈도우 리사이즈 이벤트
    window.addEventListener('resize', () => {
      this.handleWindowResize();
    });
  }

  async loadInitialData() {
    try {
      // 컨트롤러 초기화 (대시보드 데이터 로드)
      await this.controller.initialize();

      // URL 파라미터 처리
      this.handleUrlParameters();
    } catch (error) {
      console.error('초기 데이터 로드 실패:', error);
      this.view.showToast('오류', '데이터를 불러오는데 실패했습니다.');
    }
  }

  handleUrlParameters() {
    const urlParams = new URLSearchParams(window.location.search);

    // 페이지 파라미터 처리
    const page = parseInt(urlParams.get('page')) || 1;
    this.controller.updatePage(page);

    // 필터 파라미터 처리
    const status = urlParams.get('status');
    if (status) {
      this.controller.updateFilter('status', status);
    }

    const driver = urlParams.get('driver');
    if (driver) {
      this.controller.updateFilter('driver', driver);
    }

    const search = urlParams.get('search');
    if (search) {
      this.controller.updateFilter('search', search);
      this.view.elements.searchInput.value = search;
    }
  }

  handleNavigationChange() {
    // URL 파라미터 변경 시 처리
    this.handleUrlParameters();
  }

  handleKeyboardShortcuts(e) {
    // Ctrl + F: 검색
    if (e.ctrlKey && e.key === 'f') {
      e.preventDefault();
      this.view.elements.searchInput?.focus();
    }

    // Ctrl + R: 새로고침
    if (e.ctrlKey && e.key === 'r') {
      e.preventDefault();
      this.controller.refreshData(true);
    }

    // Esc: 모달 닫기
    if (e.key === 'Escape') {
      // ModalManager에서 처리
    }
  }

  handleWindowResize() {
    // 반응형 UI 조정이 필요한 경우 처리
    this.adjustUIForScreenSize();
  }

  adjustUIForScreenSize() {
    const width = window.innerWidth;

    // 모바일 화면
    if (width < 768) {
      document.body.classList.add('mobile-view');
      document.body.classList.remove('desktop-view');
    }
    // 데스크톱 화면
    else {
      document.body.classList.add('desktop-view');
      document.body.classList.remove('mobile-view');
    }
  }

  handleInitializationError(error) {
    if (error.status === 401) {
      // 인증 오류
      window.location.href = '/login.html';
    } else {
      // 기타 오류
      this.view?.showToast('오류', '대시보드 초기화에 실패했습니다.');
    }
  }

  // 애플리케이션 정리
  cleanup() {
    // 이벤트 리스너 제거
    window.removeEventListener('beforeunload', this.handleBeforeUnload);
    window.removeEventListener('popstate', this.handleNavigationChange);
    window.removeEventListener('resize', this.handleWindowResize);

    // 리소스 정리
    this.controller?.cleanup();
    this.modalManager?.cleanup();
  }
}

// 앱 인스턴스 생성
document.addEventListener('DOMContentLoaded', () => {
  try {
    window.dashboardApp = new DashboardApp();
  } catch (error) {
    console.error('Dashboard initialization failed:', error);
    // 사용자에게 오류 알림
    alert('대시보드를 불러오는데 실패했습니다.');
  }
});
