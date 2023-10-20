import { Component, OnInit, ElementRef, NgZone, OnDestroy, Input} from '@angular/core';
import { timer, Subscription } from 'rxjs';
import * as d3 from 'd3';
import { DataService } from '../data.service';

@Component({
  selector: 'app-gauge',
  templateUrl: './gauge.component.html',
  styleUrls: ['./gauge.component.css']
})
export class GaugeComponent implements OnInit, OnDestroy {
  private width: number = 260;
  private height: number = 260;
  private innerRadius: number = 75;
  private outerRadius: number = 105;
  private svg: any;
  private scale: any;
  private valueArc: any;
  private emptyArc: any;
  private transitionDuration: number = 1000;  // in milliseconds
  private updateInterval: number = 1000;  // in milliseconds
  private updateSubscription: any;
  private lastValue: number = 0;
  private gettingData: boolean = false;
  @Input() site!: string;
  @Input() category!: string;
  @Input() unit!: string;
  @Input() range_min!: number;
  @Input() range_max!: number;
  @Input() title!: string;

  constructor(private el: ElementRef, private ngZone: NgZone, private dataService: DataService) {}

  private initializeScale() {
    this.scale = d3.scaleLinear()
      .domain([this.range_max, this.range_min])
      .range([-3 * Math.PI / 4, 3 * Math.PI / 4]);
  }

  private createSVG() {
    this.svg = d3.select(this.el.nativeElement).select('.gauge-container').append('svg')
      .attr('width', this.width)
      .attr('height', this.height);
  }

  private createEmptyArc() {
    let gauge_border = 2.5;

    this.emptyArc = d3.arc()
      .innerRadius(this.innerRadius - gauge_border/2)
      .outerRadius(this.outerRadius + gauge_border/2)
      .startAngle(-3 * Math.PI / 4)
      .endAngle(3 * Math.PI / 4)
      .cornerRadius(10);

    this.svg.append("path")
      .attr("d", this.emptyArc)
      .attr("transform", `translate(${this.width / 2},${this.height/2})`)
      .attr("fill", "#888")  // Adjust to your desired gray color
      .attr("stroke", "#2f2f2f") // Border color
      .attr("stroke-width", gauge_border)  // Border width
      .attr("class", "emptyArc")
      .attr("fill", "url(#emptyArcGradient)");

    this.createGradients();  // Moved gradient creation here

    // Add the max value to the left corner
    this.svg.append("text")
        .attr("x", this.width / 2 + this.outerRadius * Math.cos(1 * Math.PI / 4) * 1.15)
        .attr("y", this.height / 2 + this.outerRadius * Math.sin(1 * Math.PI / 4) * 1.15)
        .attr("text-anchor", "middle")
        .attr("font-family", "monospace")
        .attr("font-size", "16")
        .attr("fill", "#ddd")
        .style("filter", "url(#dropshadow)")
        .text(this.range_max.toString() + this.unit);

    // Add the min value to the right corner
    this.svg.append("text")
        .attr("x", this.width / 2 + this.outerRadius * Math.cos(3 * Math.PI / 4) * 1.15)
        .attr("y", this.height / 2 + this.outerRadius * Math.sin(3 * Math.PI / 4) * 1.15)
        .attr("text-anchor", "middle")
        .attr("font-family", "monospace")
        .attr("font-size", "16")
        .attr("fill", "#ddd")
        .style("filter", "url(#dropshadow)")
        .text(this.range_min.toString() + this.unit);
  }

  private createValueArc(initialValue: number) {
    this.valueArc = d3.arc()
      .innerRadius(this.innerRadius)
      .outerRadius(this.outerRadius)
      .startAngle(-3 * Math.PI / 4)
      .endAngle(-3 * Math.PI / 4 + (6 * Math.PI / 4) * (initialValue / this.range_max))
      .cornerRadius(10);

    this.svg.append("path")
      .attr("class", "valueArc")
      .attr("transform", `translate(${this.width / 2},${this.height/2})`)
      .attr("fill", `url(${location.href}#gaugeGradient)`)
      .datum({ endAngle: -3 * Math.PI / 4 });  // Initial value;
  }

  private createGradients() {
    const defs = this.svg.append("defs");
    
    defs.append("radialGradient")
      .attr("id", "emptyArcGradient")
      .attr("cx", "50%")
      .attr("cy", "50%")
      .attr("r", "50%")
      .attr("fx", "50%")
      .attr("fy", "50%")
      .selectAll("stop")
      .data([
          {offset: "0%", color: "#bbb"},  // Adjust colors to your liking.
          {offset: "100%", color: "#666"}
      ])
      .enter().append("stop")
      .attr("offset", (d: { offset: string; }) => d.offset)
      .attr("stop-color", (d: { color: string; }) => d.color);

    const filter = defs.append("filter")
      .attr("id", "dropshadow")
      .attr("height", "130%");

    filter.append("feGaussianBlur")
      .attr("in", "SourceAlpha")
      .attr("stdDeviation", 4)
      .attr("result", "blur");
    filter.append("feOffset")
      .attr("in", "blur")
      .attr("dx", 3)
      .attr("dy", 3)
      .attr("result", "offsetBlur");
    let feMerge = filter.append("feMerge");

    feMerge.append("feMergeNode").attr("in", "offsetBlur");
    feMerge.append("feMergeNode").attr("in", "SourceGraphic");

    // Gradient for the arc
    this.svg.append("defs").append("linearGradient")
      .attr("id", "gaugeGradient")
      .attr("gradientUnits", "objectBoundingBox")
      .attr("x1", 0).attr("y1", 0.5)  // Starts from left-middle
      .attr("x2", 1).attr("y2", 0.5)  // Ends at right-middle
      .selectAll("stop")
      .data([
        {offset: 0, color: "#416fd9"},
        //{offset: 0.5, color: "#41d1d9"},
        {offset: 1, color: "#41d955"},
        //{offset: 0.2, color: "turquoise"},
        //{offset: 0.8, color: "yellow"},
        //{offset: 1, color: "#f26387"},
      ])
      .enter().append("stop")
      .attr("offset", (d: { offset: number; }) => d.offset)
      .attr("stop-color", (d: { color: string; }) => d.color);
  }

  private createText() {
    //add value text
    this.svg.append("text")
      .attr("class", "gaugeValueText")
      .attr("x", this.width / 2)
      .attr("y", this.height / 2 + 70)
      .attr("text-anchor", "middle")
      .attr("font-family", "monospace")
      .attr("font-size", "28")
      .attr("fill", "#ddd")
      .style("filter", "url(#dropshadow)")
      .text("0" + this.unit);

    //add title text
    this.svg.append("text")
      .attr("x", this.width / 2)
      .attr("y", this.height / 2 + 115)
      .attr("text-anchor", "middle")
      .attr("font-family", "monospace")
      .attr("font-size", "24")
      .attr("fill", "#ddd")
      .style("filter", "url(#dropshadow)")
      .text(this.title);
  }

  private createNeedle() {
    // add needle
    this.svg.append("line")
      .datum({ angle: this.scale(this.range_min) })  // Store the initial angle.
      .attr("x1", this.width / 2)
      .attr("y1", this.height / 2)
      .attr("x2", this.width / 2 + this.innerRadius * Math.cos(Math.PI / 2 + this.scale(this.range_min) + 0.06) * 0.875)
      .attr("y2", this.height / 2 - this.innerRadius * Math.sin(Math.PI / 2 + this.scale(this.range_min) + 0.06) * 0.875)
      .attr("class", "needle")
      .attr("stroke", "#ddd")
      .attr("stroke-width", "5")
      .style("stroke-linecap", "round")
      .style("filter", "url(#dropshadow)");

    // Add a pivot point for the needle
    this.svg.append("circle")
    .attr("cx", this.width / 2)
    .attr("cy", this.height / 2)
    .attr("r", 10)  // Radius of the pivot point. You can adjust this value.
    .attr("fill", "#c3c3c3");  // Fill color of the pivot. Adjust as needed.
  }

  private createGauge(value: number) {
    this.initializeScale();
    this.createSVG();
    this.createEmptyArc();
    this.createValueArc(this.range_min);
    this.createText();
    this.createNeedle();
    this.fetchDataAndUpdateGauge();
  }

  private updateValueArc(value: number) {
    let newEndAngle = Math.min(this.scale(value), this.scale(this.range_min));
    newEndAngle = Math.max(newEndAngle, this.scale(this.range_max));
    //const newEndAngle = this.scale(value);

    const valueArcSelection = this.svg.select(".valueArc");

    // Smooth transition
    valueArcSelection.transition()
        .duration(this.transitionDuration)
        .attrTween("d", (d: any) => {
            const interpolate = d3.interpolate(d.endAngle, -newEndAngle);
            return (t: number) => {
                d.endAngle = interpolate(t);
                this.valueArc.endAngle(d.endAngle);
                return this.valueArc(d);
            };
        });
  }

  private updateNeedle(value: number) {
    let angle = Math.min(this.scale(value), this.scale(this.range_min));
    angle = Math.max(angle, this.scale(this.range_max));

    // Get the needle selection
    const needleSelection = this.svg.select(".needle");

    // Smooth transition for the needle
    needleSelection.transition()
        .duration(this.transitionDuration)
        .attrTween("x2", (d: any) => {
            const interpolate = d3.interpolate(d.angle, angle);
            return (t: number) => {
                d.angle = interpolate(t);
                return this.width / 2 + this.innerRadius * Math.cos(Math.PI / 2 + d.angle + 0.06) * 0.875;
            };
        })
        .attrTween("y2", (d: any) => {
            const interpolate = d3.interpolate(d.angle, angle);
            return (t: number) => {
                return this.height / 2 - this.innerRadius * Math.sin(Math.PI / 2 + d.angle + 0.06) * 0.875;
            };
        });
  }

  private updateValueText(value: number) {
    /*this.svg.select(".gaugeValueText")
        .text(value.toString() + this.unit);*/
    
    const textElement = this.svg.select(".gaugeValueText");

    // Get the current value of the text element
    const currentValue = +textElement.text().replace(this.unit, '');
    const unit = this.unit;

    // Determine the color based on the value change
    const color = value > currentValue ? "green" : "red";

    const transitionDuration = this.transitionDuration;

    // Create a custom tween function
    textElement.transition()
      .duration(transitionDuration/4) // Duration of the transition in milliseconds
      .attr("fill", color)
      .duration(transitionDuration) // Duration of the transition in milliseconds
      .tween('text', function() {
            // Define the interpolator function
            const i = d3.interpolateNumber(currentValue, value);

            return function(t:any) {
                // Update the text with the interpolated value
                textElement.text(i(t).toFixed(2) + unit);
            };
        })
        .on("end", function() {
            // Transition to white color after the main transition completes
            textElement.transition()
                .duration(transitionDuration/2) // You can adjust this duration as needed
                .attr("fill", "white");
        });
  }

  private updateGauge(value: number) {
    if(this.lastValue == value) return;
    this.lastValue = value;
    this.updateValueArc(value);
    this.updateNeedle(value);
    this.updateValueText(value);
  }

  fetchDataAndUpdateGauge() {
    if(this.gettingData) return;
    this.gettingData = true;
    this.dataService.getLatestData(this.site, this.category).subscribe((data: any) => {
      // Assuming the response has a property 'value' which contains the data for the gauge
      const gaugeValue = data.Response[1];
      console.log("GaugeComponent fetchDataAndUpdateGauge", gaugeValue);
      this.updateGauge(gaugeValue);
      this.gettingData = false;
    });
  }

  ngOnInit() {
    console.log("GaugeComponent ngOnInit");
    this.createGauge(0);

    this.updateSubscription = timer(0, this.updateInterval).pipe(

    ).subscribe(result => 

      this.fetchDataAndUpdateGauge()

    );
  }

  ngOnDestroy() {
    this.updateSubscription.unsubscribe();
    this.lastValue = 0;
  }
}