"use strict";

var posWords = [];
var negWords = [];
var weights = [13, 12, 10.5, 9.8, 9.4, 8, 7, 6, 5, 5];

for (var i=0; i < posKey.length; i++) {
    posWords[i] = {text: posKey[i], weight: weights[i]};
}

for (var i=0; i < negKey.length; i++) {
    negWords[i] = {text: negKey[i], weight: weights[i]};
}

var negColors = ["#F2671F", "#9C0F5F", "#9C0F5F", "#C91B26", "#60047A", "#60047A", "#160A47", "#160A47", "#160A47"];

$('#positive-keywords').jQCloud(posWords, {width: 400, height: 250, center: {x:200, y:125}});
$('#negative-keywords').jQCloud(negWords, {width: 400, height: 250, center: {x:200, y:125}});

/*orange : F2671F;
red: C91B26;

magenta: 9C0F5F;
light purple: 60047A;
dark purple: 160A47;*/