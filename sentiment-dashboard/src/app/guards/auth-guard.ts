import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth';

export const authGuard = () => {

  const router = inject(Router);
  const auth = inject(AuthService);

  if (auth.isLoggedIn()) {
    return true;
  }

  router.navigateByUrl('/login');
  return false;

};