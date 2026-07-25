import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SidebarFooter } from './sidebar-footer';

describe('SidebarFooter', () => {
  let component: SidebarFooter;
  let fixture: ComponentFixture<SidebarFooter>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SidebarFooter]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SidebarFooter);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
