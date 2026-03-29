import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

export interface AlertMessage {
  id: number;
  type: 'success' | 'error';
  text: string;
  isClosing?: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class AlertService {
  private alerts: AlertMessage[] = [];
  public alerts$ = new BehaviorSubject<AlertMessage[]>([]);
  private idCounter = 0;

  success(text: string) {
    this.addAlert(text, 'success');
  }

  error(text: string) {
    this.addAlert(text, 'error');
  }

  private addAlert(text: string, type: 'success' | 'error') {
    const id = this.idCounter++;
    const alert: AlertMessage = {id, type, text};

    this.alerts.push(alert);
    this.alerts$.next(this.alerts);

    setTimeout(() => {
      this.removeAlert(id);
    }, 5000);
  }

  removeAlert(id: number) {
    const alert = this.alerts.find(a => a.id === id);
    if (alert) {
      alert.isClosing = true;
      this.alerts$.next([...this.alerts]);

      setTimeout(() => {
        this.alerts = this.alerts.filter(a => a.id !== id);
        this.alerts$.next(this.alerts);
      }, 400);
    }
  }
}
