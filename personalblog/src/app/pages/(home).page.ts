import { Component } from '@angular/core';

import { AnalogWelcomeComponent } from './analog-welcome.component';

@Component({
  selector: 'personalblog-home',
  standalone: true,
  imports: [AnalogWelcomeComponent],
  template: `
     <personalblog-analog-welcome/>
  `,
})
export default class HomeComponent {
}
