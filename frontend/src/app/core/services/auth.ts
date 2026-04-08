import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import {BehaviorSubject, tap, Observable, of} from 'rxjs';
import {environment} from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private API_URL = environment.apiUrl;

  private loggedIn = new BehaviorSubject<boolean>(this.hasToken());
  isLoggedIn$ = this.loggedIn.asObservable();

  constructor(
    private http: HttpClient,
    private router: Router
  ) {}

  private hasToken(): boolean {
    return !!localStorage.getItem('access_token');
  }

  login(credentials: any): Observable<any> {
    return this.http.post(`${this.API_URL}/api/login/`, credentials).pipe(
      tap((response: any) => {
        if (response && response.access) {
          localStorage.setItem('access_token', response.access);
          localStorage.setItem('refresh_token', response.refresh);
          this.loggedIn.next(true);
        }
      })
    );
  }

  register(userData: any): Observable<any> {
    return this.http.post(`${this.API_URL}/api/register/`, userData).pipe(
      tap((response: any) => {
        if (response && response.access) {
          localStorage.setItem('access_token', response.access);
          localStorage.setItem('refresh_token', response.refresh);
          this.loggedIn.next(true);
        }
      })
    );
  }

  logout(): Observable<any> {
    return this.http.post(`${this.API_URL}/api/logout/`, {}).pipe(
      tap(() => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        this.loggedIn.next(false);
        this.router.navigate(['']);
      })
    );
  }

  sendCode(email: string) {
    return this.http.post(`${this.API_URL}/api/send-code/`, { email });
  }

  verifyCode(email: string, code: string) {
    return this.http.post(`${this.API_URL}/api/verify-code/`, { email, code });
  }

  checkUsername(username: string) {
    return this.http.post(`${this.API_URL}/api/check-username/`, { username });
  }

  createAccount(currency: string): Observable<any> {
    return this.http.post(`${this.API_URL}/api/accounts/create/`, { currency });
  }

  getUserData(): Observable<any> {
    return this.http.get(`${this.API_URL}/api/dashboard/`);
  }

  getTransactions(): Observable<any[]> {
    return this.http.get<any[]>(`${this.API_URL}/api/transactions/`);
  }

  sendMoney(data: any): Observable<any> {
    return this.http.post(`${this.API_URL}/api/send-money/`, data);
  }

  requestMoney(data: any): Observable<any> {
    return this.http.post(`${this.API_URL}/api/request-money/`, data);
  }

  sendGift(data: any): Observable<any> {
    return this.http.post(`${this.API_URL}/api/send-gift/`, data);
  }

  claimGift(requestId: string): Observable<any> {
    return this.http.post(`${this.API_URL}/api/claim-gift/${requestId}/`, {});
  }

  payRequest(requestId: string): Observable<any> {
    return this.http.post(`${this.API_URL}/api/api-confirm-payment-request/${requestId}/`, {});
  }

  exchangeMoney(data: any): Observable<any> {
    return this.http.post(`${this.API_URL}/api/exchange/`, data);
  }

  deleteAccount(currencyCode: string): Observable<any> {
    return this.http.delete(`${this.API_URL}/api/accounts/${currencyCode}/delete/`);
  }

  getCredits(): Observable<any> {
    return this.http.get(`${this.API_URL}/api/credits/`);
  }

  applyForCredit(data: any): Observable<any> {
    return this.http.post(`${this.API_URL}/api/credits/`, data);
  }

  repayCredit(data: any): Observable<any> {
    return this.http.post(`${this.API_URL}/api/repay-credit/`, data);
  }

  getPiggyBanks() : Observable<any>  {
    return this.http.get(`${this.API_URL}/api/piggy-bank/`);
  }

  closePiggyBank(data: any , piggy_id: string) : Observable<any>  {
    return this.http.post(`${this.API_URL}/api/piggy-bank/${piggy_id}/close/`, data);
  }

  managePiggyBank(data: any) : Observable<any> {
    return this.http.post(`${this.API_URL}/api/piggy-bank/`, data);
  }

  getDeposits() : Observable<any> {
    return this.http.get(`${this.API_URL}/api/deposits/`);
  }

  openDeposit(data: any) : Observable<any> {
    return this.http.post(`${this.API_URL}/api/deposits/open/`, data);
  }
}
