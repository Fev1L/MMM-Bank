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

  availableCurrencies: any[] = [];
  user: any = null;
  accounts: any[] = [];
  totalBalance: number = 0;
  recentTransactions: any[] = [];

  isModalOpen: boolean = false;

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

  loadUserData() {
    this.authService.getProfile().subscribe({
      next: (data) => {
        this.user = data.user;
        this.accounts = data.accounts;
        this.totalBalance = data.totalBalance;
        this.availableCurrencies = data.availableCurrencies;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error loading profile', err);
      }
    });
  }

  openAddAccountModal() {
    this.isModalOpen = true;
  }

  closeAddAccountModal() {
    this.isModalOpen = false;
  }

  get filteredCurrencies() {
    const ownedCodes = this.accounts.map(acc => acc.code);

    return this.availableCurrencies.filter(curr => !ownedCodes.includes(curr.code));
  }

  createNewAccount(currencyCode: string) {
    this.authService.createAccount(currencyCode).subscribe({
      next: (res) => {
        this.closeAddAccountModal();
        this.loadUserData();
        alert(`Your account in ${currencyCode} has been successfully opened!`);
      },
      error: (err) => {
        alert(err.error.message || 'Error opening an account');
      }
    });

    this.closeAddAccountModal();
  }
}

