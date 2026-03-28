import { Component } from '@angular/core';
import {AuthService} from '../core/services/auth';

@Component({
  selector: 'app-dashboard',
  imports: [],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss',
})
export class Dashboard {
  constructor(private authService: AuthService) {}

  onLogout() {
    if (confirm('Are you sure you want to log out?')) {
      this.authService.logout();
    }
  }
}
