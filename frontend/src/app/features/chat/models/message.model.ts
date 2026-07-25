export interface ChatMessage {

  id: string;

  sender: 'user' | 'assistant';

  type: 'text' | 'image';

  content: string;

  imageUrl?: string;

  createdAt: Date;

}