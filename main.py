#!/usr/bin/env python

import requests
import praw
import re
import json

# optional $ char, all uppercase.
TICKER_REGEXP = "(?:\$?)[A-Z]{3,}"

def get_symbols():
    # let's put our symbols into a set for use later.
    symbols = set()
    # make a get request to get a list of symbols; we can use other APIs, but this one is convenient.
    # we'll use the requests library to get json conveniently
    res = requests.get("https://dumbstockapi.com/stock?exchanges=NYSE").json()
    # now loop over all the symbols our api gives us back
    for sym in res:
        # add the symbol to our set for use later
        symbols.add(sym['ticker'])
    return symbols

# get WSB comments as a FLAT list.
# we'll accept an argument, limit, to determine how many pages of comments we should fetch...
def get_comments(symbols, limit=25):
    wsb = praw.Reddit(
        client_id="CFkrN81YB0FwLQ",
        client_secret="4wUkEKlK-2Ile9DVlnWoiCg1kd5kyA",
        user_agent="does_not_matter"
    ).subreddit("wallstreetbets").hot(limit=limit)
    print("submissions: ")
    # interate over the limit
    comment_map = {}
    for submission in wsb:
        print(submission.title)
        # get the comments as a FLAT list.
        submission.comments.replace_more()
        for comment in submission.comments.list():
            # now we want to apply some regular expression to the comment body to determine if it mentions a NYSE ticker
            # since this is a toy script, i'm going to use a shitty regexp, which demonstrates the usage of regexp for our purposes
            print("comment: ", comment.body)
            matches = re.findall(TICKER_REGEXP, comment.body, re.MULTILINE)
            print(matches)
            for match in matches:
                # stuff our matches in
                if match in symbols:
                    comment_obj = {
                        'link': comment.permalink,
                        'body': comment.body,
                    }
                    if match in comment_map:
                        comment_map[match].append(comment_obj)
                    else:
                        comment_map[match] = [comment_obj]
    return comment_map


def main():
    print("processing wsb comments...")
    symbols = get_symbols()
    processed_comments = get_comments(symbols)
    print(processed_comments)
    with open('results.json', 'w') as file:
        json.dump(processed_comments, file)
    print("done")

# this incantation means our main() function gets called when this script is executed
if __name__ == "__main__":
    main()
