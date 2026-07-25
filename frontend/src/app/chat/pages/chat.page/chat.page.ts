import { Component } from '@angular/core';

import { ChatInput } from '../../../features/chat/components/chat-input/chat-input';
import { ChatWindow } from '../../../features/chat/components/chat-window/chat-window';
import { QuickActions } from '../../../features/chat/components/quick-actions/quick-actions';
import { UploadProgress } from '../../../features/chat/components/upload-progress/upload-progress';
import { ChatMessage } from '../../../features/chat/models/message.model';
import { QuickAction } from '../../../features/chat/models/quick-action.model';
import { ChatService } from '../../../features/chat/services/chat.service';

@Component({
  selector: 'app-chat-page',
  imports: [ChatInput, ChatWindow, QuickActions, UploadProgress],
  templateUrl: './chat.page.html',
  styleUrl: './chat.page.css',
})
export class ChatPage {
  messages: ChatMessage[] = [
    { id: 'welcome', sender: 'assistant', type: 'text', content: 'Hola, soy Corona AI. ¿Qué te gustaría renovar?', createdAt: new Date() },
  ];
  isTyping = false;
  uploadProgress: number | null = null;
  readonly quickActions: QuickAction[] = [
    { id: 'style', label: 'Mejor estilo', value: 'Quiero mejorar el estilo.' },
    { id: 'storage', label: 'Más almacenamiento', value: 'Necesito más almacenamiento.' },
    { id: 'functionality', label: 'Mejor funcionalidad', value: 'Quiero mejorar la funcionalidad.' },
    { id: 'budget', label: 'Menor presupuesto', value: 'Busco una opción de menor presupuesto.' },
  ];

  constructor(private readonly chatService: ChatService) {}

  sendMessage(text: string): void {
    this.messages = [...this.messages, this.createUserMessage(text)];
    this.isTyping = true;
    this.chatService.sendMessage(text).subscribe({
      next: (response) => (this.messages = [...this.messages, response]),
      complete: () => (this.isTyping = false),
      error: () => (this.isTyping = false),
    });
  }

  selectQuickAction(action: QuickAction): void { this.sendMessage(action.value); }

  handleImageSelected(file: File): void {
    // TODO(backend): call ChatService.sendImage(file). The local URL is only a preview; no image is uploaded yet.
    this.uploadProgress = 100;
    this.messages = [...this.messages, { id: crypto.randomUUID(), sender: 'user', type: 'image', content: file.name, imageUrl: URL.createObjectURL(file), createdAt: new Date() }];
    window.setTimeout(() => (this.uploadProgress = null), 450);
  }

  private createUserMessage(content: string): ChatMessage {
    return { id: crypto.randomUUID(), sender: 'user', type: 'text', content, createdAt: new Date() };
  }
}
