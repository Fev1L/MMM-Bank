import {ChangeDetectorRef, Component, OnInit} from '@angular/core';
import {NgIf} from '@angular/common';
import {Router, RouterLink} from '@angular/router';
import {forkJoin} from 'rxjs';
import {AuthService} from '../core/services/auth';
import {AlertService} from '../core/services/alert';
import {FormsModule} from '@angular/forms';

@Component({
  selector: 'app-more',
  imports: [
    NgIf,
    RouterLink,
    FormsModule
  ],
  templateUrl: './more.html',
  styleUrl: './more.scss',
})
export class More implements OnInit {
  isLoading = true;
  user: any = null;

  showLogoutModal: boolean = false;

  showProfileModal = false;
  selectedFile: File | null = null;
  imagePreview: string | null = null;

  constructor(
    public authService: AuthService,
    private cdr: ChangeDetectorRef,
    private router: Router,
    private alertService: AlertService
  ) {}

  ngOnInit() {
    this.loadUserData();
  }

  loadUserData() {
    this.isLoading = true;

    forkJoin({
      userData: this.authService.getUserData()
    }).subscribe({
      next: (res: any) => {
        this.user = res.userData.user;
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.alertService.error(err.error.message || 'Error loading profile');
      }
    });
  }

  confirmLogout() {
    this.showLogoutModal = false;

    this.authService.logout().subscribe({
      next: () => {
        this.alertService.success('You have successfully logged out');
        setTimeout(() => {
          this.router.navigate(['']);
        }, 1500);
      },
      error: (err) => {
        this.alertService.error('Something went wrong when I tried to log out');
      }
    });
  }

  onLogout() {
    this.showLogoutModal = true;
  }

  closeLogoutModal() {
    this.showLogoutModal = false;
  }

  openProfileModal() {
    this.showProfileModal = true;
    this.imagePreview = this.user?.avatarUrl || null;
  }

  closeProfileModal() {
    this.showProfileModal = false;
    this.selectedFile = null;
  }

  onFileSelected(event: any) {
    const file = event.target.files[0];
    if (file) {
      this.selectedFile = file;
      const reader = new FileReader();
      reader.onload = () => {
        this.imagePreview = reader.result as string;
      };
      reader.readAsDataURL(file);
    }
  }

  saveProfile() {
    console.log('Saving profile...', { file: this.selectedFile });
    this.closeProfileModal();
  }
}
