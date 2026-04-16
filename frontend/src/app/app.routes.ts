import { Routes } from '@angular/router';
import { Auth } from './features/auth/auth';
import { Dashboard } from './dashboard/dashboard';
import { authGuard } from './core/guards/auth-guard';
import {Home} from './features/home/home';
import {ClaimGift} from './components/claim-gift/claim-gift';
import {PayRequest} from './components/pay-request/pay-request';
import {Credits} from './credits/credits';
import {Deposits} from './deposits/deposits';
import { Helpage } from "./helpage/helpage";
import {More} from './more/more';
import {AdminSupport} from './admin-support/admin-support';

export const routes: Routes = [
  { path: '', component: Home , canActivate: [authGuard]},
  {
    path: 'auth',
    component: Auth,
    canActivate: [authGuard]
  },
  { path: 'claim-gift/:id', component: ClaimGift },
  { path: 'pay-request/:id', component: PayRequest },
  { path: 'dashboard', component: Dashboard,},
  { path: 'credits', component: Credits },
  { path: 'deposits', component: Deposits },
  { path: 'helpage', component: Helpage },
  { path: 'admin/support', component: AdminSupport },
  { path: 'more', component: More },
  { path: '**', redirectTo: '' }
];
