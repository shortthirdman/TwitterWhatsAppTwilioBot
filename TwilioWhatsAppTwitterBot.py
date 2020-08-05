from flask import Flask, request
from tweepy import OAuthHandler, API
from twilio.twiml.messaging_response import MessagingResponse
import requests
import datetime

app = Flask(__name__)

consumer_key = "faihxPpmBp11xVJrNtf5tqekc"
consumer_secret = "BcRhLtrFrj2Mn7AAoKGcclT0JQ6qhSbUJI3A6VZE9xUpmFgB1f"
access_token = "55815908-VhllSfYNV6pp5KNXWu9V7gAoOKPg6Ch8KoUHMU5cg"
access_secret = "oBq0iSZH1n6WjnxeGgECr7XXZwe7ta2MGi2nYfTdrVMOC"

@app.route('/bot', methods=['POST'])
def bot():
    incoming_msg = request.values.get('Body', '')..strip().lower()
    resp = MessagingResponse()
    msg = resp.message()
    responded = False

    me = authenticateCredentials()

    if 'Start' in incoming_msg:
        reply = ("Hello and welcome to the Twitter Counter Stats WhatsApp Bot!\n\n"
                "You can choose the below options to get your started:\n"
                "- Overall tweets\n"
                "- Followers\n"
                "- Followings\n"
                "- Account age\n"
                "- Daily average\n"
                "- Last tweet status")
        msg.body(reply)
        responded = True

    if 'Tweets' in incoming_msg:
        statuses = "{:,}".format(me.statuses_count)
        reply = "Your total tweet status count stands at {}".format(statuses)
        msg.body(reply)
        responded = True

    if 'Followers' in incoming_msg:
        reply = "You have {} followers.".format(me.followers_count)
        msg.body(reply)
        responded = True

    if 'Followings' in incoming_msg:
        reply = "You follow **{}** accounts at the moment.".format(me.friends_count)
        msg.body(reply)
        responded = True

    if 'Account age' in incoming_msg:
        delta = datetime.date.today() - me.created_at.date()
        account_age = delta.days
        reply = "Your Twitter account is **{}** days old.".format(account_age)
        msg.body(reply)
        responded = True

    if 'Daily' in incoming_msg:
        daily_avg = '{:.2f}'.format(statuses/account_age)
        reply = "You tweet at an average of **{}** daily.".format(daily_avg)
        msg.body(reply)
        responded = True

    if 'Last tweet' in incoming_msg:
        last_status = ""
        reply = "Your last status update:\n **{}**".format(last_status)
        msg.body(reply)
        responded = True

    if me is None:
        reply =
        msg.body()
        responded = True

    if not responded:
        msg.body('Sorry! Invalid option. You chose an invalid query option.')
    return str(resp)

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
    return api.me()

if __name__ == '__main__':
    app.run()