"use strict";

// Replace existing html with new html that contains 
// just reviews in user's search, with their query highlighted
function displayReviews(results) {

    var review_html = "";

    $.each(results, function(i, obj) {
        review_html += "<h3>" + obj.summary + "</h3>";

        // If there's a user logged in, display heart
        if (obj.user) {

        console.log(obj.favorite);

          // If it's a favorited review, display red heart
          if (obj.favorite) {
            review_html += "<img src='/static/heart.png' class='heart' height='35' width='35' data-review-id=" + obj.review_id +">";
          } else {
            // Otherwise, display empty heart
            review_html += "<img src='/static/heart-empty.jpg' class='heart' height='35' width='35' data-review-id=" + obj.review_id +">";
          }
        }
        review_html += "<ul>";
        review_html += "<li>Score:" + obj.score + "</li>";
        review_html += "<li>" + obj.review + "</li>";
        review_html += "</ul>";

    });

    $("#reviews").html(review_html);

    // Highlight the word in the review
    var query = $("#query").val();
    $('li').highlight(query);

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
