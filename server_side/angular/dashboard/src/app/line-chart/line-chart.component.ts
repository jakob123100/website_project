import { ViewEncapsulation } from '@angular/core';
import { Component, OnInit } from '@angular/core';
import * as d3 from 'd3';
import { HttpClient } from '@angular/common/http';
import { interval } from 'rxjs';
import { delay, startWith, switchMap } from 'rxjs/operators';

@Component({
  selector: 'app-line-chart',
  templateUrl: './line-chart.component.html',
  styleUrls: ['./line-chart.component.css'],
  encapsulation: ViewEncapsulation.None
})

export class LineChartComponent implements OnInit {
  private data: {date: Date, value: number}[] = [];
  private svg: any;
  private margin = {top: 50, right: 40, bottom: 60, left: 60};
  private width = 960 - this.margin.left - this.margin.right;
  private height = 500 - this.margin.top - this.margin.bottom;
  private xScale: any;
  private yScale: any;
  private xAxis: any;
  private yAxis: any;
  private line: any;
  private valueline: any;
  private totalLength = 0;
  private old_len = 0;
  private tooltip: any;
  private tooltip_enabled: boolean = false;
  private minY = 0
  private maxY = 0
  private colors = ["#0d6efd", "#198754", "#ab2e3c"];
  private labels = ["Data 1", "Data 2", "Data 3"];

  constructor(private http: HttpClient) { }

  ngOnInit() {
    this.fetchData().subscribe((res: any) => {
      this.data = this.processData(res.Response);
      this.createChart();
      this.updateData();
    });
  }

  private fetchData(){
    return this.http.get('http://217.208.66.120:7777/koltrastvägen/temp_outdoor_c/get/all')
  }

  private processData(rawData: [string, number][]): {date: Date, value: number}[] {
    return rawData.map((d: [string, number]) => ({date: new Date(d[0]), value: d[1]})).reverse();
  }

  private updateData() {
    interval(5000).pipe(
      switchMap(() => this.fetchData())
    ).subscribe((res: any) => {
      this.data = this.processData(res.Response);
      this.updateChart();
      console.log("asddas")
    });
  }

  private createChart() {
    this.initializeSvg();
    this.createScales();
    this.createLine();
    this.addAxes();
    this.addLabels();
    this.addTitle();
    this.addLegend();
    this.addTooltip();
  }

  private initializeSvg() {
    this.svg = d3.select('body').append('svg')
      .attr("class", "plot")
      .attr('width', this.width + this.margin.left + this.margin.right)
      .attr('height', this.height + this.margin.top + this.margin.bottom)
      .append('g')
      .attr('transform', 'translate(' + this.margin.left + ',' + this.margin.top + ')');
  }
  
  private createScales() {
    // X scale
    let min_time = this.getMinTime(this.data);
    let max_time = this.getMaxTime(this.data);
  
    this.xScale = d3.scaleTime()
      .domain([min_time, max_time] as [Date, Date])
      .range([0, this.width]);
  
    // Y scale
    this.yScale = d3.scaleLinear()
      .domain([
        Math.min(this.minY, d3.min(this.data, d => d.value) ?? 0),
        Math.max(this.maxY, d3.max(this.data, d => d.value + 5) ?? 0)
      ] as [number, number])
      .range([this.height, 0]);
  }
  
  private getMinTime(data: {date: Date, value: number}[]): Date {
    let min_time: Date = new Date(d3.min(data, d => d.date) ?? new Date);
    min_time.setHours(0);
    min_time.setMinutes(0);
    min_time.setSeconds(0);
    min_time.setMilliseconds(0);
    return min_time;
  }
  
  private getMaxTime(data: {date: Date, value: number}[]): Date {
    let max_time: Date = new Date(d3.max(data, d => d.date) ?? new Date);
    max_time.setHours(23);
    max_time.setMinutes(59);
    max_time.setSeconds(59);
    max_time.setMilliseconds(0);
    return max_time;
  }
  
  private createLine() {
    this.svg.append("defs")
      .append("filter")
      .attr("id", "glow")
      .append("feGaussianBlur")
      .attr("stdDeviation", "4")
      .attr("result", "coloredBlur");

    let feMerge = this.svg.select("#glow")
      .append("feMerge");
    
    feMerge.append("feMergeNode")
      .attr("in", "coloredBlur");
    feMerge.append("feMergeNode")
      .attr("in", "SourceGraphic");

    // Define the line
    this.valueline = d3.line<{ date: Date, value: number }>()
      .x(d => this.xScale(d.date))
      .y(d => this.yScale(d.value))
      .curve(d3.curveMonotoneX);
  
    this.line = this.svg.append("path")
      .datum(this.data)
      .attr("class", "chart line")
      .attr('fill', 'none')
      .attr('stroke', this.colors[0])
      .attr('stroke-width', 2)
      .attr('d', this.valueline)
      .style("filter", "url(#glow)");

    // Update total length
    this.totalLength = this.line.node().getTotalLength();
  
    // Animate line drawing
    this.line.attr("stroke-dasharray", this.totalLength + " " + this.totalLength)
      .attr("stroke-dashoffset", this.totalLength - this.old_len)
      .transition()
      .duration(2000)
      .ease(d3.easeLinear)
      .attr("stroke-dashoffset", 0);

      this.old_len = this.totalLength
  }
  
  private addAxes() {
    // X-axis
    this.xAxis = this.svg.append("g")
      .attr("class", "axis axis--x")
      .attr("transform", "translate(0," + this.height + ")")
      .call(d3.axisBottom(this.xScale).ticks(5).tickPadding(10).tickSize(10));
  
    // Y-axis
    this.yAxis = this.svg.append("g")
      .attr("class", "axis axis--y")
      .call(d3.axisLeft(this.yScale).ticks(5).tickPadding(10).tickSize(10));
  }
  
  private addLabels() {
    // X-axis label
    this.svg.append("text")
      .attr("class", "x label")
      .attr("text-anchor", "end")
      .attr("x", this.width)
      .attr("y", this.height - 6)
      .text("Date");
  
    // Y-axis label
    this.svg.append("text")
      .attr("class", "y label")
      .attr("text-anchor", "end")
      .attr("y", 6)
      .attr("dy", "0.5em")
      .attr("dx", "1.5em")
      .text("°C");
  }
  
  private addTitle() {
    // Chart title
    this.svg.append("text")
      .attr("class", "chartTitle")
      .attr("x", this.width / 2)
      .attr("y", -20)
      .attr("text-anchor", "middle")
      .text("Temperature");
  }
  
  private addLegend() {
    // Add the legend
    let legend = this.svg.selectAll(".legend")
      .data(this.labels)
      .enter().append("g")
      .attr("class", "legend")
      .attr("transform", (d: any, i: number) => "translate(0," + i * 20 + ")");
  
    // Add the colored rectangles
    legend.append("line")
      .attr("x1", 160)
      .attr("x2", 180)
      .attr("y1", -25)
      .attr("y2", -25)
      .attr("stroke", (d: any, i: number) => this.colors[i])
      .attr("stroke-width", 3);
  
    // Add the labels
    legend.append("text")
      .attr("x", 150)
      .attr("y", -25)
      .attr("dy", ".35em")
      .style("text-anchor", "end")
      .text((d: any) => d);
  }
  
  private addTooltip() {
    this.tooltip = d3.select("body").append("div")
      .attr("class", "tooltip")
      .style("opacity", 0);
  
    // Add a circle element
  
    const circle = this.svg.append("circle")
      .attr("class", "dot")
      .attr("r", 0)
      .attr("fill", "steelblue")
      .style("stroke", "white")
      .attr("opacity", .70)
      .style("pointer-events", "none");
  
    // Create a listening rectangle
  
    const listeningRect = this.svg.append("rect")
      .attr("width", this.width)
      .attr("height", this.height)
      .attr("opacity", 0);
  
    listeningRect.on("mousemove", (event: MouseEvent) => {
      this.handleMouseMove(event, circle);
    });
  
    listeningRect.on("mouseout", (event: MouseEvent, d: {date: Date, value: number}) => {
      this.handleMouseOut(circle);
    });
  }

  private handleMouseMove(event: MouseEvent, circle: any) {
    const [xCoord] = d3.pointer(event, this);
    const bisectDate = d3.bisector((d:any) => d.date).left;
    const x0 = this.xScale.invert(xCoord - 68);
    const i = bisectDate(this.data, x0, 1);
    const d0: any = this.data[i - 1];
    const d1: any = this.data[i];
  
    try {
      const data = x0 - d0.date > d1.date - x0 ? d1 : d0;
      const xPos = this.xScale(data.date);
      const yPos = this.yScale(data.value);
  
      // Update the circle position
      circle.attr("cx", xPos).attr("cy", yPos);
  
      // Add transition for the circle radius
      if(!this.tooltip_enabled){
        circle.transition()
          .duration(300)
          .attr("r", 5);
  
        this.tooltip.transition()
          .duration(300)
          .style("opacity", .9);
  
        this.tooltip_enabled = true;
      }
  
      this.tooltip.html("Date: " + data.date.getFullYear() + "/" + (data.date.getMonth() + 1) + "/" + data.date.getDate() + 
      " " + data.date.getHours() + ":" + data.date.getMinutes() + ":" + data.date.getSeconds() +
      "<br/>Value: " + data.value);
  
      let node = this.tooltip.node();
      if(node === null){
        return;
      }
  
      let tooltipBox = node.getBoundingClientRect();
      this.tooltip.style("left", (this.margin.left + this.xScale(data.date) + 35) + "px")
        .style("top", (this.yScale(data.value) + tooltipBox.height/2) + "px");
    } catch {
      if(!this.tooltip_enabled){
        return;
      }
      circle.transition()
        .duration(500)
        .attr("r", 0);
  
      this.tooltip.transition()
        .duration(500)
        .style("opacity", 0);
  
      this.tooltip_enabled = false;
    }
  }
  
  private handleMouseOut(circle: any) {
    if(!this.tooltip_enabled){
      return;
    }
  
    circle.transition()
      .duration(500)
      .attr("r", 0);
  
    this.tooltip.transition()
      .duration(500)
      .style("opacity", 0);
  
    this.tooltip_enabled = false;
  }

  private updateChart() {
    this.updateScales();
    this.updateAxes();
    this.updateLine();
  }

  private updateScales() {
    // Update X scale
    let min_time = this.getMinTime(this.data);
    let max_time = this.getMaxTime(this.data);
  
    this.xScale.domain([min_time, max_time] as [Date, Date]);
  
    // Update Y scale
    this.yScale.domain([
      Math.min(this.minY, d3.min(this.data, d => d.value) ?? 0),
      Math.max(this.maxY, d3.max(this.data, d => d.value + 5) ?? 0)
    ] as [number, number]);
  }
  
  private updateAxes() {
    // Update X-axis
    this.xAxis.transition()
      .duration(750)
      .call(d3.axisBottom(this.xScale).ticks(5).tickPadding(10).tickSize(10));
  
    // Update Y-axis
    this.yAxis.transition()
      .duration(750)
      .call(d3.axisLeft(this.yScale).ticks(5).tickPadding(10).tickSize(10));
  }
  
  private updateLine() {
    // Update line path
    this.line.datum(this.data)
      .transition()
      .duration(750)
      .attr("d", this.valueline);
  
    // Update total length
    this.totalLength = this.line.node().getTotalLength();
  
    // Animate line drawing
    this.line.attr("stroke-dasharray", this.totalLength + " " + this.totalLength)
      .attr("stroke-dashoffset", this.totalLength - this.old_len)
      .transition()
      .duration(2000)
      .ease(d3.easeLinear)
      .attr("stroke-dashoffset", 0);

      this.old_len = this.totalLength
  }
}