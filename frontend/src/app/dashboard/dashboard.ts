import { Component, OnInit } from '@angular/core';
import { AuthService } from '../core/services/auth';
import {CommonModule} from '@angular/common';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  templateUrl: './dashboard.html',
  styleUrls: ['./dashboard.scss'],
  imports: [CommonModule]
})
export class Dashboard implements OnInit {
  activeTab = 'accounts';

  user = {
    firstName: 'Влад',
    lastName: 'Девелопер',
    initials: 'ВД',
    plan: 'Premium'
  };

  totalBalance = 15420.50;

  accounts = [
    { currency: 'Ukrainian Hryvnia', code: 'UAH', symbol: '₴', balance: 12500.00, flag: '🇺🇦' },
    { currency: 'US Dollar', code: 'USD', symbol: '$', balance: 45.50, flag: '🇺🇸' },
    { currency: 'Euro', code: 'EUR', symbol: '€', balance: 35.00, flag: '🇪🇺' }
  ];

  constructor(public authService: AuthService) {}

  ngOnInit() {}

  onLogout() {
    if (confirm('Are you sure you want to log out?')) {
      this.authService.logout();
    }
  }
}
