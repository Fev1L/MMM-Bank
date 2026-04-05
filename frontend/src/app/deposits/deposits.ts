import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../core/services/auth';
import { AlertService } from '../core/services/alert';
import {Router, RouterLink} from '@angular/router';

@Component({
  selector: 'app-deposits',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './deposits.html',
  styleUrl: './deposits.scss',
})
export class Deposits implements OnInit {
  activeTab: 'piggy' | 'deposits' = 'piggy';

  user: any = null;
  accounts: any[] = [];
  piggies: any[] = [];
  activeDeposits: any[] = [];
  depositHistory: any[] = [];
  rates: { [key: string]: number } = {};
  viewCurrency: string = 'USD';
  totalBalance: number = 0;

  showLogoutModal: boolean = false;
  showPiggyModal = false;
  showDepositModal = false;
  showManagePiggyModal = false;

  piggyAction: 'add' | 'withdraw' = 'add';
  selectedPiggy: any = null;

  newPiggyData = { name: '', goal: null, currency: '' };
  managePiggyData = { piggy_id: null, amount: null, currency: '', action: '' };
  newDepositData = { amount: null, duration: 3, currency: '' };


  constructor(
    private authService: AuthService,
    private alertService: AlertService,
    private cdr: ChangeDetectorRef,
    private router: Router,
  ) {}

  ngOnInit() {
    this.loadUserData();
    this.loadSavingsData();
  }

  loadUserData() {
    this.authService.getUserData().subscribe({
      next: (data) => {
        this.user = data.user;
        this.accounts = data.accounts;

        if (this.accounts && this.accounts.length > 0 && !this.newPiggyData.currency) {
          this.newPiggyData.currency = this.accounts[0].code;
        }
        if (this.accounts && this.accounts.length > 0 && !this.managePiggyData.currency) {
          this.managePiggyData.currency = this.accounts[0].code;
        }
        if (this.accounts && this.accounts.length > 0 && !this.newDepositData.currency) {
          this.newDepositData.currency = this.accounts[0].code;
        }

        this.rates = data.rates;
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.alertService.error(err.error.message || 'Error loading profile');
      }
    });
  }

  getConvertedTotal(): number {
    const targetRate = this.rates[this.viewCurrency] || 1;
    return this.totalBalance * targetRate;
  }

  loadSavingsData() {
    this.authService.getPiggyBanks().subscribe(res => {
      this.piggies = res.piggies;
      this.cdr.detectChanges();
    });

    this.authService.getDeposits().subscribe(res => {
      this.activeDeposits = res.active_deposits;
      this.depositHistory = res.history;
      this.cdr.detectChanges();
    });
  }

  createPiggy() {
    const payload = { action: 'create', ...this.newPiggyData };
    this.authService.managePiggyBank(payload).subscribe({
      next: (res) => {
        this.alertService.success(res.message);
        this.showPiggyModal = false;
        this.newPiggyData = { name: '', goal: null , currency: '' };
        this.loadSavingsData();
      },
      error: (err) => this.alertService.error(err.error.message)
    });
  }

  openManagePiggy(piggy: any, action: 'add' | 'withdraw') {
    this.selectedPiggy = piggy;
    this.piggyAction = action;
    this.managePiggyData.piggy_id = piggy.id;
    this.managePiggyData.amount = null;
    this.showManagePiggyModal = true;
  }

  submitManagePiggy() {
    this.managePiggyData.action = this.piggyAction;
    this.authService.managePiggyBank(this.managePiggyData).subscribe({
      next: (res) => {
        this.alertService.success(res.message);
        this.showManagePiggyModal = false;
        this.loadSavingsData();
        this.loadUserData();
      },
      error: (err) => this.alertService.error(err.error.message)
    });
  }

  get expectedProfit() {
    const amount = this.newDepositData.amount || 0;
    const rates: any = { 3: 3, 6: 5, 12: 7, 24: 9 };
    return (amount * rates[this.newDepositData.duration]) / 100;
  }

  openDeposit() {
    this.authService.openDeposit(this.newDepositData).subscribe({
      next: (res) => {
        this.alertService.success(res.message);
        this.showDepositModal = false;
        this.newDepositData.amount = null;
        this.loadSavingsData();
        this.loadUserData();
      },
      error: (err) => this.alertService.error(err.error.message)
    });
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
}
