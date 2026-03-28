import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { BehaviorSubject, tap, Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private API_URL = 'http://127.0.0.1:8000';

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
    return this.http.post(`${this.API_URL}/api/login/`, credentials).pipe(
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

  logout() {
    localStorage.removeItem('user_session');
    this.loggedIn.next(false);
    this.router.navigate(['']);
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
}
