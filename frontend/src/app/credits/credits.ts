import {ChangeDetectorRef, Component, OnInit} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import {Router, RouterLink} from '@angular/router';
import { AuthService } from '../core/services/auth';
import { AlertService } from '../core/services/alert';

@Component({
  selector: 'app-credits',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './credits.html',
  styleUrls: ['./credits.scss']
})
export class Credits implements OnInit {
  activeTab = 'loans';
  totalBalance: number = 0;
  viewCurrency: string = 'USD';

  user: any;
  accounts: any[] = [];
  credits: any[] = [];
  rates: { [key: string]: number } = {};

  showLogoutModal: boolean = false;
  showLoanModal: boolean = false;

  loanData = {
    amount: null,
    loan_target: '',
    currency: '',
  };

  constructor(
    private authService: AuthService,
    private alertService: AlertService,
    private cdr: ChangeDetectorRef,
    private router: Router
  ) {}

  ngOnInit() {
    this.loadInitialData();
  }

  loadInitialData() {
    this.authService.getUserData().subscribe(res => {
      this.user = res.user;
      this.accounts = res.accounts;
      this.rates = res.rates;

      if (this.accounts && this.accounts.length > 0 && !this.loanData.currency) {
        this.loanData.currency = this.accounts[0].code;
      }

      this.calculateTotal();
      this.cdr.detectChanges();
    });

    this.authService.getCredits().subscribe(res => {
      this.credits = res.credits;
      this.calculateTotal();
      this.cdr.detectChanges();
    });
  }

  calculateTotal() {
    if (!this.credits.length || Object.keys(this.rates).length === 0) {
      this.totalBalance = 0;
      return;
    }

    this.totalBalance = this.credits.reduce((total, acc) => {
      const currencyKey = acc.currency;
      const rate = this.rates[currencyKey];

      if (rate) {
        return total + (acc.amount / rate);
      }
      return total;
    }, 0);
  }

  getConvertedTotal(): number {
    const targetRate = this.rates[this.viewCurrency] || 1;
    return this.totalBalance * targetRate;
  }

  get selectedCurrencyCode(): string {
    if (!this.accounts || !this.loanData.currency) return 'USD';

    const selectedAcc = this.accounts.find(a => a.code == this.loanData.currency);
    return selectedAcc ? selectedAcc.code : 'USD';
  }

  get estimatedMonthlyPayment(): number {
    const amount = parseFloat(this.loanData.amount || '0');
    if (amount <= 0) return 0;
    return (amount * 1.04) / 12;
  }

  openLoanModal() {
    this.showLoanModal = true;
  }

  closeLoanModal() {
    this.showLoanModal = false;
  }

  applyLoan() {
    this.authService.applyForCredit(this.loanData).subscribe({
      next: (res) => {
        this.alertService.success(res.message);
        this.loadInitialData();
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
