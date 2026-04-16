import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Helpage } from './helpage';

describe('Helpage', () => {
  let component: Helpage;
  let fixture: ComponentFixture<Helpage>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Helpage],
    }).compileComponents();

    fixture = TestBed.createComponent(Helpage);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
