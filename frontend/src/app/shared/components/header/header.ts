import { Component } from '@angular/core';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [],
  templateUrl: './header.html',
  styleUrl: './header.css',
})
export class Header {

  isProjectMenuOpen = false;

  toggleProjectMenu(): void {
    this.isProjectMenuOpen = !this.isProjectMenuOpen;
  }
  
}
