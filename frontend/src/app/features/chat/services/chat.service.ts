import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { ChatMessage } from '../models/message.model';

@Injectable({ providedIn: 'root' })
export class ChatService {
  sendMessage(message: string): Observable<ChatMessage> {
    return new Observable<ChatMessage>((subscriber) => {
      // TODO(backend): replace this timeout with POST /chat using { message }.
      // The endpoint must return a ChatMessage.
      const timeoutId = window.setTimeout(() => {
        subscriber.next({
          id: crypto.randomUUID(),
          sender: 'assistant',
          type: 'text',
          content: `Entendido. Voy a ayudarte a renovar tu espacio${message ? `: “${message}”` : ''}.`,
          createdAt: new Date(),
        });
        subscriber.complete();
      }, 800);

      return () => window.clearTimeout(timeoutId);
    });
  }

  /** TODO(backend): implement POST /chat/image with multipart/form-data. */
  sendImage(_file: File): Observable<ChatMessage> {
    return new Observable<ChatMessage>((subscriber) => subscriber.complete());
  }
}
