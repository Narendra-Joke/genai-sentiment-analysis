import { Injectable } from '@angular/core';
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private logoutTimer: any;

  constructor(private router: Router) {}

  setToken(token: string) {

    localStorage.setItem('token', token);

    this.startAutoLogout(token);

  }

  isLoggedIn(): boolean {

    const token = localStorage.getItem('token');

    if (!token) {
      return false;
    }

    const payload = JSON.parse(atob(token.split('.')[1]));

    const expiry = payload.exp * 1000;

    if (Date.now() > expiry) {

      this.logout();

      return false;

    }

    return true;
  }

  startAutoLogout(token: string) {

    const payload = JSON.parse(atob(token.split('.')[1]));

    const expiry = payload.exp * 1000;

    const timeout = expiry - Date.now();

    if (timeout <= 0) {

      this.logout();

      return;

    }

    this.logoutTimer = setTimeout(() => {

      this.logout();

      alert("Session expired. Please login again.");

    }, timeout);

  }

  logout() {

    localStorage.removeItem('token');

    if (this.logoutTimer) {
      clearTimeout(this.logoutTimer);
    }

    this.router.navigateByUrl('/login');

  }

}