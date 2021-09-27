from flask import Flask, request
from tweepy import OAuthHandler, API
from twilio.twiml.messaging_response import MessagingResponse
import requests
import datetime
import os

app = Flask(__name__)

consumer_key = os.environ.get('CONSUMER_KEY')
consumer_secret = os.environ.get('CONSUMER_SECRET')
access_token = os.environ.get('ACCESS_TOKEN')
access_secret = os.environ.get('ACCESS_TOKEN_SECRET')

def authenticateCredentials():
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    api = API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    try:
        api.verify_credentials()
    except tweepy.TweepError as t:
        return "Error: Unable to connect to Twitter API this time. Please try again later!"
        # return t.response.text
    except tweepy.RateLimitError as r:
        return "Twitter API Rate Limit exceeded. Please wait for the desired timeout period and try again."
        # return r.response.text
    return api

def average_tweets(me: object):
    delta = (datetime.date.today()) - (me.created_at.date())
    daily_avg = '{:.2f}'.format(me.statuses_count/delta.days)
    return daily_avg

def account_period(me: object):
    delta = (datetime.date.today()) - (me.created_at.date())
    return delta.days

@app.route('/bot', methods=['POST'])
def bot():
    incoming_msg = request.values.get('Body', '').strip()
    resp = MessagingResponse()
    msg = resp.message()
    responded = False

    me = authenticateCredentials().me()

    if 'Hello' in incoming_msg:
        reply = ("Hello and welcome to the Twitter Counter Stats WhatsApp Bot!\n\n"
                "You can choose the below options to get your started:\n"
                "- Summary\n"
                "- User Lookup (Screen name)")
        msg.body(reply)
        responded = True
    
    if 'Summary' in incoming_msg:
        reply = "Screen Name: *{}*\n".format(me.screen_name)
        reply += "Account User ID: *{}*\n".format(me.id_str)
        reply += "Account Created On: *{}*\n".format(str(me.created_at))
        reply += "Statuses: *{}* tweets\n".format(statuses := "{:,}".format(me.statuses_count))
        reply += "Followers: *{}*\n".format(me.followers_count)
        reply += "Following: *{}*\n".format(me.friends_count)
        reply += "Favourites: *{}*\n".format(me.favourites_count)
        reply += "Account Age: *{}* days\n".format(account_period(me))
        reply += "Average: *{}* tweets per day".format(average_tweets(me))
        msg.body(reply)
        responded = True

    if not responded:
        msg.body('Sorry! Invalid option. You chose an invalid query option.')
    return str(resp)

if __name__ == '__main__':
    app.run()
