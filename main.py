from flask import Flask, request
from tweepy import OAuthHandler, API
from twilio.twiml.messaging_response import MessagingResponse
import requests
import datetime
import os
import arrow

app = Flask(__name__)

DATETIME_FORMAT = 'YYYY-MM-DD HH:mm:ss ZZ'

consumer_key = os.environ.get('CONSUMER_KEY')
consumer_secret = os.environ.get('CONSUMER_SECRET')
access_token = os.environ.get('ACCESS_TOKEN')
access_secret = os.environ.get('ACCESS_TOKEN_SECRET')

def authenticateCredentials():
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    api = API(auth, wait_on_rate_limit=True)
    try:
        api.verify_credentials(include_entities=False, include_email=False)
    except tweepy.errors.Unauthorized as ue:
        return ue.response.text
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

    me = authenticateCredentials().verify_credentials(include_entities=False, include_email=False)
    
    if 'Hello' in incoming_msg:
        reply = ("Hello and welcome to the Twitter Counter Stats WhatsApp Bot!\n\n"
                "You can choose the below options to get you started:\n"
                "- Summary\n"
                "- Lookup (Screen name)")
        msg.body(reply)
        responded = True
    
    if 'Summary' in incoming_msg:
        reply = "Screen Name: *{}*\n".format(me.screen_name)
        reply += "Account User ID: *{}*\n".format(me.id_str)
        fmt_dt = arrow.get(me.created_at.date()).format(DATETIME_FORMAT)
        reply += "Created On: *{}*\n".format(str(fmt_dt))
        reply += "Statuses: *{}* tweets\n".format(statuses := "{:,}".format(me.statuses_count))
        reply += "Followers: *{}*\n".format(me.followers_count)
        reply += "Following: *{}*\n".format(me.friends_count)
        reply += "Favourites: *{}*\n".format(me.favourites_count)
        reply += "Account Age: *{}* days\n".format(account_period(me))
        reply += "Average: *{}* tweets per day".format(average_tweets(me))
        msg.body(reply)
        responded = True
    
    if incoming_msg.lower().startswith('lookup') and len(incoming_msg.split()) == 2:
        mention = (incoming_msg.split())[1]
        user = authenticateCredentials().get_user(screen_name=mention, include_entities=False)
        reply = "Name: *{}*\n".format(user.name)
        reply += "Is protected? *{}*\n".format("Yes" if (user.protected is True) else "No")
        reply += "Is verified? *{}*\n".format("Yes" if (user.verified is True) else "No")
        fmt_dt = arrow.get(user.created_at.date()).format(DATETIME_FORMAT)
        reply += "Created On: *{}*\n".format(str(fmt_dt))
        reply += "Statuses: *{}* tweets\n".format(statuses := "{:,}".format(user.statuses_count))
        reply += "Followers: *{}*\n".format(followers := "{:,}".format(user.followers_count))
        reply += "Following: *{}*\n".format(followings := "{:,}".format(user.friends_count))
        reply += "Favourites: *{}*\n".format(user.favourites_count)
        reply += "Account Age: *{}* days\n".format(account_period(user))
        reply += "Average: *{}* tweets per day (TPD)".format(average_tweets(user))
        msg.body(reply)
        responded = True

    if not responded:
        msg.body('Sorry! Invalid option. You chose an invalid query option.')
    return str(resp)

if __name__ == '__main__':
    app.run()
