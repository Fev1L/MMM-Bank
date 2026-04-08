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
    return !!localStorage.getItem('user_session');
  }

  login(credentials: any): Observable<any> {
    return this.http.post(`${this.API_URL}/api/login/`, credentials, { withCredentials: true }).pipe(
      tap(() => {
        localStorage.setItem('user_session', 'active');
        this.loggedIn.next(true);
      })
    );
  }

  register(userData: any): Observable<any> {
    return this.http.post(`${this.API_URL}/api/register/`, userData, { withCredentials: true }).pipe(
      tap(() => {
        localStorage.setItem('user_session', 'active');
        this.loggedIn.next(true);
      })
    );
  }

  logout(): Observable<any> {
    return this.http.post(`${this.API_URL}/api/logout/`, {}, { withCredentials: true }).pipe(
      tap(() => {
        localStorage.removeItem('user_session');
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
    return this.http.post(`${this.API_URL}/api/accounts/create/`, { currency }, { withCredentials: true });
  }

  getUserData(): Observable<any> {
    return this.http.get(`${this.API_URL}/api/dashboard/`, { withCredentials: true });
  }

  getTransactions(): Observable<any[]> {
    return this.http.get<any[]>(`${this.API_URL}/api/transactions/`, { withCredentials: true });
  }

  sendMoney(data: any): Observable<any> {
    return this.http.post(`${this.API_URL}/api/send-money/`, data, { withCredentials: true });
  }

  requestMoney(data: any): Observable<any> {
    return this.http.post(`${this.API_URL}/api/request-money/`, data, { withCredentials: true });
  }

  sendGift(data: any): Observable<any> {
    return this.http.post(`${this.API_URL}/api/send-gift/`, data, { withCredentials: true });
  }

  claimGift(requestId: string): Observable<any> {
    return this.http.post(`${this.API_URL}/api/claim-gift/${requestId}/`, {}, { withCredentials: true });
  }

  payRequest(requestId: string): Observable<any> {
    return this.http.post(`${this.API_URL}/api/api-confirm-payment-request/${requestId}/`, {}, { withCredentials: true });
  }

  exchangeMoney(data: any): Observable<any> {
    return this.http.post(`${this.API_URL}/api/exchange/`, data, { withCredentials: true });
  }

  deleteAccount(currencyCode: string): Observable<any> {
    return this.http.delete(`${this.API_URL}/api/accounts/${currencyCode}/delete/`, { withCredentials: true });
  }

  getCredits(): Observable<any> {
    return this.http.get(`${this.API_URL}/api/credits/`, { withCredentials: true });
  }

  applyForCredit(data: any): Observable<any> {
    return this.http.post(`${this.API_URL}/api/credits/`, data, { withCredentials: true });
  }

  repayCredit(data: any): Observable<any> {
    return this.http.post(`${this.API_URL}/api/repay-credit/`, data, { withCredentials: true });
  }

  getPiggyBanks() : Observable<any>  {
    return this.http.get(`${this.API_URL}/api/piggy-bank/`, { withCredentials: true });
  }

  closePiggyBank(data: any , piggy_id: string) : Observable<any>  {
    return this.http.post(`${this.API_URL}/api/piggy-bank/${piggy_id}/close/`, data, { withCredentials: true });
  }

  managePiggyBank(data: any) : Observable<any> {
    return this.http.post(`${this.API_URL}/api/piggy-bank/`, data , { withCredentials: true });
  }

  getDeposits() : Observable<any> {
    return this.http.get(`${this.API_URL}/api/deposits/` , { withCredentials: true });
  }

  openDeposit(data: any) : Observable<any> {
    return this.http.post(`${this.API_URL}/api/deposits/open/`, data , { withCredentials: true });
  }
}
