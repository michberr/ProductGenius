"use strict";

// Updates whether the user favorited or unfavorited a product in the db
function favoriteProduct(evt) {

    var formInputs = {
        "asin": asin
    };

    $.post("/favorite-product",
        formInputs,
        function(status) {

            // status is a message from the server that takes the values of
            // "Unfavorited" or "Favorited"
            if (status === "Favorited") {
                $("#product-fav-button").text("Favorited");
            } else {
                $("#product-fav-button").text("Add to favorites");
            }
        });
}

// Event handler for clicking on a prodct favorite button
var addProductFavoriteClicks = function() {
    $("#product-fav-button").on("click", favoriteProduct);
};


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
$(document).ready((addProductFavoriteClicks));
