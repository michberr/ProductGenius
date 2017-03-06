from model import User
from model import connect_to_db, db
import json


#################### Functions to format data for javascript #################

def get_chart_data(score_list):
    """Construct data dictionary to create histogram with chart.js."""

    data_dict = {
        "labels": ["1", "2", "3", "4", "5"],
        "datasets": [{
            "label": "Buyer Ratings",
            "data": score_list,
            "backgroundColor": 'rgba(96, 4, 122, 0.6)',
            "hoverBackgroundColor": 'rgba(96, 4, 122, 1)',
            "borderWidth": 5
        }]
    }

    return data_dict

def format_reviews_to_dicts(reviews, user_id):
    """Format a list of review tuples into a list of dictionaries.

       This list will be sent to the front-end via json
    """

    # When constructing the list of review dictionaries, we could
    # query the database everytime to see if the review is the user's
    # favorite. To be more efficient, I extracted all of the user's
    # favorite reviews as a set of their id's, so that lookup time is
    # constant when constructing the list of dictionaries.
    favorite_review_ids = set()

    if user_id:
        user = User.query.get(user_id)
        favorite_review_ids = user.get_favorite_review_ids()

    rev_dict_list = []

    for review_id, review, asin, score, summary, time, _, _ in reviews:
        rev_dict = {}
        rev_dict["review_id"] = review_id
        rev_dict["review"] = review
        rev_dict["summary"] = summary
        rev_dict["score"] = score
        rev_dict["time"] = time
        rev_dict["user"] = user_id       # Is user logged in?
        rev_dict["favorite"] = review_id in favorite_review_ids   # Boolean of whether review is favorited
        rev_dict_list.append(rev_dict)

    return rev_dict_list
