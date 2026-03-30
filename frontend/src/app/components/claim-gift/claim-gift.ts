import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from '../../core/services/auth';
import { AlertService } from '../../core/services/alert';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-claim-gift',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './claim-gift.html',
  styleUrl: './claim-gift.scss',
})
export class ClaimGift implements OnInit {
  loading = true;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private authService: AuthService,
    private alertService: AlertService
  ) {}

  ngOnInit() {
    const giftId = this.route.snapshot.paramMap.get('id');

    if (giftId) {
      this.authService.claimGift(giftId).subscribe({
        next: (res: any) => {
          this.loading = false;
          this.alertService.success(res.message || 'The gift has been successfully received!');
          this.router.navigate(['/dashboard']);
        },
        error: (err) => {
          this.loading = false;
          this.alertService.error(err.error.message || 'An error occurred when receiving the gift');
          this.router.navigate(['/dashboard']);
        }
      });
    } else {
      this.alertService.error('Invalid link');
      this.router.navigate(['/dashboard']);
    }
  }
}
