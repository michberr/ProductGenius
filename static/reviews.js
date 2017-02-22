"use strict";

// Replace existing html with new html that contains 
// just reviews in user search, with query highlighted
function displayReviews(results) {

    var review_html = "";

    $.each(results, function(rev_id, obj) {
        review_html += "<h3>" + obj.summary + "</h3>";
        review_html += "<ul>";
        review_html += "<li>Score:" + obj.score + "</li>";
        review_html += "<li>" + obj.review + "</li>";
        review_html += "</ul>";
    });

    $("#reviews").html(review_html);

    // Highlight the word in the review
    $('li').highlight('bass');

}

function getReviewsFromSearch(evt) {
  evt.preventDefault();

  var formInputs = {
    "query": $("#query").val()
  };

  $.get("/search-review/" + asin + ".json",
        formInputs,
        displayReviews);
}

// When user searches, make an AJAX call to retrieve matching reviews
$("#review-search-form").on("submit", getReviewsFromSearch);
