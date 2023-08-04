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
      delay(5000),
      switchMap(() => this.fetchData())
    ).subscribe((res: any) => {
      this.data = this.processData(res.Response);
      this.updateChart();
      console.log("asddas")
    });
  }

  createChart(){
    d3.select('body').html("");

    this.data = this.data.map((d, i) => ({id: i, date: new Date(d.date), value: d.value}))

    // Define the colors for the legend
    let colors = ["#0d6efd", "#198754", "#ab2e3c"];
  
    // Define the labels for the legend
    let labels = ["Temp Outdoors", "Data 2", "Data 3"];

    // Filter the labels and colors to only include the first 2
    labels = labels.slice(0, 1);
    colors = colors.slice(0, 1);

    let min_time: Date = new Date(d3.max(this.data, d => d.date) ?? new Date);
    let max_time: Date = new Date(d3.max(this.data, d => d.date) ?? new Date);
    
    min_time.setHours(0)
    min_time.setMinutes(0)
    min_time.setSeconds(0)
    min_time.setMilliseconds(0)

    max_time.setHours(23)
    max_time.setMinutes(59)
    max_time.setSeconds(59)
    max_time.setMilliseconds(0)

    this.xScale = d3.scaleTime()
      //.domain(d3.extent(this.data, d => d.date) as [Date, Date])
      .domain([
        min_time, 
        max_time
      ] as [Date, Date])
      .range([0, this.width]);

    this.yScale = d3.scaleLinear()
    .domain([
      //Math.min(this.minY, d3.min(this.data, d => d.value - 5) ?? 0), 
      d3.min(this.data, d => d.value - 5), 
      d3.max(this.data, d => d.value + 5)
    ] as [number, number])
    .range([this.height, 0]);

    // Define the line
    this.valueline = d3.line<{ date: Date, value: number }>()
      .x(d => this.xScale(d.date))
      .y(d => this.yScale(d.value))
      .curve(d3.curveMonotoneX);

    this.svg = d3.select('body').append('svg')
      .attr("class", "plot")
      .attr('width', this.width + this.margin.left + this.margin.right)
      .attr('height', this.height + this.margin.top + this.margin.bottom)
      .append('g')
      .attr('transform', 'translate(' + this.margin.left + ',' + this.margin.top + ')');

    this.svg.append("defs")
      .append("filter")
      .attr("id", "glow")
      .append("feGaussianBlur")
      .attr("stdDeviation", "3")
      .attr("result", "coloredBlur");
    
    let feMerge = this.svg.select("#glow")
      .append("feMerge");
    
    feMerge.append("feMergeNode")
      .attr("in", "coloredBlur");
    feMerge.append("feMergeNode")
      .attr("in", "SourceGraphic");

    // Add a path for the line chart
    this.line = this.svg.append("path")
      .datum(this.data)
      .attr("class", "chart line")
      .attr('fill', 'none')
      .attr('stroke', colors[0])
      .attr('stroke-width', 2)
      .attr('d', this.valueline)
      .style("filter", "url(#glow)");

    // Add the animation
    this.totalLength = (this.line.node() as SVGPathElement).getTotalLength();

    this.old_len = 0

    this.line.attr("stroke-dasharray", this.totalLength + " " + this.totalLength)
      .attr("stroke-dashoffset", this.totalLength - this.old_len)
      .transition()
      .duration(2000)
      .ease(d3.easePolyInOut)
      .attr("stroke-dashoffset", 0);

    this.old_len = this.totalLength

    // X-axis
    this.xAxis = this.svg.append("g")
      .attr("class", "axis axis--x")  // Add class to the x-axis
      .attr("transform", "translate(0," + this.height + ")")
      .call(
        d3.axisBottom(this.xScale)
        .ticks(5)
        .tickPadding(10)
        .tickSize(10)
        );

    // Y-axis
    this.yAxis = this.svg.append("g")
      .attr("class", "axis axis--y")  // Add class to the y-axis
      .call(d3.axisLeft(this.yScale).ticks(5).tickPadding(10).tickSize(10));

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
      //.attr("transform", "rotate(-90)")
      .text("°C");

    // Chart title
    this.svg.append("text")
      .attr("class", "chartTitle")
      .attr("x", this.width / 2)
      .attr("y", -20)
      .attr("text-anchor", "middle")
      .text("Temerature");

    // Add the legend
    let legend = this.svg.selectAll(".legend")
      .data(labels)
      .enter().append("g")
      .attr("class", "legend")
      .attr("transform", (d: any, i: number) => "translate(0," + i * 20 + ")");

    // Add the colored rectangles
    legend.append("line")
      .attr("x1", 160)
      .attr("x2", 180)
      .attr("y1", -25)
      .attr("y2", -25)
      .attr("stroke", (d: any, i: number) => colors[i])
      .attr("stroke-width", 3);

    // Add the labels
    legend.append("text")
      .attr("x", 150)
      .attr("y", -25)
      .attr("dy", ".35em")
      .style("text-anchor", "end")
      .text((d: any) => d);

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
      // create a listening rectangle

      const listeningRect = this.svg.append("rect")
      .attr("width", this.width)
      .attr("height", this.height)
      .attr("opacity", 0);

    listeningRect.on("mousemove", (event: MouseEvent) => {
      const [xCoord] = d3.pointer(event, this);
      const bisectDate = d3.bisector((d:any) => d.date).left;
      const x0 = this.xScale.invert(xCoord - 68);
      const i = bisectDate(this.data, x0, 1);
      const d0: any = this.data[i - 1];
      const d1: any = this.data[i];
      try{
        const data = x0 - d0.date > d1.date - x0 ? d1 : d0;
        const xPos = this.xScale(data.date);
        const yPos = this.yScale(data.value);

        // Update the circle position

        circle.attr("cx", xPos)
          .attr("cy", yPos);

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

        this.tooltip.html("Date: " + data.date.getFullYear() + "/" + data.date.getMonth() + 1 + "/" + data.date.getDate() + 
        " " + data.date.getHours() + ":" + data.date.getMinutes() + ":" + data.date.getSeconds() +
        "<br/>Value: " + data.value);
        let node = this.tooltip.node()
        if(node === null){
          return
        }
        
        let tooltipBox = node.getBoundingClientRect();
        this.tooltip.style("left", (this.margin.left + this.xScale(data.date) + 35) + "px")
          .style("top", (this.yScale(data.value) + tooltipBox.height/2) + "px");
        
      }
      catch{
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
      })

      listeningRect.on("mouseout", (event: MouseEvent, d: {date: Date, value: number}) => {

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
      });
  }

  updateChart() {
    let min_time: Date = new Date(d3.max(this.data, d => d.date) ?? new Date);
    let max_time: Date = new Date(d3.max(this.data, d => d.date) ?? new Date);
    
    min_time.setHours(0)
    min_time.setMinutes(0)
    min_time.setSeconds(0)
    min_time.setMilliseconds(0)

    max_time.setHours(23)
    max_time.setMinutes(59)
    max_time.setSeconds(59)
    max_time.setMilliseconds(0)

    this.xScale = d3.scaleTime()
      //.domain(d3.extent(this.data, d => d.date) as [Date, Date])
      .domain([
        min_time, 
        max_time
      ] as [Date, Date])
      .range([0, this.width]);

    this.yScale = d3.scaleLinear()
    .domain([
      d3.min(this.data, d => d.value - 5), 
      d3.max(this.data, d => d.value + 5)
    ] as [number, number])
    .range([this.height, 0]);

    // Update axes
    this.xAxis
    .call(
      d3.axisBottom(this.xScale)
      .ticks(5)
      .tickPadding(10)
      .tickSize(10)
      );
    this.yAxis.call(d3.axisLeft(this.yScale).ticks(5).tickPadding(10).tickSize(10));

    // Update the line generator
    this.valueline = d3.line<{ date: Date, value: number }>()
      .x(d => this.xScale(d.date))
      .y(d => this.yScale(d.value))
      .curve(d3.curveMonotoneX);

    let line = d3.line<{ date: Date, value: number }>()
      .x(d => this.xScale(d.date))
      .y(d => this.yScale(d.value))
      .curve(d3.curveMonotoneX);

    // Bind the data to the line
    const update = this.svg.selectAll(".chart.line").data([this.data]);

    // Update the line
    update.enter().append("path").merge(update).attr("d", this.valueline);

    // Remove old elements as needed
    update.exit().remove();

    // Add the animation
    this.totalLength = (this.line.node() as SVGPathElement).getTotalLength();

    this.line.attr("stroke-dasharray", this.totalLength + " " + this.totalLength)
      .attr("stroke-dashoffset", (0))

    this.line.attr("stroke-dasharray", this.totalLength + " " + this.totalLength)
      .attr("stroke-dashoffset", (this.totalLength - this.old_len))
      .transition()
      .duration(2000)
      //.ease(d3.easeLinear)
      .attr("stroke-dashoffset", 0);

      
    this.old_len = this.totalLength
  }

}