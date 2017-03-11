// Generates a jqCloud object from review keywords stored in db

"use strict";

var posWords = [];
var negWords = [];

// Weights correspond to size/importance of words
var weights = [13, 12, 10.5, 9.8, 9.4, 8, 7, 6, 5, 5];

for (var i=0; i < posKey.length; i++) {
    posWords[i] = {text: posKey[i], weight: weights[i]};
}

for (var i=0; i < negKey.length; i++) {
    negWords[i] = {text: negKey[i], weight: weights[i]};
}

// Use custom colors for negative keywords
var negColors = ["#F2671F", "#9C0F5F", "#9C0F5F", "#C91B26", "#60047A",
    "#60047A", "#160A47", "#160A47", "#160A47"];

// Creates jQCloud on page 
$('#positive-keywords').jQCloud(posWords,
    {width: 400, height: 250, center: {x:200, y:125}});

$('#negative-keywords').jQCloud(negWords,
    {width: 400, height: 250, center: {x:200, y:125}});

