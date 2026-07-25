import { Component } from '@angular/core';

import { ProjectsSection } from './components/projects-section/projects-section';
import { SpacesSection } from './components/spaces-section/spaces-section';
import { RecentProjectsSection } from './components/recent-projects-section/recent-projects-section';
import { SidebarFooter } from './components/sidebar-footer/sidebar-footer';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [ProjectsSection, SpacesSection, RecentProjectsSection, SidebarFooter],
  templateUrl: './sidebar.html',
  styleUrl: './sidebar.css',
})
export class Sidebar {

}
