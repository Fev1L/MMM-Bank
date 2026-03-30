import { Routes } from '@angular/router';
import { Auth } from './features/auth/auth';
import { Dashboard } from './dashboard/dashboard';
import { authGuard } from './core/guards/auth-guard';
import {Home} from './features/home/home';
import {ClaimGift} from './components/claim-gift/claim-gift';
import {PayRequest} from './components/pay-request/pay-request';

export const routes: Routes = [
  { path: '', component: Home , canActivate: [authGuard]},
  {
    path: 'auth',
    component: Auth,
    canActivate: [authGuard]
  },
  { path: 'claim-gift/:id', component: ClaimGift },
  { path: 'pay-request/:id', component: PayRequest },
  {
    path: 'dashboard',
    component: Dashboard,
  },
  { path: '**', redirectTo: '' }
];
