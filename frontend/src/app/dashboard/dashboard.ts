import {ChangeDetectorRef, Component, OnInit} from '@angular/core';
import { AuthService } from '../core/services/auth';
import {CommonModule} from '@angular/common';
import {AlertService} from '../core/services/alert';
import {Router} from '@angular/router';
import {Observable} from 'rxjs';
import {FormsModule} from '@angular/forms';

interface GroupedTransactions {
  date: string;
  items: any[];
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  templateUrl: './dashboard.html',
  styleUrls: ['./dashboard.scss'],
  imports: [CommonModule, FormsModule]
})

export class Dashboard implements OnInit {
  activeTab = 'accounts';

  availableCurrencies: any[] = [];
  user: any = null;
  accounts: any[] = [];
  totalBalance: number = 0;
  rates: { [key: string]: number } = {};
  viewCurrency: string = 'USD';
  groupedTransactions: GroupedTransactions[] = [];
  selectedAccount: any = null;

  isModalOpen: boolean = false;
  showLogoutModal: boolean = false;
  isAccountModalOpen: boolean = false;
  isDeleteAccountModalOpen: boolean = false;
  activeModal: 'send' | 'request' | 'gift' | 'exchange' | null = null;

  transferData = {
    user: '',
    amount: 0,
    currency: '',
    message: ''
  };
  exchangeData = {
    amount: 0,
    from_currency: '',
    to_currency: ''
  };

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
        this.groupedTransactions = this.groupTransactions(data);
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.alertService.error('Unable to load transaction history');
      }
    });
  }

  groupTransactions(transactions: any[]): GroupedTransactions[] {
    const groups = transactions.reduce((acc, transaction) => {
      const date = new Date(transaction.date).toLocaleDateString('en-GB', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
      });

      if (!acc[date]) {
        acc[date] = [];
      }
      acc[date].push(transaction);
      return acc;
    }, {} as { [key: string]: any[] });

    return Object.keys(groups).map(date => ({
      date: this.formatDateLabel(date),
      items: groups[date]
    }));
  }

  formatDateLabel(dateStr: string): string {
    const today = new Date().toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' });
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    const yesterdayStr = yesterday.toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' });

    if (dateStr === today) return 'Today';
    if (dateStr === yesterdayStr) return 'Yesterday';
    return dateStr;
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
        this.cdr.detectChanges();
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

  openActionModal(type: 'send' | 'request' | 'gift' | 'exchange') {
    this.activeModal = type;

    if (type === 'exchange' && this.accounts.length >= 2) {
      if (this.selectedAccount) {
        this.exchangeData.from_currency = this.selectedAccount.currency_code || this.selectedAccount.code;
        const otherAcc = this.accounts.find(a => (a.currency_code || a.code) !== this.exchangeData.from_currency);
        if (otherAcc) this.exchangeData.to_currency = otherAcc.currency_code || otherAcc.code;
      } else {
        this.exchangeData.from_currency = this.accounts[0].currency_code || this.accounts[0].code;
        this.exchangeData.to_currency = this.accounts[1].currency_code || this.accounts[1].code;
      }
    }

    if(this.selectedAccount) {
      this.transferData.currency = this.selectedAccount.currency_code || this.selectedAccount.code;
    }else if (this.accounts.length > 0) {
      this.transferData.currency = this.accounts[0].currency_code || this.accounts[0].code;
    }
  }

  get estimatedExchangeAmount(): number {
    if (!this.exchangeData.amount || !this.exchangeData.from_currency || !this.exchangeData.to_currency) return 0;

    const rateFrom = this.rates[this.exchangeData.from_currency];
    const rateTo = this.rates[this.exchangeData.to_currency];

    if (rateFrom && rateTo) {
      return (this.exchangeData.amount / rateFrom) * rateTo;
    }
    return 0;
  }

  closeActionModal() {
    this.activeModal = null;
    this.transferData = { user: '', amount: 0, currency: '', message: '' };
  }

  handleTransfer() {
    let request: Observable<any>;

    if (this.activeModal === 'send') request = this.authService.sendMoney(this.transferData);
    else if (this.activeModal === 'request') request = this.authService.requestMoney(this.transferData);
    else if (this.activeModal === 'exchange') request = this.authService.exchangeMoney(this.exchangeData);
    else request = this.authService.sendGift(this.transferData);

    request.subscribe({
      next: (res) => {
        this.alertService.success(res.message);
        this.closeActionModal();
        this.loadUserData();
        this.loadTransactions();
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.alertService.error(err.error.message || 'An error has occurred');
      }
    });
  }

  openAccountDetails(account: any) {
    this.selectedAccount = account;
    this.isAccountModalOpen = true;
  }

  closeAccountDetails() {
    this.isAccountModalOpen = false;
    this.selectedAccount = null;
  }

  openDeleteAccountDetails() {
    this.isDeleteAccountModalOpen = true;
  }

  closeDeleteAccountDetails() {
    this.isDeleteAccountModalOpen = false;
  }

  deleteAccount(currencyCode: string) {
    if (this.selectedAccount.balance > 0) {
      this.alertService.error('You cannot delete an account that contains funds!');
      return;
    }else{
      this.authService.deleteAccount(currencyCode).subscribe({
        next: (res) => {
          this.alertService.success(res.message);
          this.closeAccountDetails();
          this.closeDeleteAccountDetails();
          this.loadUserData();
        },
        error: (err) => {
          this.alertService.error(err.error.message || 'Deletion error');
        }
      });
    }
  }

  protected readonly length = length;
}

