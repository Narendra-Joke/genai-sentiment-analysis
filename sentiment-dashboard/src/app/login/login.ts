import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './login.html',
  styleUrl: './login.css'
})
export class LoginComponent implements OnInit {

  email = '';
  password = '';
  showPassword = false;

  errorMessage = '';

  formError = '';
  googleError = '';

  constructor(
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {

    if (typeof window === 'undefined') return;

    const token = localStorage.getItem('token');

    if (token) {
      this.router.navigateByUrl('/');
      return;
    }

    this.route.queryParams.subscribe(params => {

      this.formError = '';
      this.googleError = '';

      if (params['error'] === 'invalid_credentials') {
        this.formError = 'Invalid credentials';
      }

      if (params['error'] === 'user_not_found') {
        this.googleError = 'User not allowed to login';
      }

    });
  }

  togglePassword() {
    this.showPassword = !this.showPassword;
  }

  login() {

  if (!this.email || !this.password) {
    this.formError  = "Email and password are required";
    return;
  }

  const form = document.createElement('form');
  form.method = 'POST';
  form.action = 'http://localhost:8082/auth/login';

  const emailInput = document.createElement('input');
  emailInput.type = 'hidden';
  emailInput.name = 'username';
  emailInput.value = this.email;

  const passwordInput = document.createElement('input');
  passwordInput.type = 'hidden';
  passwordInput.name = 'password';
  passwordInput.value = this.password;

  form.appendChild(emailInput);
  form.appendChild(passwordInput);

  document.body.appendChild(form);
  form.submit();
}

  googleLogin() {
    window.location.href =
      "http://localhost:8082/oauth2/authorization/google";
  }
}