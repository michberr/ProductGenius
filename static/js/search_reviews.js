// AJAX call to search within a product's reviews and return the most relevant reviews

"use strict";

// Replace existing html with new html that contains 
// just reviews in user's search, with their query highlighted
function displayReviews(results) {

    var review_html = "";

    $.each(results, function(i, obj) {
        review_html += "<br><h3>" + obj.summary + "</h3>";

        // If there's a user logged in, display heart
        if (obj.user) {

          // If it's a favorited review, display red heart
          if (obj.favorite) {
            review_html += "<img src='/static/img/heart.png' class='heart' height='35' width='35' data-review-id=" + obj.review_id +">";
          } else {
            // Otherwise, display empty heart
            review_html += "<img src='/static/img/heart-empty.jpg' class='heart' height='35' width='35' data-review-id=" + obj.review_id +">";
          }
        }
        review_html += "<p class='score'>Score: " + obj.score + "</p>";
        review_html += "<p>" + obj.review + "</p><br><hr>";
    });

    // Update the reviews html
    $("#reviews").html(review_html);

    // Extract the value of the query and format it
    // so that it can be highlighted in the review
    var query = $("#query").val();
    query = query.trim();
    var words = query.split(' ');
    $("#reviews").highlight(words);

    // Must add event handler to new heart elements in DOM
    addHeartClicks();

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
