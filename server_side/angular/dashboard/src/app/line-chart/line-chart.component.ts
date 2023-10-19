import { ViewEncapsulation } from '@angular/core';
import { Component, OnInit, Input, ElementRef } from '@angular/core';
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
  @Input() chartTitle!: string; // E.g., "lastHour", "lastDay"
  @Input() labels!: { yAxis: string, xAxis: string}; // E.g., "lastHour", "lastDay"
  @Input() dataSources: { site: string, category: string, label: string }[] = [];
  @Input() timeframe!: string; // E.g., "lastHour", "lastDay"
  @Input() smoothingFactor: number = 1; // E.g., "lastHour", "lastDay"

  private allData: {date: Date, value: number}[][] = [];
  private svg: any;
  private margin = {top: 50, right: 40, bottom: 60, left: 60};
  private width = 1400 - this.margin.left - this.margin.right;
  private height = 800 - this.margin.top - this.margin.bottom;
  private xScale: any;
  private yScale: any;
  private xAxis: any;
  private yAxis: any;
  private line: any;
  private valueline: any;
  private totalLength = 0;
  private tooltip: any;
  private tooltip_enabled: boolean = false;
  private colors = ["#3278fa", "#1ad994", "#04c7d1", "#8e3dff", "#d4709b"];
  private legends = ["Data 1", "Data 2", "Data 3", "Data 4", "Data 5"];
  private startDate: Date = new Date();
  private endDate: Date = new Date();
  private DATAPOINTS_PER_GRAPH = 150;
  private updateInterval = 5000;

  constructor(private el: ElementRef, private http: HttpClient) { }

  ngOnInit() {
    this.setDates();
    this.legends = [];
    this.initializeSvg(); 
    this.dataSources.forEach(dataSource => {
      this.legends.push(dataSource.label.toString())
    });

    this.fetchDataForTimeframe().subscribe(allData => {
      this.allData = allData;
      this.createChart(); 
      this.updateData();
    });
  }

  getPosition(event: { srcElement: any; }){
    let offsetLeft = 0;
    let offsetTop = 0;

    let el = event.srcElement;

    while(el){
        offsetLeft += el.offsetLeft;
        offsetTop += el.offsetTop;
        el = el.parentElement;
    }
    return { offsetTop:offsetTop , offsetLeft:offsetLeft }
  }

  fetchDataForTimeframe() {
    this.setDates();

    let startTime: string = this.startDate.toISOString();
    let endTime: string = this.endDate.toISOString();

    return this.getDataBetweenDates(startTime, endTime);
  }

  setDates(){
    let currentTime = new Date(Date.now() + 2 * 60 * 60 * 1000);
    this.startDate = new Date(currentTime);
    this.endDate = new Date(currentTime);
    this.endDate.setHours(2, 0, 0, 0)
    this.endDate.setUTCDate(currentTime.getUTCDate() + 1);

    switch (this.timeframe) {
        case 'lastHour':
          this.startDate = new Date(currentTime.getTime() - 1 * 60 * 60 * 1000);
          this.endDate = new Date(currentTime.getTime());
          this.updateInterval = 1000 * 5;
          break;
        case 'thisDay':
          this.startDate.setHours(2, 0, 0, 0);
          this.startDate.setUTCDate(currentTime.getUTCDate());
          this.updateInterval = 1000 * 60;
          break;
        case 'thisWeek':
          this.startDate.setHours(2, 0, 0, 0)
          this.startDate.setUTCDate(currentTime.getUTCDate() - 7);
          this.updateInterval = 1000 * 60 * 5;
          break;
        case 'thisMonth':
          this.startDate.setHours(2, 0, 0, 0);
          this.startDate.setUTCDate(currentTime.getUTCDate());
          this.startDate.setUTCMonth(currentTime.getUTCMonth() - 1);
          this.updateInterval = 1000 * 60 * 10;
          break;
        case 'thisYear':
          this.startDate.setHours(2, 0, 0, 0);
          this.startDate.setUTCDate(currentTime.getUTCDate());
          this.startDate.setUTCFullYear(currentTime.getUTCFullYear() - 1);
          this.updateInterval = 1000 * 60 * 60;
        break;
        // ... other timeframes

        default:
          this.startDate.setHours(2, 0, 0, 0)
          this.startDate.setUTCDate(currentTime.getUTCDate())
          break;
    }
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
          
          processedData = this.sampleDataByTime(processedData, this.DATAPOINTS_PER_GRAPH);
          processedData = this.smoothData(processedData, this.smoothingFactor);
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
    interval(this.updateInterval).pipe(
      // For each emission from the interval, switch to fetching the data
      switchMap(() => this.fetchDataForTimeframe())
    ).subscribe(allData => {
      this.allData = allData;
      this.updateChart();
    });
  }

  /**
  * Samples data at regular time intervals.
  * @param data - The original dataset, sorted by date/time.
  * @param desiredPoints - The number of data points you want.
  * @returns - The sampled dataset.
  */
  private sampleDataByTime(data: { date: Date, value: number }[], desiredPoints: number): { date: Date, value: number }[] {
    if (desiredPoints >= data.length || desiredPoints <= 0) {
        return data;  // Return original data if desiredPoints is invalid.
    }

    const timeRange = data[data.length - 1].date.getTime() - data[0].date.getTime();
    const timeInterval = timeRange / (desiredPoints - 1);
    
    let sampled = [];
    let nextTime = data[0].date.getTime();

    for (let point of data) {
        if (point.date.getTime() >= nextTime) {
            sampled.push(point);
            nextTime += timeInterval;
        }
    }

    return sampled;
  }

  private smoothData(data: { date: Date, value: number }[], smoothingFactor: number): { date: Date, value: number }[] {
    if (smoothingFactor <= 1) {
        return data;  // Return original data if smoothingFactor is invalid.
    }

    let smoothedData: { date: Date, value: number }[] = data;
    for (let i = 0; i < data.length; i++) {
      let sum = 0;
      let smoothBy = Math.min(smoothingFactor, data.length - i)
      for (let j = 0; j < smoothBy; j++) {
        sum += data[i + j].value;
      }
      smoothedData[i].value = Math.round(sum/smoothBy * 100)/100;
    }

    return smoothedData;
  }

  private createChart() {
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

    
    this.svg = d3.select(this.el.nativeElement).select('.linechart-container').append('svg')
      .attr("class", "plot")
      .attr('width', this.width + this.margin.left + this.margin.right)
      .attr('height', this.height + this.margin.top + this.margin.bottom)
      .append('g')
      .attr('transform', 'translate(' + this.margin.left + ',' + this.margin.top + ')');
  }
  
  private createScales() {
    // X scale
    let min_time = this.getMinTime(this.allData[0]);
    let max_time = this.getMaxTime(this.allData[0]);
  
    this.xScale = d3.scaleTime()
      .domain([new Date(this.startDate.getTime() - 2 * 60 * 60 * 1000), new Date(this.endDate.getTime() - 2 * 60 * 60 * 1000)] as [Date, Date])
      .range([0, this.width]);
  
    // Y scale
    let globalMinValue = Infinity;
    let globalMaxValue = -Infinity;

    this.allData.forEach(data => {
      let currentMin = d3.min(data, d => d.value - 5);
      let currentMax = d3.max(data, d => d.value + 5);
      globalMinValue = Math.min(globalMinValue, currentMin != undefined ? currentMin : Infinity)
      globalMaxValue = Math.max(globalMaxValue, currentMax != undefined ? currentMax : -Infinity)
    });

    this.yScale = d3.scaleLinear()
      .domain([
        globalMinValue,
        globalMaxValue
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
      .attr("stroke-dashoffset", this.totalLength)
      .transition()
      .duration(2000)
      .ease(d3.easeSinInOut)
      .attr("stroke-dashoffset", 0)
      .attr("data-old-length", this.totalLength);
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
      .text(this.labels.xAxis);
  
    // Y-axis label
    this.svg.append("text")
      .attr("class", "y label")
      .attr("text-anchor", "end")
      .attr("y", 6)
      .attr("dy", "0.5em")
      .attr("dx", "1.5em")
      .text(this.labels.yAxis);
  }
  
  private addTitle() {
    // Chart title
    this.svg.append("text")
      .attr("class", "chartTitle")
      .attr("x", this.width / 2)
      .attr("y", -20)
      .attr("text-anchor", "middle")
      .text(this.chartTitle);
  }
  
  private addLegend() {
    // Add the legend
    let legend = this.svg.selectAll(".legend")
      .data(this.legends)
      .enter().append("g")
      .attr("class", "legend")
      .attr("transform", (d: any, i: number) => "translate(0," + (i-0.5) * 20 + ")");
  
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
      .attr("font-family", "monospace")
      .text((d: any) => d);
  }
  
  private addTooltip() {
    this.tooltip = d3.select(this.el.nativeElement).select('.linechart-container').append("div")
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
        const distance = Math.abs(this.yScale(d.value) - d3.pointer(event)[1]);
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

    // Assuming 'circle' is the D3 selection of the circle being hovered over
    let circlePosition = circle.node().getBoundingClientRect();

    // Adjust for scroll
    let scrollX = window.scrollX || window.pageXOffset;
    let scrollY = window.scrollY || window.pageYOffset;

    // Setting tooltip position
    let tooltipX = circlePosition.left + circlePosition.width + 20 + scrollX; // 10px gap to the right of the circle
    let tooltipY = circlePosition.top + scrollY;
    /*const container = d3.select(this.el.nativeElement).select('.linechart-container').node();
      if (container instanceof Element) {
        tooltipX =  container.getBoundingClientRect().left + circlePosition.width + 20 + scrollX;
      }
    console.log("ToolTIP XXXX" + tooltipX);*/

    this.tooltip.style("left", tooltipX + "px").style("top", tooltipY + "px");
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
    let min_time = this.getMinTime(this.allData[0]);
    let max_time = this.getMaxTime(this.allData[0]);

    //let currentTime = new Date(2023, 7, 9, 23, 51);
  
    this.xScale.domain([new Date(this.startDate.getTime() - 2 * 60 * 60 * 1000), new Date(this.endDate.getTime() - 2 * 60 * 60 * 1000)] as [Date, Date])

    let globalMinValue = Infinity;
    let globalMaxValue = -Infinity;

    this.allData.forEach(data => {
      let currentMin = d3.min(data, d => d.value - 5);
      let currentMax = d3.max(data, d => d.value + 5);
      globalMinValue = Math.min(globalMinValue, currentMin != undefined ? currentMin : Infinity)
      globalMaxValue = Math.max(globalMaxValue, currentMax != undefined ? currentMax : -Infinity)
    });

    // Update Y scale
    this.yScale.domain([
      globalMinValue,
      globalMaxValue
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


    // Update each line based on its corresponding dataset
    let lines = this.svg.selectAll(".chart.line");

    this.allData.forEach((dataset, index) => {
      let lineElement = lines.filter(function(d: any, i: number) {
        return i === index;
      });

      // Define the line
      let valueline = d3.line<{ date: Date, value: number }>()
        .x(d => this.xScale(d.date))
        .y(d => this.yScale(d.value))
        .curve(d3.curveMonotoneX);

      lineElement.datum(dataset)
        .transition("line")
        .attr("d", valueline);
    
        
      // Update total length
      let totalLength = lineElement.node().getTotalLength();
      
      let oldLength = lineElement.attr("data-old-length");

      // Animate line drawing
      lineElement.attr("stroke-dasharray", totalLength + " " + totalLength)
        .attr("stroke-dashoffset", totalLength - oldLength)
        .transition()
        .duration(2000)
        .ease(d3.easeLinear)
        .attr("stroke-dashoffset", 0)
        .attr("data-old-length", totalLength);
    });
  
  }   
}