import { MarkdownComponent, injectContent } from '@analogjs/content';
import { AsyncPipe, NgIf } from '@angular/common';
import { Component } from '@angular/core'; 

import { BlogPost } from '../../models/post';
import { RouterOutlet } from '@angular/router';

@Component({
  standalone: true,
  imports: [RouterOutlet, MarkdownComponent, NgIf, AsyncPipe],
  template: `
    <div *ngIf="post$ | async as post">
      <h2>{{ post.attributes.title }}</h2>

      <analog-markdown [content]="post.content" />
    </div>
  `,
})
export default class BlogPostPage {
  

  post$ = injectContent<BlogPost>({
    param: 'slug',
    subdirectory: 'blog',
  });
} 