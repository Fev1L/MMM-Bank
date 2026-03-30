import {ChangeDetectorRef, Component, OnInit} from '@angular/core';
import { AuthService } from '../core/services/auth';
import {CommonModule} from '@angular/common';
import {AlertService} from '../core/services/alert';
import {Router} from '@angular/router';

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
  rates: { [key: string]: number } = {};
  viewCurrency: string = 'USD';
  recentTransactions: any[] = [];

  isModalOpen: boolean = false;
  showLogoutModal: boolean = false;

  constructor(
    public authService: AuthService,
    private cdr: ChangeDetectorRef,
    private router: Router,
    private alertService: AlertService
  ) {}

  ngOnInit() {
    this.loadUserData();
    this.loadTransactions();
  }

  onLogout() {
    this.showLogoutModal = true;
  }

  closeLogoutModal() {
    this.showLogoutModal = false;
  }

  confirmLogout() {
    this.showLogoutModal = false;

    this.authService.logout().subscribe({
      next: () => {
        this.alertService.success('You have successfully logged out');
        setTimeout(() => {
          this.router.navigate(['']);
        }, 1500);
      },
      error: (err) => {
        this.alertService.error('Something went wrong when I tried to log out');
      }
    });
  }

  loadUserData() {
    this.authService.getProfile().subscribe({
      next: (data) => {
        this.user = data.user;
        this.accounts = data.accounts;
        this.rates = data.rates;
        this.availableCurrencies = data.availableCurrencies;
        this.calculateTotal();;
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.alertService.error(err.error.message || 'Error loading profile');
      }
    });
  }

  loadTransactions() {
    this.authService.getTransactions().subscribe({
      next: (data) => {
        this.recentTransactions = data;
      },
      error: (err) => {
        this.alertService.error('Unable to load transaction history');
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
        this.alertService.success(`Your account in ${currencyCode} has been successfully opened!`);
      },
      error: (err) => {
        this.alertService.error(err.error.message || 'Error opening an account');
      }
    });

    this.closeAddAccountModal();
  }

  calculateTotal() {
    if (!this.accounts.length || Object.keys(this.rates).length === 0) {
      this.totalBalance = 0;
      return;
    }

    this.totalBalance = this.accounts.reduce((total, acc) => {
      const currencyKey = acc.currency_code || acc.code;
      const rate = this.rates[currencyKey];

      if (rate) {
        return total + (acc.balance / rate);
      }
      return total;
    }, 0);
  }

  getConvertedTotal(): number {
    const targetRate = this.rates[this.viewCurrency] || 1;
    return this.totalBalance * targetRate;
  }
}

