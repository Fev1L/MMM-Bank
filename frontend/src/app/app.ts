import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import {AlertsComponent} from './components/alerts/alerts';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, AlertsComponent],
  templateUrl: './app.html',
  standalone: true,
  styleUrl: './app.scss'
})
export class App {
  protected readonly title = signal('frontend');
}
