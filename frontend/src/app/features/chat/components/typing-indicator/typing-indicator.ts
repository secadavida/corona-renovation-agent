import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-typing-indicator',
  imports: [],
  templateUrl: './typing-indicator.html',
  styleUrl: './typing-indicator.css',
})
export class TypingIndicator {
  @Input() visible = false;
}
