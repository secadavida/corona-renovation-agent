import { Component } from '@angular/core';
import { Header } from '../../shared/components/header/header';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [Header],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css',
})
export class Dashboard {

}
