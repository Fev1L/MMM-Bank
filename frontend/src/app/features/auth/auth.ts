import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';

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

  constructor(
    private fb: FormBuilder,
    private route: ActivatedRoute
  ) {
    this.authForm = this.fb.group({
      username: ['', [Validators.required, Validators.minLength(3)]],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]],
      name: [''],
      surname: ['']
    });
  }

  ngOnInit() {
    this.route.queryParams.subscribe(params => {
      if (params['mode'] === 'signup') {
        this.isLogin = false;
      } else {
        this.isLogin = true;
      }
    });
  }

  toggleMode() {
    this.isLogin = !this.isLogin;
    this.authForm.reset();
  }

  onSubmit() {
    if (this.authForm.valid) {
      console.log('Дані форми:', this.authForm.value);
    }
  }
}
