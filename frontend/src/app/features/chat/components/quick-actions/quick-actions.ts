import { Component, EventEmitter, Input, Output } from '@angular/core';

import { QuickAction } from '../../models/quick-action.model';

@Component({
  selector: 'app-quick-actions',
  imports: [],
  templateUrl: './quick-actions.html',
  styleUrl: './quick-actions.css',
})
export class QuickActions {
  @Input() actions: QuickAction[] = [];
  @Output() actionSelected = new EventEmitter<QuickAction>();
}
