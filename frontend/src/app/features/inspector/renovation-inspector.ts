import { Component } from '@angular/core';

type InspectorTab = 'summary' | 'products' | 'activity';

@Component({
  selector: 'app-renovation-inspector',
  standalone: true,
  templateUrl: './renovation-inspector.html',
  styleUrl: './renovation-inspector.css',
})
export class RenovationInspector {
  activeTab: InspectorTab = 'summary';

  selectTab(tab: InspectorTab): void {
    this.activeTab = tab;
  }
}
