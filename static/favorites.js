"use strict";

function favoriteReview(evt) {
    evt.preventDefault();

    var reviewID = $(this).data('review-id');

    var formInputs = {
        "reviewID": reviewID,
        "asin": asin
    };

    $.post("/favorite-review",
        formInputs,
        function(data) {

            console.log(data);

            if (data === "Unfavorited") {
                $("img[data-review-id=" + reviewID + "]").attr("src",
                    "/static/heart-empty.jpg");
            } else {
                var src = $("img[data-review-id=" + reviewID + "]").attr("src");
                $("img[data-review-id=" + reviewID + "]").attr("src",
                    "/static/heart.png");
            }
        });
}

// When user clicks on a heart, 
// make an AJAX call to add or remove review from favorites
$(".heart").on("click", favoriteReview);
