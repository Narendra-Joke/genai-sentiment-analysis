import { Routes } from '@angular/router';

import { authGuard } from './guards/auth-guard';

export const routes: Routes = [

  {
    path: '',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./layout/layout/layout').then(m => m.LayoutComponent),
    children: [
      {
        path: '',
        loadComponent: () =>
          import('./pages/dashboard/dashboard').then(m => m.DashboardComponent)
      }
    ]
  },

  {
    path: 'login',
    loadComponent: () =>
      import('./login/login').then(m => m.LoginComponent)
  },

  {
    path: 'oauth-success',
    loadComponent: () =>
      import('./oauth-success/oauth-success').then(m => m.OauthSuccessComponent)
  },

  {
    path: '**',
    redirectTo: ''
  }

];