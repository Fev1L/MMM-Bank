import 'zone.js';
import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { App } from './app/app';
import {getApps, initializeApp} from '@angular/fire/app';
import {environment} from './environments/environment';

if (!getApps().length) {
  initializeApp(environment.firebase);
  console.log('🚀 Firebase manual init in main.ts');
}

bootstrapApplication(App, appConfig)
  .catch((err) => console.error(err));
