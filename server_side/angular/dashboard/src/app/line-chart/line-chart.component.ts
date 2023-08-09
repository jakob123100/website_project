import { ViewEncapsulation } from '@angular/core';
import { Component, OnInit, Input } from '@angular/core';
import * as d3 from 'd3';
import { HttpClient } from '@angular/common/http';
import { interval, forkJoin, Observable } from 'rxjs';
import { delay, map, startWith, switchMap } from 'rxjs/operators';

@Component({
  selector: 'app-line-chart',
  templateUrl: './line-chart.component.html',
  styleUrls: ['./line-chart.component.css'],
  encapsulation: ViewEncapsulation.None
})

export class LineChartComponent implements OnInit {
  //@Input() site!: string;
  //@Input() category!: string;
  @Input() dataSources: { site: string, category: string, label: string }[] = [];
  @Input() timeframe!: string; // E.g., "lastHour", "lastDay"

  private allData: {date: Date, value: number}[][] = [];
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
  private colors = ["#0d6efd", "#198754", "#ab2e3c"];
  private labels = ["Data 1", "Data 2", "Data 3"];

  constructor(private http: HttpClient) { }

  ngOnInit() {
    //this.fetchDataForTimeframe();

    this.fetchDataForTimeframe().subscribe(allData => {
      console.log(allData);
      this.allData = allData;
      this.createChart();
      this.updateData();
    });
  }

  fetchDataForTimeframe() {
    let currentTime = new Date(Date.now() + 2 * 60 * 60 * 1000);
    let startDate: Date = new Date(currentTime);
    let startTime: string;
    let endTime: string = new Date(currentTime).toISOString();

    switch (this.timeframe) {
        case 'lastHour':
          startDate.setHours(currentTime.getHours() - 1)

          startTime = new Date(startDate).toISOString(); // 1 hour ago
          break;
        case 'thisDay':
          startDate.setHours(2)
          startDate.setMinutes(0)
          startDate.setSeconds(0)

          startTime = new Date(startDate).toISOString(); // 1 day ago
          break;
        // ... other timeframes

        default:
          startDate.setHours(2)
          startDate.setMinutes(0)
          startDate.setSeconds(0)
          startTime = new Date(startDate).toISOString(); // 1 day ago
          break;
    }

    return this.getDataBetweenDates(startTime, endTime);

    this.getDataBetweenDates(startTime, endTime).subscribe(allData => {
      console.log(allData);
      return allData;
      // Do any additional processing here if needed
    });
  }

  getDataBetweenDates(startTime: string, endTime: string): Observable<any[]> {
    // Create an array to hold our observables
    let observables: Observable<any>[] = [];
  
    this.dataSources.forEach(dataSource => {
      // Construct the API endpoint
      const apiUrl = `http://217.208.66.120:7777/${dataSource.site}/${dataSource.category}/get/between-date-time`;
  
      // Push the Observable into our array
      observables.push(this.http.get(apiUrl, {
        params: {
          startTime: startTime,
          endTime: endTime
        }
      }));
    });
  
    // Use forkJoin to wait for all the Observables to complete
    return forkJoin(observables).pipe(
      map((responses: any[]) => {
        let allData: any = [];
        responses.forEach(res => {
          let processedData = this.processData(res.Response);
          allData.push(processedData);
        });
        return allData;
      })
    );
  }

  private fetchData(){
    return this.http.get('http://217.208.66.120:7777/koltrastvägen/temp_outdoor_c/get/all')
  }

  private processData(rawData: [string, number][]): {date: Date, value: number}[] {
    return rawData.map((d: [string, number]) => ({date: new Date(d[0]), value: d[1]})).reverse();
  }

  private updateData() {
    // Start an interval that emits every 5 seconds
    interval(5000).pipe(
      // For each emission from the interval, switch to fetching the data
      switchMap(() => this.fetchDataForTimeframe())
    ).subscribe(allData => {
      this.allData = allData;
      this.updateChart();
      console.log("asdasd");
    });
  }

  private createChart() {
    this.initializeSvg();  
    this.createScales();
    
    // Create a line for each dataset
    this.allData.forEach((dataset, index) => {
      this.createLine(dataset, index);
    });

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
    let data = this.allData[0]
    console.log(data)
    // X scale
    let min_time = this.getMinTime(data);
    let max_time = this.getMaxTime(data);
  
    this.xScale = d3.scaleTime()
      .domain([min_time, max_time] as [Date, Date])
      .range([0, this.width]);
  
    // Y scale v
    this.yScale = d3.scaleLinear()
      .domain([
        d3.min(data, d => d.value - 5),
        d3.max(data, d => d.value + 5)
      ] as [number, number])
      .range([this.height, 0]);
  }
  
  private getMinTime(data: {date: Date, value: number}[]): Date {
    let min_time: Date = new Date(d3.max(data, d => d.date) ?? new Date);
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
  
  private createLine(dataset: { date: Date, value: number }[], index: number) {
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
  
    // Use the index to determine the line's color from the colors array
    const lineColor = this.colors[index % this.colors.length];

    this.line = this.svg.append("path")
      .datum(dataset)
      .attr("class", "chart line")
      .attr('fill', 'none')
      .attr('stroke', lineColor)
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
    // Find the closest data point from any line
    let closestDataPoint: { date: Date, value: number | undefined } = { date: new Date, value: undefined };
    let closestDistance = Infinity;
    let closestDatasetIndex = -1;
    
    this.allData.forEach((dataset, index) => {
      const bisect = d3.bisector((d: any) => d.date).left;
      const x0 = this.xScale.invert(d3.pointer(event)[0]);
      const i = bisect(dataset, x0, 1);
      const d0 = dataset[i - 1];
      const d1 = dataset[i];
      const d = (d1 && d0) ? (x0.getTime() - d0.date.getTime() > d1.date.getTime() - x0.getTime() ? d1 : d0) : null;

      if (d) {
        const distance = Math.abs(this.xScale(d.date) - d3.pointer(event)[0]);
        if (distance < closestDistance) {
          closestDistance = distance;
          closestDataPoint = d;
          closestDatasetIndex = index;
        }
      }
    });

    if(closestDataPoint.value == undefined){
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

      return;
    }
  
    const xPos = this.xScale(closestDataPoint.date);
    const yPos = this.yScale(closestDataPoint.value);

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

    this.tooltip.html("Date: " + closestDataPoint.date.getFullYear() + "/" + (closestDataPoint.date.getMonth() + 1) + "/" + closestDataPoint.date.getDate() + 
    " " + closestDataPoint.date.getHours() + ":" + closestDataPoint.date.getMinutes() + ":" + closestDataPoint.date.getSeconds() +
    "<br/>Value: " + closestDataPoint.value);

    let node = this.tooltip.node();

    let tooltipBox = node.getBoundingClientRect();
    this.tooltip.style("left", (this.margin.left + this.xScale(closestDataPoint.date) + 35) + "px")
      .style("top", (this.yScale(closestDataPoint.value) + tooltipBox.height/2) + "px");
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
    let data = this.allData[0]

    // Update X scale
    let min_time = this.getMinTime(data);
    let max_time = this.getMaxTime(data);
  
    this.xScale.domain([min_time, max_time] as [Date, Date]);
  
    // Update Y scale
    this.yScale.domain([
      d3.min(data, d => d.value - 5),
      d3.max(data, d => d.value + 5)
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
    // Update each line based on its corresponding dataset
  this.allData.forEach((dataset, index) => {
    const lineElement = this.svg.select(".line" + index);
    lineElement.datum(dataset)
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
    });
  
  }   
}