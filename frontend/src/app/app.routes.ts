import { Routes } from '@angular/router';
import { Home } from './features/home/home';
import { Auth } from './features/auth/auth';

export const routes: Routes = [
  { path: '', component: Home},
  { path: 'auth', component: Auth },
];
