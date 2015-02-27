var elementOfInterest;
$( document ).ready(function() {
$('#nodeForm').hide();
var width = 500,
    height = 500,
    radius = 15,
    fontSize = 15;

var force = d3.layout.force()
    .nodes(dataset.neurons)
    .links(dataset.edges)
    .size([width, height])
    .linkDistance(radius * 8)
    .charge(-300)
    .on("tick", tick)
    .start();

var svg = d3.select("#svgContainer").append("svg")
    .attr("width", width)
    .attr("height", height);

// Per-type markers, as they don't inherit styles.
svg.append("defs").selectAll("marker")
    .data(['connection'])
  .enter().append("marker")
    .attr("id", function(d) { return d; })
    .attr("viewBox", "0 -5 10 10")
    .attr("refX", 15)
    .attr("refY", -1.5)
    .attr("markerWidth", 10)
    .attr("markerHeight", 10)
    .attr("orient", "auto")
  .append("path")
    .attr("d", "M0,-5L10,0L0,5");

var path = svg.append("g").selectAll("path")
    .data(force.links())
  .enter().append("path")
  .attr('class', 'link')
  .attr('id', function(d,idx){
  	return('link' + idx)
  })
  .attr("marker-end", function(d) { return "url(#connection)"; });

var circle = svg.append("g").selectAll("circle")
    .data(force.nodes())
  .enter().append("circle")
    .attr("r", radius)
    .attr('id', function(d,idx){
    	return('node' + idx)
    })
    .on('click', function(){
    	elementOfInterest = this;
    	$('#nodeForm').show();
    	populateNodeForm(elementOfInterest);
    	console.log(elementOfInterest)
    })
    .call(force.drag);

var text = svg.append("g").selectAll("text")
    .data(force.nodes())
  .enter().append("text")
    .attr("x", 0)
    .attr("y", ".31em")
    .attr("text-anchor", "middle")
    .attr('id', function(d,idx){
    	return('node' + idx + 'text')
    })
    .text(function(d) { return d.name; });

var linkText = svg.append("g").selectAll("text")
    .data(force.links())
  .enter().append("text")
    .attr("x", 0)
    .attr("y", ".10em")
    .attr('dy', -5)
    //.attr("text-anchor", "middle")
    .append('textPath')
    .attr('startOffset', '45%')
    .attr("xlink:href",function(d,idx){
    	return('#link' + idx)
    })
    .attr("stroke","black")
    .text(function(d) { return d.weight; })
    ;

// Use elliptical arc path segments to doubly-encode directionality.
function tick() {
  path.attr("d", linkArc);
  circle.attr("transform", transform);
  text.attr("transform", transform);
}

function linkArc(d) {
  var dx = d.target.x - d.source.x,
      dy = d.target.y - d.source.y,
      dr = Math.sqrt(dx * dx + dy * dy);
  return "M" + d.source.x + "," + d.source.y + "A" + dr + "," + dr + " 0 0,1 " + d.target.x + "," + d.target.y;
}

function transform(d) {
  return "translate(" + d.x + "," + d.y + ")";
}
function populateNodeForm(el){
	var jqueryEl = $('#' + el.id);
	var textEl = $('#' + el.id + 'text');
	$('#nodeSizeValue').text(jqueryEl.attr('r'));
  $('#nodeFontSizeValue').text('10');
}
$("#nodeSize").change(function(){
  var jqueryEl = $('#' + elementOfInterest.id);
  jqueryEl.attr('r', $("#nodeSize").val());
  $('#nodeSizeValue').text($('#nodeSize').val());
});
$("#nodeColor").change(function(){
  var jqueryEl = $('#' + elementOfInterest.id);
  jqueryEl.css('fill', $("#nodeColor").val());
});
$("#nodeFontSize").change(function(){
  var jqueryEl = $('#' + elementOfInterest.id + "text");
  jqueryEl.css('font-size', $("#nodeFontSize").val() + "px");
  $('#nodeFontSizeValue').text($('#nodeFontSize').val());
});

});
