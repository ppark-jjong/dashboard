// navbar.js
import { apiService } from './apiService.js';

class NavbarManager {
  constructor() {
    this.initializeNavbar();
  }

  async initializeNavbar() {
    // 현재 활성 경로 설정
    this.setActiveNavLink();

    // 사용자 정보 업데이트
    await this.updateUserInfo();
  }

  setActiveNavLink() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach((link) => {
      const href = link.getAttribute('href');
      if (
        (currentPath.includes('index.html') ||
          currentPath === '/' ||
          currentPath === '') &&
        href.includes('index.html')
      ) {
        link.classList.add('active');
      } else if (
        currentPath.includes('visualization.html') &&
        href.includes('visualization.html')
      ) {
        link.classList.add('active');
      } else {
        link.classList.remove('active');
      }
    });
  }

  async updateUserInfo() {
    try {
      // nav-links 컨테이너 찾기
      const navLinks = document.querySelector('.nav-links');
      if (!navLinks) return;

      // 기존 user-info가 있다면 제거
      const existingUserInfo = document.querySelector('.user-info');
      if (existingUserInfo) {
        existingUserInfo.remove();
      }

      const response = await apiService.checkAuth();

      // user-info 엘리먼트 생성
      const userInfo = document.createElement('div');
      userInfo.className = 'user-info';

      if (response.success) {
        userInfo.innerHTML = `
                    <span class="username">${response.data.user_id}님</span>
                    <button id="logout-btn" class="nav-logout">
                        <i class="fas fa-sign-out-alt"></i> 로그아웃
                    </button>
                `;

        navLinks.appendChild(userInfo);

        // 로그아웃 버튼 이벤트 리스너
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
          logoutBtn.addEventListener('click', this.handleLogout.bind(this));
        }
      } else {
        // 인증되지 않은 경우 로그인 페이지로 리다이렉트
        window.location.href = '/login.html';
      }
    } catch (error) {
      console.error('사용자 정보 업데이트 중 오류:', error);
      window.location.href = '/login.html';
    }
  }

  async handleLogout() {
    try {
      await apiService.logout();
      window.location.href = '/login.html';
    } catch (error) {
      console.error('로그아웃 중 오류:', error);
    }
  }
}

// 페이지 로드 시 NavbarManager 인스턴스 생성
document.addEventListener('DOMContentLoaded', () => {
  window.navbarManager = new NavbarManager();
});

export default NavbarManager;
