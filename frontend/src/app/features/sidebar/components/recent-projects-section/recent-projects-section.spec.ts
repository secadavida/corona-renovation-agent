import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RecentProjectsSection } from './recent-projects-section';

describe('RecentProjectsSection', () => {
  let component: RecentProjectsSection;
  let fixture: ComponentFixture<RecentProjectsSection>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RecentProjectsSection]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RecentProjectsSection);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
