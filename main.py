import csv
import os
import re
from tweepy import API
from tweepy import Cursor
from tweepy import OAuthHandler
from cred import (ACCESS_TOKEN, ACCESS_SECRET,
                  CONSUMER_KEY, CONSUMER_SECRET)


# initialize the tweepy api
auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = API(auth, wait_on_rate_limit=True)


def tweet_replying_to(tweet_id, thread_ids=[]):
    tweet_reply = api.statuses_lookup(id_=[tweet_id])[0]
    replying_to = tweet_reply.in_reply_to_status_id_str
    while replying_to:
        thread_ids.append(replying_to)
        tweet_replying_to(replying_to)
        replying_to = False

    return list(set(thread_ids))


def get_original_author(tweet_id):
    """Get author of tweets"""
    aa = api.statuses_lookup(id_=[tweet_id])[0]
    user_name = aa.user.screen_name
    user_id = aa.user.id
    tweet_text = aa.text
    return user_name, user_id, tweet_text


def quoted_replies(tweet_id):
    """Get quoted replies"""
    name, original_starter_id, tweet_text = get_original_author(tweet_id)
    replies = [
        tweet for tweet in Cursor(
            api.search,
            q="url:" + tweet_id,
            timeout=99999999).items()]
    return replies


def get_media_url(tweet):
    """Function to get list of media urls"""
    result = [
        image['media_url']
        for image in tweet.entities['media']
        if 'media' in tweet.entities]
    return result


def output_csv(list_tweets, name, tweet_text, original_starter_id):
    """Function to output list of tweets to csv"""
    os.system(f"mkdir -p ./data/{name}")
    fname = re.sub('\\W+', '', tweet_text)
    with open(f"./data/{name}/{fname}.csv", "w+") as f:
        writer = csv.writer(f)
        title_row = ["user_id", "user", "text", "media"]
        writer.writerow(title_row)
        _ = [
            writer.writerow(
                [tweet.user.id, tweet.user.screen_name,
                 tweet.text, get_media_url(tweet)])
            for tweet in list_tweets
            if tweet.user.id != original_starter_id]


def get_replies_to(tweet_id):
    name, original_starter_id, tweet_text = get_original_author(tweet_id)
    replies = []
    for tweet in Cursor(api.search, q="to:" + name, timeout=9999999).items():
        if tweet.in_reply_to_status_id_str:
            if tweet.in_reply_to_status_id_str == tweet_id:
                replies.append(tweet)
    qrt_replies = quoted_replies(tweet_id) + replies
    print(f"\n\n\n\n Replies got {len(qrt_replies)}")
    output_csv(qrt_replies, name, tweet_text, original_starter_id)


def scrapper():
    start_id = str(input("enter start id of the last tweet in thread "))
    thread_ids = tweet_replying_to(start_id) + [start_id]
    for n, thread_id in enumerate(thread_ids):
        print(f"Id {n+1} of {len(thread_ids)}")
        get_replies_to(thread_id)


if __name__ == "__main__":
    scrapper()
