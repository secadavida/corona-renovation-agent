import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-upload-progress',
  imports: [],
  templateUrl: './upload-progress.html',
  styleUrl: './upload-progress.css',
})
export class UploadProgress {
  @Input() progress = 0;
}
