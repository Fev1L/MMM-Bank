import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from '../../core/services/auth';
import { AlertService } from '../../core/services/alert';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-pay-request',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './pay-request.html',
  styleUrl: './pay-request.scss',
})
export class PayRequest implements OnInit{
  loading = true;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private authService: AuthService,
    private alertService: AlertService
  ) {}

  ngOnInit() {
    const requestId = this.route.snapshot.paramMap.get('id');

    if (requestId) {
      this.authService.payRequest(requestId).subscribe({
        next: (res: any) => {
          this.loading = false;
          this.alertService.success(res.message || 'The request has been successfully received!');
          this.router.navigate(['/dashboard']);
        },
        error: (err) => {
          this.loading = false;
          this.alertService.error(err.error.message || 'An error occurred when paying the request');
          this.router.navigate(['/dashboard']);
        }
      });
    } else {
      this.alertService.error('Invalid link');
      this.router.navigate(['/dashboard']);
    }
  }
}
