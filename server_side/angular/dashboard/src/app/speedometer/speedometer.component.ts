import { Component, Input, OnInit } from '@angular/core';

@Component({
  selector: 'app-speedometer',
  templateUrl: './speedometer.component.html',
  styleUrls: ['./speedometer.component.css']
})
export class SpeedometerComponent implements OnInit {
  @Input() speed: number = 0;

  constructor() { }

  ngOnInit(): void { }

  calculateOffset(speed: number): number {
    const maxSpeed = 100;  // Assuming 100 is the max speed for full circle
    const circumference = 2 * Math.PI * 150;
    return circumference * (1 - speed / maxSpeed);
  }
}
