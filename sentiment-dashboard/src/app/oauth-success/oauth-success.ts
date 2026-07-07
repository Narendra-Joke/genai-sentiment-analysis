import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from '../services/auth';

@Component({
  selector: 'app-oauth-success',
  standalone: true,
  template: `<p>Signing in...</p>`
})
export class OauthSuccessComponent implements OnInit {

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private auth: AuthService
  ) {}

  ngOnInit(): void {

    const token = this.route.snapshot.queryParamMap.get('token');

    if (token) {

      this.auth.setToken(token);

      this.router.navigateByUrl('/');

    } else {

      this.router.navigateByUrl('/login');

    }

  }

}