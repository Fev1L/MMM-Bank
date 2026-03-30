import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PayRequest } from './pay-request';

describe('PayRequest', () => {
  let component: PayRequest;
  let fixture: ComponentFixture<PayRequest>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PayRequest],
    }).compileComponents();

    fixture = TestBed.createComponent(PayRequest);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
