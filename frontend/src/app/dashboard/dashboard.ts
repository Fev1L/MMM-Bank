import {ChangeDetectorRef, Component, OnInit} from '@angular/core';
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
  availableCurrencies = ['USD', 'EUR', 'UAH', 'GBP', 'PLN'];

  user: any = null;
  accounts: any[] = [];
  totalBalance: number = 0;
  recentTransactions: any[] = [];

  constructor(
    public authService: AuthService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    this.loadUserData();
  }

  onLogout() {
    if (confirm('Are you sure you want to log out?')) {
      this.authService.logout();
    }
  }

  openNewAccount(currency: string) {
    this.authService.createAccount(currency).subscribe({
      next: (res) => {
        this.accounts.push(res.account);
        alert(`Your account in ${currency} has been successfully opened!`);
      },
      error: (err) => {
        alert(err.error.message || 'Error opening an account');
      }
    });
  }

  loadUserData() {
    this.authService.getProfile().subscribe({
      next: (data) => {
        this.user = data.user;
        this.accounts = data.accounts;
        this.totalBalance = data.totalBalance;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error loading profile', err);
      }
    });
  }
}
