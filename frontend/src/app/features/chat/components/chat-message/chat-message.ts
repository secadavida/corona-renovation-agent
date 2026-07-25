import { DatePipe } from '@angular/common';
import { Component, Input, OnChanges } from '@angular/core';

import { ChatMessage as ChatMessageModel } from '../../models/message.model';

@Component({
  selector: 'app-chat-message',
  imports: [DatePipe],
  templateUrl: './chat-message.html',
  styleUrl: './chat-message.css',
})
export class ChatMessage implements OnChanges {
  @Input({ required: true }) message!: ChatMessageModel;

  formattedContent = '';

  ngOnChanges(): void {
    this.formattedContent = this.message.sender === 'assistant' ? this.renderMarkdown(this.message.content) : '';
  }

  private renderMarkdown(content: string): string {
    const lines = content.replace(/\r\n/g, '\n').split('\n');
    const html: string[] = [];
    let paragraph: string[] = [];
    let listType: 'ul' | 'ol' | null = null;

    const closeList = (): void => {
      if (listType) html.push(`</${listType}>`);
      listType = null;
    };
    const closeParagraph = (): void => {
      if (paragraph.length) html.push(`<p>${paragraph.map((line) => this.renderInline(line)).join('<br>')}</p>`);
      paragraph = [];
    };

    for (const line of lines) {
      const heading = line.match(/^(#{1,3})\s+(.+)$/);
      const unorderedItem = line.match(/^\s*[-*+]\s+(.+)$/);
      const orderedItem = line.match(/^\s*\d+[.)]\s+(.+)$/);

      if (/^\s*(-{3,}|\*{3,}|_{3,})\s*$/.test(line)) {
        closeParagraph();
        closeList();
        html.push('<hr>');
      } else if (heading) {
        closeParagraph();
        closeList();
        const level = Math.min(heading[1].length + 2, 5);
        html.push(`<h${level}>${this.renderInline(heading[2])}</h${level}>`);
      } else if (unorderedItem || orderedItem) {
        closeParagraph();
        const nextListType = unorderedItem ? 'ul' : 'ol';
        if (listType && listType !== nextListType) closeList();
        if (!listType) {
          listType = nextListType;
          html.push(`<${listType}>`);
        }
        html.push(`<li>${this.renderInline((unorderedItem ?? orderedItem)![1])}</li>`);
      } else if (!line.trim()) {
        closeParagraph();
        closeList();
      } else {
        closeList();
        paragraph.push(line);
      }
    }

    closeParagraph();
    closeList();
    return html.join('');
  }

  private renderInline(value: string): string {
    // Escape before formatting so model output is always treated as text, never executable HTML.
    let rendered = value
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');

    rendered = rendered.replace(/`([^`]+)`/g, '<code>$1</code>');
    rendered = rendered.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    rendered = rendered.replace(/(?<!\*)\*([^*]+)\*(?!\*)/g, '<em>$1</em>');
    rendered = rendered.replace(/\$([^$]+)\$/g, '<span class="chat-message__math">$1</span>');
    rendered = rendered.replace(/\^([0-9]+)/g, '<sup>$1</sup>');
    return rendered;
  }
}
