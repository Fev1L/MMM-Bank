import { Routes } from '@angular/router';
import { Auth } from './features/auth/auth';
import { Dashboard } from './dashboard/dashboard';
import { authGuard } from './core/guards/auth-guard';
import {Home} from './features/home/home';

export const routes: Routes = [
  { path: '', component: Home , canActivate: [authGuard]},
  {
    path: 'auth',
    component: Auth,
    canActivate: [authGuard]
  },
  {
    path: 'dashboard',
    component: Dashboard,
  },
  { path: '**', redirectTo: '' }
];
