import { Component, EventEmitter, Output } from '@angular/core';

@Component({
  selector: 'app-chat-input',
  imports: [],
  templateUrl: './chat-input.html',
  styleUrl: './chat-input.css',
})
export class ChatInput {
  @Output() send = new EventEmitter<string>();
  @Output() imageSelected = new EventEmitter<File>();

  submit(textarea: HTMLTextAreaElement): void {
    const text = textarea.value.trim();
    if (!text) return;
    this.send.emit(text);
    textarea.value = '';
  }

  selectImage(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (file) this.imageSelected.emit(file);
    input.value = '';
  }
}
