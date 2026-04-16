import {ApplicationConfig, provideBrowserGlobalErrorListeners, provideZoneChangeDetection} from '@angular/core';
import { provideRouter } from '@angular/router';
import { routes } from './app.routes';
import { provideHttpClient, withFetch, withInterceptors } from '@angular/common/http';
import { authInterceptor } from './core/services/auth.interceptor';

import { initializeApp as initializeFirebaseApp, getApp, getApps } from 'firebase/app';
import { provideFirebaseApp } from '@angular/fire/app';
import { getFirestore, provideFirestore } from '@angular/fire/firestore';
import { environment } from '../environments/environment';

const app = getApps().length === 0
  ? initializeFirebaseApp(environment.firebase)
  : getApp();

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),

    provideFirebaseApp(() => app),
    provideFirestore(() => getFirestore(app)),

    provideBrowserGlobalErrorListeners(),
    provideHttpClient(
      withInterceptors([authInterceptor]),
      withFetch()
    ),
    provideRouter(routes),
  ]
};
