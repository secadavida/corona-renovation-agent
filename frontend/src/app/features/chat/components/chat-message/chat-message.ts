import { DatePipe } from '@angular/common';
import { Component, Input } from '@angular/core';

import { ChatMessage as ChatMessageModel } from '../../models/message.model';

@Component({
  selector: 'app-chat-message',
  imports: [DatePipe],
  templateUrl: './chat-message.html',
  styleUrl: './chat-message.css',
})
export class ChatMessage {
  @Input({ required: true }) message!: ChatMessageModel;
}
