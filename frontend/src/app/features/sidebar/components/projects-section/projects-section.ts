import { Component } from '@angular/core';
import { Project } from '../../models/project.model';

@Component({
  selector: 'app-projects-section',
  standalone: true,
  imports: [],
  templateUrl: './projects-section.html',
  styleUrl: './projects-section.css'
})
export class ProjectsSection {

  protected readonly projects: Project[] = [
    {
      id: 1,
      name: 'Mi Apartamento',
      icon: 'ri-folder-line',
      selected: true
    }
  ];

}