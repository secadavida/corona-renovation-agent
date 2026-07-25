import { CurrencyPipe } from '@angular/common';
import { Component } from '@angular/core';

import { RenovationContextService } from './renovation-context.service';

type InspectorTab = 'summary' | 'products' | 'activity';

@Component({
  selector: 'app-renovation-inspector',
  standalone: true,
  imports: [CurrencyPipe],
  templateUrl: './renovation-inspector.html',
  styleUrl: './renovation-inspector.css',
})
export class RenovationInspector {
  activeTab: InspectorTab = 'summary';

  constructor(readonly renovationContext: RenovationContextService) {}

  selectTab(tab: InspectorTab): void {
    this.activeTab = tab;
  }
}
