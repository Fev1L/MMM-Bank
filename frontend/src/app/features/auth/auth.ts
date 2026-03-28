import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators, AbstractControl, ValidationErrors } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from '../../core/services/auth';

@Component({
  selector: 'app-auth',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './auth.html',
  styleUrl: './auth.scss',
})
export class Auth implements OnInit {
  authForm: FormGroup;
  isLogin = true;

  currentStep = 1;
  showPassword = false;
  showConfirmPassword = false;

  constructor(
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private router: Router,
    private authService: AuthService
  ) {
    this.authForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],

      username: ['', [Validators.required, Validators.minLength(3)]],
      password: ['', [Validators.required, Validators.minLength(8)]],
      confirmPassword: ['', [Validators.required]],

      name: ['', Validators.required],
      surname: ['', Validators.required],
      nationality: ['', Validators.required],
      address: ['', Validators.required]
    }, { validators: this.passwordMatchValidator });
  }

  ngOnInit() {
    this.route.queryParams.subscribe(params => {
      this.isLogin = params['mode'] !== 'signup';
      this.currentStep = 1;
    });
  }

  passwordMatchValidator(control: AbstractControl): ValidationErrors | null {
    const password = control.get('password');
    const confirmPassword = control.get('confirmPassword');
    if (password && confirmPassword && password.value !== confirmPassword.value) {
      return { passwordMismatch: true };
    }
    return null;
  }

  togglePassword() { this.showPassword = !this.showPassword; }
  toggleConfirmPassword() { this.showConfirmPassword = !this.showConfirmPassword; }

  toggleMode() {
    this.isLogin = !this.isLogin;
    this.currentStep = 1;
    this.authForm.reset();
  }

  nextStep() {
    if (this.currentStep < 3) {
      this.currentStep++;
    }
  }

  prevStep() {
    if (this.currentStep > 1) {
      this.currentStep--;
    }
  }

  onSubmit() {
    if (this.isLogin) {
      const loginData = {
        username: this.authForm.value.username,
        password: this.authForm.value.password
      };

      this.authService.login(loginData).subscribe({
        next: (response: any) => {
          this.router.navigate(['/dashboard']);
        },
        error: (err: any) => alert('Login Error: ' + err.error.message)
      });

    } else {
      if (this.currentStep < 3) {
        this.nextStep();
      } else if (this.authForm.valid) {
        this.authService.register(this.authForm.value).subscribe({
          next: (response: any) => {
            console.log('User registered with full info!', response);
            this.router.navigate(['/dashboard']);
          },
          error: (err: any) => alert('Registration Error: ' + (err.error?.message || 'Check your data'))
        });
      }
    }
  }
}
