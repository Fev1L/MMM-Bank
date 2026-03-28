import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private API_URL = 'http://127.0.0.1:8000';

  constructor(private http: HttpClient) {}

  login(credentials: any) {
    return this.http.post(`${this.API_URL}/api/login/`, credentials, { withCredentials: true });
  }

  register(userData: any) {
    return this.http.post(`${this.API_URL}/api/register/`, userData, { withCredentials: true });
  }

  sendCode(email: string) {
    return this.http.post(`${this.API_URL}/api/send-code/`, { email });
  }

  verifyCode(email: string, code: string) {
    return this.http.post(`${this.API_URL}/api/verify-code/`, { email, code });
  }
}
