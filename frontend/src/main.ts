import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { App } from './app/app';
import { initializeApp } from 'firebase/app';
import {environment} from './environments/environment';

try {
  initializeApp(environment.firebase);
  console.log('🚀 Firebase pre-initialized in main.ts');
} catch (err) {
  console.error('Firebase init error:', err);
}

bootstrapApplication(App, appConfig)
  .catch((err) => console.error(err));
