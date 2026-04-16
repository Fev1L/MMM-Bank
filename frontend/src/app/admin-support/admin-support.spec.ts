import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdminSupport } from './admin-support';

describe('AdminSupport', () => {
  let component: AdminSupport;
  let fixture: ComponentFixture<AdminSupport>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AdminSupport],
    }).compileComponents();

    fixture = TestBed.createComponent(AdminSupport);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
