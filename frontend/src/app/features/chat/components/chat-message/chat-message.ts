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

    for (let index = 0; index < lines.length; index += 1) {
      const line = lines[index];
      const heading = line.match(/^(#{1,3})\s+(.+)$/);
      const unorderedItem = line.match(/^\s*[-*+]\s+(.+)$/);
      const orderedItem = line.match(/^\s*\d+[.)]\s+(.+)$/);
      const tableHeader = this.parseTableRow(line);
      const tableSeparator = lines[index + 1]?.trim();

      if (tableHeader && tableSeparator && this.isTableSeparator(tableSeparator)) {
        closeParagraph();
        closeList();
        const rows: string[] = [];
        index += 2;

        while (index < lines.length) {
          const row = this.parseTableRow(lines[index]);
          if (!row) break;
          rows.push(`<tr>${row.map((cell) => `<td>${this.renderInline(cell)}</td>`).join('')}</tr>`);
          index += 1;
        }

        html.push(
          `<div class="chat-message__table-wrap"><table><thead><tr>${tableHeader
            .map((cell) => `<th scope="col">${this.renderInline(cell)}</th>`)
            .join('')}</tr></thead><tbody>${rows.join('')}</tbody></table></div>`,
        );
        index -= 1;
      } else if (/^\s*(-{3,}|\*{3,}|_{3,})\s*$/.test(line)) {
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
      .replace(/\s*\(SKU:\s*[^)]+\)/gi, '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');

    // Only absolute HTTP(S) links are accepted; image URLs come from the catalog.
    rendered = rendered.replace(
      /\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/gi,
      '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>',
    );
    rendered = rendered.replace(/`([^`]+)`/g, '<code>$1</code>');
    rendered = rendered.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    rendered = rendered.replace(/(?<!\*)\*([^*]+)\*(?!\*)/g, '<em>$1</em>');
    rendered = rendered.replace(/\$([^$]+)\$/g, '<span class="chat-message__math">$1</span>');
    rendered = rendered.replace(/\^([0-9]+)/g, '<sup>$1</sup>');
    return rendered;
  }

  private parseTableRow(line: string): string[] | null {
    const value = line.trim();
    if (!value.includes('|')) return null;

    const cells = value.replace(/^\||\|$/g, '').split('|').map((cell) => cell.trim());
    return cells.length > 1 ? cells : null;
  }

  private isTableSeparator(line: string): boolean {
    return /^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?$/.test(line);
  }
}
