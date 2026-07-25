import { Component } from '@angular/core';
import { Space } from '../../models/space.model';

@Component({
  selector: 'app-spaces-section',
  standalone: true,
  imports: [],
  templateUrl: './spaces-section.html',
  styleUrl: './spaces-section.css'
})
export class SpacesSection {

  protected readonly spaces: Space[] = [
    {
      id:1,
      name:'Bathroom',
      icon: "ri-surgical-mask-line",
      selected:true
    },
    {
      id:2,
      name:'Kitchen',
      icon:'ri-restaurant-line',
      selected:false
    },
    {
      id:3,
      name:'Living Room',
      icon:'ri-sofa-line',
      selected:false
    },
    {
      id:4,
      name:'Bedroom',
      icon:'ri-hotel-bed-line',
      selected:false
    }
  ];

}