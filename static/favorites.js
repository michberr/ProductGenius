"use strict";

// Updates whether the user favorited or unfavorited a review in the db
function favoriteReview(evt) {

    var reviewID = $(this).data('review-id');

    var formInputs = {
        "reviewID": reviewID,
        "asin": asin
    };

    $.post("/favorite-review",
        formInputs,
        function(status) {
            console.log(status);

            // status is a message from the server that takes the values of
            // "Unfavorited" or "Favorited"
            if (status === "Favorited") {
                $("img[data-review-id=" + reviewID + "]").attr("src",
                    "/static/heart.png");
            } else {
                $("img[data-review-id=" + reviewID + "]").attr("src",
                    "/static/heart-empty.jpg");
            }
        });
}


// Event handler for clicking on a heart
var addHeartClicks = function() {
    $(".heart").on("click", favoriteReview);
};

// Calls addHeartClicks when document loads
$(document).ready(addHeartClicks());
