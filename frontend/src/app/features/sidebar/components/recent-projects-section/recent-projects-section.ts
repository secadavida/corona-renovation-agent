import { Component } from '@angular/core';
import { RecentProject } from '../../models/recent-project.model';

@Component({
  selector: 'app-recent-projects-section',
  standalone: true,
  imports: [],
  templateUrl: './recent-projects-section.html',
  styleUrl: './recent-projects-section.css'
})
export class RecentProjectsSection {

  protected readonly projects:RecentProject[]=[

    {
      id:1,
      name:'Casa de Playa',
      image:'images/bathroom.png',
      lastOpened:'2 days ago'
    },

    {
      id:2,
      name:'Oficina Central',
      image:'images/living-room.png',
      lastOpened:'1 week ago'
    },

    {
      id:3,
      name:'Departamento',
      image:'images/kitchen.png',
      lastOpened:'2 weeks ago'
    }

  ];

}