import { Component, OnInit } from '@angular/core';
import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  // Default number of columns for the grid list
  cols: number = 3;

  // Sample data for dashboard cards
  cards = [
    { title: 'Card 1', content: 'Content 1' },
    { title: 'Card 2', content: 'Content 2' },
    { title: 'Card 3', content: 'Content 3' },
    // ... add more cards as needed
  ];

  constructor(private breakpointObserver: BreakpointObserver) {}

  ngOnInit() {
    // Adjust the number of columns based on the screen size
    this.breakpointObserver.observe([
      Breakpoints.Handset,
      Breakpoints.Tablet,
      Breakpoints.Web
    ]).subscribe(result => {
      if (result.matches) {
        if (result.breakpoints[Breakpoints.Handset]) {
          this.cols = 1; // 1 column for handset
        } else if (result.breakpoints[Breakpoints.Tablet]) {
          this.cols = 2; // 2 columns for tablets
        } else {
          this.cols = 3; // 3 columns for web
        }
      }
    });
  }
}
