import { Component, OnInit } from '@angular/core';
import {Router} from '@angular/router';


@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {

  private opened = true;
  private slide = 'push';
  private active = 0;
  constructor(private route: Router) {
    this.route.events.subscribe((change) => this.checkUrlActive(), (err) => console.log(err));
  }

  private _toggleSidebar() {
    this.opened = !this.opened;
    localStorage.setItem('farmdrones_sidebar', this.opened ? 'true' : 'false');
  }

  private checkUrlActive() {
    const url = this.route.url;
    if (url.startsWith('/farm')) {
      this.active = 0;
    } else if (url.startsWith('/schedule')) {
      this.active = 1;
    } else if (url.startsWith('/map')) {
      this.active = 2;
    } else if (url.startsWith('/analytics')) {
      this.active = 3;
    } else if (url.startsWith('/timeline')) {
      this.active = 4;
    }  
    this.opened = !(localStorage.getItem('farmdrones_sidebar') === 'false');

  }

  ngOnInit(): void {
    this.checkUrlActive();
  }


}
