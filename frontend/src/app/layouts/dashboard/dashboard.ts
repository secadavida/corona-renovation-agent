import { Component } from '@angular/core';

import { Header } from '../../shared/components/header/header';
import { Sidebar } from '../../features/sidebar/sidebar';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [Header, Sidebar],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css',
})
export class Dashboard {

}
