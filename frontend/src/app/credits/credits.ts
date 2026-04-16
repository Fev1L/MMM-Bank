import {ChangeDetectorRef, Component, OnInit} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import {Router, RouterLink} from '@angular/router';
import { AuthService } from '../core/services/auth';
import { AlertService } from '../core/services/alert';
import {forkJoin} from 'rxjs';

@Component({
  selector: 'app-credits',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './credits.html',
  styleUrls: ['./credits.scss']
})
export class Credits implements OnInit {
  isLoading = true;
  activeTab = 'loans';
  totalBalance: number = 0;
  viewCurrency: string = 'USD';

  user: any;
  accounts: any[] = [];
  credits: any[] = [];
  rates: { [key: string]: number } = {};
  selectedCredit: any = null;

  showLogoutModal: boolean = false;
  showLoanModal: boolean = false;
  showCreditDetail: boolean = false;
  activeCreditAction: 'pay_extra' | 'details' | 'close' | null = null;

  repaymentData = {
    currency: '',
    amount: null as number | null
  };

  loanData = {
    amount: null,
    loan_target: '',
    currency: '',
    id: '',
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

  get activeCredits(): any[] {
    return this.credits.filter(c => c.is_active);
  }

  get closedCredits(): any[] {
    return this.credits.filter(c => !c.is_active);
  }

  loadInitialData() {
    this.isLoading = true;

    forkJoin({
      userData: this.authService.getUserData(),
      creditDate: this.authService.getCredits()
    }).subscribe(res => {
      this.user = res.userData.user;
      this.accounts = res.userData.accounts;
      this.rates = res.userData.rates;

      if (this.accounts && this.accounts.length > 0 && !this.loanData.currency) {
        this.loanData.currency = this.accounts[0].code;
      }

      this.credits = res.creditDate.credits

      this.calculateTotal();
      this.isLoading = false;
      this.cdr.detectChanges();
    });
  }

  calculateTotal() {
    if (!this.activeCredits.length || Object.keys(this.rates).length === 0) {
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
        this.closeLoanModal()
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

  openCreditDetails(credit: any) {
    this.selectedCredit = credit;
    this.showCreditDetail = true;
  }

  closeCreditDetails() {
    this.showCreditDetail = false;
    this.selectedCredit = null;
  }

  openCreditAction(action: 'pay_extra' | 'details' | 'close') {
    this.activeCreditAction = action;

    if (this.accounts && this.accounts.length > 0) {
      this.repaymentData.currency = this.accounts[0].code;
    }

    if (action === 'close') {
      this.repaymentData.currency = this.selectedCredit.currency;
      this.repaymentData.amount = this.selectedCredit.amount;
    } else {
      this.repaymentData.amount = null;
    }
  }

  closeCreditAction() {
    this.activeCreditAction = null;
  }

  processRepayment() {
    if (!this.repaymentData.amount || this.repaymentData.amount <= 0) {
      this.alertService.error('Please enter a valid amount');
      return;
    }

    if (this.repaymentData.amount > this.selectedCredit.amount) {
      this.alertService.error('You cannot pay more than your total debt for this loan!');
      return;
    }

    const payload = {
      credit_currency: this.selectedCredit.currency,
      account_currency: this.repaymentData.currency,
      amount: this.repaymentData.amount,
      id: this.selectedCredit.id,
    };

    this.authService.repayCredit(payload).subscribe({
      next: (res) => {
        this.alertService.success(res.message);
        this.closeCreditAction();
        this.closeCreditDetails();
        this.loadInitialData();
      },
      error: (err) => this.alertService.error(err.error.message)
    });
  }
}
