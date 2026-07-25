import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, map, tap } from 'rxjs';

import { ChatMessage } from '../models/message.model';

@Injectable({ providedIn: 'root' })
export class ChatService {
  private sessionId?: string;

  constructor(private readonly http: HttpClient) {}

  sendMessage(message: string): Observable<ChatMessage> {
    const payload: AgentChatRequest = { message };
    if (this.sessionId) {
      payload.session_id = this.sessionId;
    }

    return this.http.post<AgentChatResponse>('/api/agent/chat', payload).pipe(
      tap(({ session_id }) => (this.sessionId = session_id)),
      map<AgentChatResponse, ChatMessage>(({ response }) => ({
        id: crypto.randomUUID(),
        sender: 'assistant',
        type: 'text',
        content: response,
        createdAt: new Date(),
      })),
    );
  }

  startNewConversation(): void {
    this.sessionId = undefined;
  }
}

interface AgentChatRequest {
  message: string;
  session_id?: string;
}

interface AgentChatResponse {
  session_id: string;
  response: string;
}
