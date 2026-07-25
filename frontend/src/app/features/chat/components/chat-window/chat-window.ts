import { Component, Input } from '@angular/core';

import { ChatMessage as ChatMessageModel } from '../../models/message.model';
import { ChatMessage } from '../chat-message/chat-message';
import { TypingIndicator } from '../typing-indicator/typing-indicator';

@Component({
  selector: 'app-chat-window',
  imports: [ChatMessage, TypingIndicator],
  templateUrl: './chat-window.html',
  styleUrl: './chat-window.css',
})
export class ChatWindow {
  @Input({ required: true }) messages: ChatMessageModel[] = [];
  @Input() typing = false;
}
