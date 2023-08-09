function _1(md){return(
md`# Input + Chart

Using [Inputs.range](https://github.com/observablehq/inputs/blob/main/README.md#range) and [Plot](/@observablehq/plot).`
)}

function _data(FileAttachment){return(
FileAttachment("penguins.csv").csv({typed: true})
)}

function _bins(Inputs){return(
Inputs.range([3, 20], {step: 1, label: "Bins"})
)}

function _4(Plot,aapl,bins){return(
Plot.plot({
  marks: [
    Plot.ruleY([0]),
    Plot.lineY(aapl, Plot.windowY({x: "Date", y: "Close", k: bins, reduce: "mean"}))
  ]
})
)}

export default function define(runtime, observer) {
  const main = runtime.module();
  function toString() { return this.url; }
  const fileAttachments = new Map([
    ["penguins.csv", {url: new URL("./files/715db1223e067f00500780077febc6cebbdd90c151d3d78317c802732252052ab0e367039872ab9c77d6ef99e5f55a0724b35ddc898a1c99cb14c31a379af80a.csv", import.meta.url), mimeType: "text/csv", toString}]
  ]);
  main.builtin("FileAttachment", runtime.fileAttachments(name => fileAttachments.get(name)));
  main.variable(observer()).define(["md"], _1);
  main.variable(observer("data")).define("data", ["FileAttachment"], _data);
  main.variable(observer("viewof bins")).define("viewof bins", ["Inputs"], _bins);
  main.variable(observer("bins")).define("bins", ["Generators", "viewof bins"], (G, _) => G.input(_));
  main.variable(observer()).define(["Plot","aapl","bins"], _4);
  return main;
}
