import { Routes } from '@angular/router';
import { Home } from './features/home/home';
import { Auth } from './features/auth/auth';
import { Dashboard } from './dashboard/dashboard';

export const routes: Routes = [
  { path: '', component: Home},
  { path: 'auth', component: Auth },
  { path: 'dashboard', component: Dashboard }
];
