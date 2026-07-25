import { Component } from '@angular/core';

import { Header } from '../../shared/components/header/header';
import { Sidebar } from '../../features/sidebar/sidebar';
import { RenovationInspector } from '../../features/inspector/renovation-inspector';
import { ChatPage } from '../../chat/pages/chat.page/chat.page';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [Header, Sidebar, ChatPage, RenovationInspector],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css',
})
export class Dashboard {

}
