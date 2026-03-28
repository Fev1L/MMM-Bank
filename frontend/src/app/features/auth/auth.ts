import {Component, ElementRef, OnInit, QueryList, ViewChildren , ChangeDetectorRef} from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  ReactiveFormsModule,
  FormBuilder,
  FormGroup,
  Validators,
  AbstractControl,
  ValidationErrors,
  FormsModule
} from '@angular/forms';
import { Subject, debounceTime, distinctUntilChanged } from 'rxjs';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from '../../core/services/auth';


@Component({
  selector: 'app-auth',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, FormsModule],
  templateUrl: './auth.html',
  styleUrl: './auth.scss',
})
export class Auth implements OnInit {
  authForm: FormGroup;
  isLogin = true;

  currentStep = 1;
  showPassword = false;
  showConfirmPassword = false;

  isCodeSent = false;
  verificationCode = '';
  isLoading = false;

  usernameError: string | null = null;
  private usernameSubject = new Subject<string>();
  emailError: string | null = null;

  constructor(
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private router: Router,
    private authService: AuthService,
    private cdr : ChangeDetectorRef,
  ) {
    this.authForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],

      username: ['', [Validators.required, Validators.minLength(3)]],
      password: ['', [Validators.required, Validators.minLength(8)]],
      confirmPassword: ['', [Validators.required]],

      firstName: ['', Validators.required],
      lastName: ['', Validators.required],
      nationality: ['', Validators.required],
      city: ['', Validators.required],
      street: ['', Validators.required],
      building: ['', Validators.required]
    }, { validators: this.passwordMatchValidator });
  }

  sendEmailCode() {
    const email = this.authForm.get('email')?.value;
    if (!email || this.authForm.get('email')?.invalid) {
      alert('Please enter a valid email');
      return;
    }

    this.isLoading = true;
    this.emailError = null;

    this.authService.sendCode(email).subscribe({
      next: () => {
        this.isCodeSent = true;
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.isLoading = false;
        this.emailError = err.error?.message || 'Error sending the code';
        this.cdr.detectChanges();
      }
    });
  }

  checkCode() {
    const email = this.authForm.get('email')?.value;
    if (!email || this.verificationCode.length < 6 || this.isLoading) return;

    this.isLoading = true;

    this.authService.verifyCode(email, this.verificationCode).subscribe({
      next: (res: any) => {
        this.isLoading = false;
        this.currentStep = 2;
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.isLoading = false;
        alert(err.error?.message || 'Invalid code');
        this.verificationCode = '';
        this.cdr.detectChanges();
      }
    });
  }

  @ViewChildren('otpInput') otpInputs!: QueryList<ElementRef>;

  onOtpInput(event: any, index: number) {
    const value = event.target.value;
    const inputs = this.otpInputs.toArray();

    if (value && index < 5) {
      inputs[index + 1].nativeElement.focus();
    }

    this.collectAndVerify();
  }

  collectAndVerify() {
    const inputs = this.otpInputs.toArray();
    const fullCode = inputs.map(input => input.nativeElement.value).join('');

    if (fullCode.length === 6) {
      this.verificationCode = fullCode;
    }
  }

  ngOnInit() {
    this.route.queryParams.subscribe(params => {
      this.isLogin = params['mode'] !== 'signup';
      this.currentStep = 1;
    });

    this.usernameSubject.pipe(
      debounceTime(500),
      distinctUntilChanged()
    ).subscribe(username => {
      this.validateUsername(username);
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
    this.isCodeSent = false;
    this.usernameError = null;
    this.verificationCode = '';

    this.authForm.reset();

    this.router.navigate([], {
      queryParams: { mode: this.isLogin ? 'login' : 'signup' },
      queryParamsHandling: 'merge'
    });
  }

  nextStep() {
    if (this.currentStep < 3) {
      this.currentStep++;
    }
  }

  onUsernameChange() {
    const username = this.authForm.get('username')?.value;
    this.usernameSubject.next(username);
  }

  validateUsername(username: string) {
    if (username.length < 3) return;

    this.authService.checkUsername(username).subscribe({
      next: (res: any) => {
        if (!res.available) {
          this.usernameError = res.message;
        } else {
          this.usernameError = null;
        }
      }
    });
  }

  onSubmit() {
    if (this.isLogin) {
      this.handleLogin();
    } else {
      if (this.authForm.valid) {
        this.isLoading = true;

        this.authService.register(this.authForm.value).subscribe({
          next: (response: any) => {
            this.isLoading = false;
            console.log('Registration successful!', response);
            this.router.navigate(['/dashboard']);
          },
          error: (err: any) => {
            this.isLoading = false;
            alert('Registration Error: ' + (err.error?.message || 'Something went wrong'));
          }
        });
      } else {
        alert('Please fill in all the fields correctly.');
      }
    }
  }

  handleLogin() {
    const loginData = {
      username: this.authForm.value.username,
      password: this.authForm.value.password
    };

    this.authService.login(loginData).subscribe({
      next: () => this.router.navigate(['/dashboard']),
      error: (err) => alert('Login Error: ' + err.error.message)
    });
  }

}
