import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SpacesSection } from './spaces-section';

describe('SpacesSection', () => {
  let component: SpacesSection;
  let fixture: ComponentFixture<SpacesSection>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SpacesSection]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SpacesSection);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
