import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ClaimGift } from './claim-gift';

describe('ClaimGift', () => {
  let component: ClaimGift;
  let fixture: ComponentFixture<ClaimGift>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ClaimGift],
    }).compileComponents();

    fixture = TestBed.createComponent(ClaimGift);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
