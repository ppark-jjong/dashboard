import { apiService } from './apiService.js';
import { DashboardController } from './dashboardController.js';
import { DashboardView } from './dashboardView.js';
import { ModalManager } from './modalManager.js';

export default class DashboardApp {
  constructor() {
    this.view = new DashboardView();
    this.controller = new DashboardController(this.view, apiService);
    this.modalManager = new ModalManager(this.controller);

    this.view.bindEvents(this.controller);
    this.controller.initialize();
  }
}