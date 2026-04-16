import {ApplicationConfig, provideBrowserGlobalErrorListeners, provideZoneChangeDetection} from '@angular/core';
import { provideRouter } from '@angular/router';

import { routes } from './app.routes';
import {provideHttpClient, withFetch, withInterceptors} from '@angular/common/http';
import {authInterceptor} from './core/services/auth.interceptor';

import {provideFirebaseApp, initializeApp, getApps} from '@angular/fire/app';
import { provideFirestore, getFirestore } from '@angular/fire/firestore';
import { environment } from '../environments/environment';

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),

    provideFirebaseApp(() => {
      const existingApps = getApps();
      return existingApps.length ? existingApps[0] : initializeApp(environment.firebase);
    }),
    provideFirestore(() => getFirestore()),

    provideBrowserGlobalErrorListeners(),
    provideHttpClient(
      withInterceptors([authInterceptor]),
      withFetch()
    ),
    provideRouter(routes),
  ]
};
