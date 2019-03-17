import React, { Component } from 'react';
import "./App.css"
import "bootstrap"
import 'bootstrap/dist/css/bootstrap.css'

//  .././api.py run from root dir
// also run npm start

var d3 = require("d3");
var $ = require("jquery");
var log = "";

var diseases  = {};
var UPDATE_TIME = 5000;

class App extends Component {
  render() {
    return (
      
      <div class="container-fluid">
        <div class="row top-container">

          <div class="col-6 title-container">
            <h1 class="display-1">DOC</h1>
            <p class="lead">
              Where doctors get a second opinion and patients a more accurate diagnosis.
            </p>
          </div>

          <div class="col-6">
            {/* <div class="info-container">

              <MetricsGraphics
                chart_type='bar'
                title="Diagnosis"
                description="This graphic shows a time-series of downloads."
                data={[{ 'date': new Date('2014-11-01'), 'value': 12 }, { 'date': new Date('2014-11-02'), 'value': 18 }]}
                bar_width={20}
                bar_height={10}
                bar_orientation="horizontal"
              />
            </div> */}
          </div>
        </div>

        <div class="row middle-container">
          <div class="col-7 notes-container">
            <div id="sound-icon"></div>
            <textarea id="notes-text" placeholder="Notes...">

            </textarea>
          </div>
          <div class="col-5 log-container">
            <textarea id="transcript-text" placeholder="Transcript..." disabled>

            </textarea>
            <button id="record-button" type="button" class="btn btn-success">Start Recording</button>
          </div>
        </div>
        <div class="row bottom-container">
          <div class="col-2 doctor-container">
            <textarea id="doctor-text" placeholder="Doctor's diagnosis..." disabled>

            </textarea>
            <button id="toggle-button" type="button" class="btn btn-info">Patient Mode</button>
          </div>
          <div class="col-4 diagnosis-container">
            <textarea id="diagnosis-text" placeholder="Algorithm's diagnosis..." disabled>

            </textarea>
          </div>
          <div class="col-6 recommendations-container">
            <textarea id="rec-text" placeholder="Recommended questions..." disabled>

            </textarea>
          </div>
        </div>
        <div class="row">
          <div class="col-12">
            <div id="graph"></div>
          </div>
        </div> 
      </div>
    );
  }
}

var points = []
var data = {}

// //sort bars based on value
// data = data.sort(function (a, b) {
//   return d3.ascending(a.value, b.value);
// })

// const xAxis = "xAxis";
// const yAxis = "yAxis";
// const svg = d3n.createSVG();
// svg.append("g")
//   .attr("fill", "steelblue")
//   .selectAll("rect")
//   .data(data)
//   .join("rect")
//   .attr("x", x(0))
//   .attr("y", d => y(d.name))
//   .attr("width", d => x(d.value) - x(0))
//   .attr("height", y.bandwidth());
// svg.append("g")
//   .attr("fill", "white")
//   .attr("text-anchor", "end")
//   .style("font", "12px sans-serif")
//   .selectAll("text")
//   .data(data)
//   .join("text")
//   .attr("x", d => x(d.value) - 4)
//   .attr("y", d => y(d.name) + y.bandwidth() / 2)
//   .attr("dy", "0.35em")
//   .text(d => format(d.value));
// svg.append("g").call(xAxis);
// svg.append("g").call(yAxis);


$(document).ready(function() {
  //set up svg using margin conventions - we'll need plenty of room on the left for labels

  // tippy("#record-button", {
  //   content: "test", 
  //   onShow(instance) {
  //     instance.setContent(log);
  //   }
  // });

  // function radians(deg) { return deg * Math.PI / 180; };
  // function distributeAngles(me, total) { return me / total * 360;}

  // var soundcanvas = $("<canvas id='sound-canvas'></canvas>").get(0);
  // $("#sound-icon").append(soundcanvas);
  // var ctx = soundcanvas.getContext("2d");

  // var num_items = 200;
  // var radius = 100;
  // ctx.lineWidth = 2;
  // var particles = [];
  // var w = 10;
  // var h = 10;
  
  // // working out the angles 
  // for (var i = 0; i < num_items; i++) {
  //   var angle = radians(distributeAngles(i, num_items));
  //   particles[i] = {
  //     x: w / 2 + Math.cos(angle) * radius,
  //     y: h / 2 + Math.sin(angle) * radius,
  //     angle: angle
  //   }
  // }

  // setTimeout(function () {
  //   // ctx.background(0);
  //   for (var i = 0; i < num_items; i++) {
  //     var p = particles[i];
  //     var s = Mic.mapSound(i, num_items, 5, 100);
  //     // map to greyscale
  //     // ctx.strokeStyle = rgb(map(i, 0, num_items, 0, 255));

  //     var x2 = w / 2 + Math.cos(p.angle) * (s + radius);
  //     var y2 = h / 2 + Math.sin(p.angle) * (s + radius);
  //     ctx.beginPath();
  //     ctx.moveTo(p.x, p.y);
  //     ctx.lineTo(x2, y2);
  //     ctx.stroke();
  //     // ctx.line(p.x, p.y, x2, y2);
  //   } 
  // }, 100);

  setInterval(function () {
    $.get("http://127.0.0.1:5000/transcript", function(json) {
      var str = "";
      $.each(json, function(timestamp, text) {
        str += timestamp + "\t" + text;
      });
      $("#transcript-text").val(str);
    });

    $.get("http://127.0.0.1:5000/diseases", function(json) {
      points = [];
      var str = "";
      $.each(json, function (i, text) {
        str += text + "\n";
        if (data[text] === undefined) {
          data[text] = 1;
        } else {
          data[text] = data[text] + 1;
        }
        $.each(data, function (key, value) {
          points.push({ "name": key, "value": value });
        });
      });
      $("#diagnosis-text").val(str); 
    });

    $.get("http://127.0.0.1:5000/recommendations", function(json) {
      var str = "";
      $.each(json, function (index, text) {
        str += text + "\n";
      });
      $("#rec-text").val(str);
    });

    $.post("http://127.0.0.1:5000/sendnotes", $("#notes-text").val().length > 0 ? $("#notes-text").val() : "EMPTY");
    if ($("#toggle-button").text() === "Doctor Mode") {
      $.post("http://127.0.0.1:5000/senddiagnosis", $("#doctor-text").val().length > 0 ? $("#doctor-text").val() : "EMPTY");
    }

    var margin = {
      top: 15,
      right: 25,
      bottom: 15,
      left: 200
    };

    var width = 900 - margin.left - margin.right,
      height = 400 - margin.top - margin.bottom;

    $("#graph").empty();
    var svg = d3.select("#graph").append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
    var x = d3.scaleLinear()
      .range([0, width])
      .domain([0, d3.max(points, function (d) {
        return d.value;
      })]);

    var y = d3.scaleBand()
      .rangeRound([height, 0])
      .padding(0.1)
      .domain(points.map(function (d) {
        return d.name;
      }));

    //make y axis to show bar names
    var yAxis = d3.axisLeft()
      .scale(y)
      //no tick marks
      .tickSize(0);

    var gy = svg.append("g")
      .attr("class", "y axis")
      .call(yAxis)

    var bars = svg.selectAll(".bar")
      .data(points)
      .enter()
      .append("g")

    //append rects
    bars.append("rect")
      .attr("class", "bar")
      .attr("y", function (d) {
        return y(d.name);
      })
      .attr("height", y.bandwidth())
      .attr("x", 0)
      .attr("width", function (d) {
        return x(d.value);
      });

    //add a value label to the right of each bar
    bars.append("text")
      .attr("class", "label")
      //y position of the label is halfway down the bar
      .attr("y", function (d) {
        return y(d.name) + y.bandwidth() / 2 + 4;
      })
      //x position is 3 pixels to the right of the bar
      .attr("x", function (d) {
        return x(d.value) + 3;
      })
      .text(function (d) {
        return d.value;
      });
  }, UPDATE_TIME);
  

  $("#record-button").on("click", function () {
    $(this).toggleClass("btn-danger");
    $(this).toggleClass("btn-success");
    if ($(this).text() === "Start Recording") {
      $(this).text("Stop Recording");
      $.get("http://127.0.0.1:5000/starttrans");
    } else if ($(this).text() === "Stop Recording") {
      $(this).text("Start Recording");
      $.get("http://127.0.0.1:5000/stoptrans");
     }
  });

  $("#toggle-button").on("click", function () {
    $(this).toggleClass("btn-secondary");
    $(this).toggleClass("btn-info");
    if ($(this).text() === "Patient Mode") {
      $(this).text("Doctor Mode");
      $("#doctor-text").prop("disabled", false);
    } else if ($(this).text() === "Doctor Mode") {
      $(this).text("Patient Mode");
      $("#doctor-text").prop("disabled", true);
    }
  });

  $(function () {
    $('[data-toggle="popover"]').popover();
  });
});


export default App;
