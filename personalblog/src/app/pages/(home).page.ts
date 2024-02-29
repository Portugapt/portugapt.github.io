import { Component } from '@angular/core';

import { AnalogWelcomeComponent } from './analog-welcome.component';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'personalblog-home',
  standalone: true,
  imports: [AnalogWelcomeComponent, RouterLink],
  template: `
     <a [routerLink]="['/blog']">Blog</a>
     <personalblog-analog-welcome/>
  `,
})
export default class HomeComponent {
}
