import { ViewEncapsulation } from '@angular/core';
import { Component, OnInit } from '@angular/core';
import * as d3 from 'd3';
import { HttpClient } from '@angular/common/http';
import { interval } from 'rxjs';
import { startWith, switchMap } from 'rxjs/operators';

@Component({
  selector: 'app-help',
  templateUrl: './help.component.html',
  styleUrls: ['./help.component.css'],
  encapsulation: ViewEncapsulation.None
})

export class HelpComponent implements OnInit {
  private data: any[] = [];

  constructor(private http: HttpClient) { }

  ngOnInit() {  
    interval(50000).pipe(
      startWith(0),  // So that it fetches immediately
      switchMap(() => this.http.get('http://213.67.132.100:7777/temp_indoor_c/get/all'))
    ).subscribe((res: any) => {
      this.data = res.Response.map((d: [string, number]) => ({date: new Date(d[0]), value: d[1]}));
      this.data.reverse();
      this.createChart();
    });

    
  }

  createChart() {
    d3.select('body').html("");

    this.data = this.data.map((d, i) => ({id: i, date: new Date(d.date), value: d.value}))

    // Define the colors for the legend
    let colors = ["#0d6efd", "#198754", "#ab2e3c"];
  
    // Define the labels for the legend
    let labels = ["Data 1", "Data 2", "Data 3"];

    // Filter the labels and colors to only include the first 2
    labels = labels.slice(0, 1);
    colors = colors.slice(0, 1);

    let margin = {top: 50, right: 40, bottom: 60, left: 60};
    let width = 960 - margin.left - margin.right;
    let height = 500 - margin.top - margin.bottom;

    let xScale = d3.scaleTime()
      .domain(d3.extent(this.data, d => d.date) as [Date, Date])
      .range([0, width]);

    let yScale = d3.scaleLinear()
      .domain([Math.min(0, d3.min(this.data, d => d.value)), Math.max(0, d3.max(this.data, d => d.value))] as [Number, Number])
      .range([height, 0]);

    // Define the line
    let valueline = d3.line<{ date: Date, value: number }>()
      .x(d => xScale(d.date))
      .y(d => yScale(d.value))
      .curve(d3.curveMonotoneX);

    let svg = d3.select('body').append('svg')
      .attr("class", "plot")
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

    svg.append("defs")
      .append("filter")
      .attr("id", "glow")
      .append("feGaussianBlur")
      .attr("stdDeviation", "3")
      .attr("result", "coloredBlur");
    
    let feMerge = svg.select("#glow")
      .append("feMerge");
    
    feMerge.append("feMergeNode")
      .attr("in", "coloredBlur");
    feMerge.append("feMergeNode")
      .attr("in", "SourceGraphic");

    // Add a path for the line chart
    let line = svg.append("path")
      .datum(this.data)
      .attr("class", "chart line")
      .attr('fill', 'none')
      .attr('stroke', colors[0])
      .attr('stroke-width', 2)
      .attr('d', valueline)
      .style("filter", "url(#glow)");

    // Add the animation
    let totalLength = (line.node() as SVGPathElement).getTotalLength();

    line.attr("stroke-dasharray", totalLength + " " + totalLength)
      .attr("stroke-dashoffset", totalLength)
      .transition()
      .duration(2000)
      .attr("stroke-dashoffset", 0);

    // X-axis
    let xAxisG = svg.append("g")
      .attr("class", "axis axis--x")  // Add class to the x-axis
      .attr("transform", "translate(0," + height + ")")
      .call(d3.axisBottom(xScale).ticks(5).tickPadding(10).tickSize(10));

    // Y-axis
    let yAxisG = svg.append("g")
      .attr("class", "axis axis--y")  // Add class to the y-axis
      .call(d3.axisLeft(yScale)
      .ticks(5)
      .tickPadding(10)
      .tickSize(10));

    // X-axis label
    svg.append("text")
      .attr("class", "x label")
      .attr("text-anchor", "end")
      .attr("x", width)
      .attr("y", height - 6)
      .text("Date");

    // Y-axis label
    svg.append("text")
      .attr("class", "y label")
      .attr("text-anchor", "end")
      .attr("y", 6)
      .attr("dy", ".75em")
      .attr("transform", "rotate(-90)")
      .text("Value");

    // Chart title
    svg.append("text")
      .attr("class", "chartTitle")
      .attr("x", width / 2)
      .attr("y", -20)
      .attr("text-anchor", "middle")
      .text("Chart Title");

    // Add the legend
    let legend = svg.selectAll(".legend")
      .data(labels)
      .enter().append("g")
      .attr("class", "legend")
      .attr("transform", (d, i) => "translate(0," + i * 20 + ")");

    // Add the colored rectangles
    legend.append("line")
      .attr("x1", 110)
      .attr("x2", 130)
      .attr("y1", -25)
      .attr("y2", -25)
      .attr("stroke", (d, i) => colors[i])
      .attr("stroke-width", 3);

    // Add the labels
    legend.append("text")
      .attr("x", 100)
      .attr("y", -25)
      .attr("dy", ".35em")
      .style("text-anchor", "end")
      .text(d => d);

    let tooltip = d3.select("body").append("div")
      .attr("class", "tooltip")
      .style("opacity", 0);

    // Visible dot
    svg.selectAll(".dot")
      .data(this.data)
      .enter().append("circle")
      .attr("class", d => `dot dot-${(d as {id: number, date: Date, value: number}).id}`)  // Assign a unique class to each dot
      .attr("cx", d => xScale(d.date))
      .attr("cy", d => yScale(d.value))
      .attr("r", 0)

    // Invisible hover dot
    svg.selectAll(".dot-hover")
      .data(this.data)
      .enter().append("circle")
      .attr("class", "dot-hover")
      .attr("cx", d => xScale(d.date))
      .attr("cy", d => yScale(d.value))
      .attr("r", 30)  // Set a larger radius for the hover area
      .style("opacity", 0)  // Make the circle invisible
      // Attach the mouseover and mouseout events to these circles
      .on("mouseover", (event, d) => {
        d3.select(`.dot-${(d as {id: number, date: Date, value: number}).id}`).transition()
        .duration(200)
        .attr("r", 5);
        let data = d as {date: Date, value: number};
        tooltip.transition()
          .duration(200)
          .style("opacity", .9);
        tooltip.html("Date: " + data.date.getFullYear() + "/" + data.date.getMonth() + 1 + "/" + data.date.getDate() + 
        " " + data.date.getHours() + ":" + data.date.getMinutes() + ":" + data.date.getSeconds() +
        "<br/>Value: " + data.value);
        let node = tooltip.node()
        if(node === null){
          return
        }
        
        let tooltipBox = node.getBoundingClientRect();
        tooltip.style("left", (margin.left + xScale(data.date) + 35) + "px")
          .style("top", (yScale(data.value) + tooltipBox.height/2) + "px");
      })
      
      .on("mouseout", (event, d) => {
        d3.select(`.dot-${(d as {id: number, date: Date, value: number}).id}`).transition()
        .duration(350)
        .attr("r", 0);

        tooltip.transition()
          .duration(500)
          .style("opacity", 0);
      });
  }

}
