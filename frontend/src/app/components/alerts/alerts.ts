import {ChangeDetectorRef, Component, OnInit} from '@angular/core';
import { AlertService, AlertMessage } from '../../core/services/alert';
import {CommonModule} from '@angular/common';

@Component({
  selector: 'app-alerts',
  templateUrl: './alerts.html',
  standalone: true,
  imports: [
    CommonModule
  ],
  styleUrls: ['./alerts.scss']
})
export class AlertsComponent implements OnInit {
  alerts: AlertMessage[] = [];

  constructor(
    private alertService: AlertService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.alertService.alerts$.subscribe(res => {
      this.alerts = res;
      this.cdr.detectChanges();
    });
  }

  closeAlert(id: number) {
    this.alertService.removeAlert(id);
  }
}
