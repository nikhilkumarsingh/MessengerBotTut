from flask import Flask, request
from pymessenger import Bot
from utils import fetch_reply, news_categories, HELP_MSG
import requests,json
import os

app = Flask("My news bot")


FB_ACCESS_TOKEN = os.environ.get('FB_ACCESS_TOKEN')
bot = Bot(FB_ACCESS_TOKEN)


@app.route('/', methods=['GET'])
def verify():
	if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
		if not request.args.get("hub.verify_token") == os.environ.get('VERIFICATION_TOKEN'):
			return "Verification token mismatch", 403
		return request.args["hub.challenge"], 200
	return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():
	print(request.data)
	data = request.get_json()

	if data['object'] == "page":
		entries = data['entry']

		for entry in entries:
			messaging = entry['messaging']

			for messaging_event in messaging:

				sender_id = messaging_event['sender']['id']
				recipient_id = messaging_event['recipient']['id']

				if messaging_event.get('message'):
					# HANDLE NORMAL MESSAGES HERE

					if messaging_event['message'].get('text'):
						# HANDLE TEXT MESSAGES

						query = messaging_event['message']['text']

						if messaging_event['message'].get('quick_reply'):
							# HANDLE TEXT MESSAGE WITH QUICK REPLY
							payload = messaging_event['message']['quick_reply']['payload']
							if payload in list(zip(*news_categories))[1]:
								query = payload

						reply = fetch_reply(query, sender_id)
				
						if reply['type'] == 'news':
							bot.send_generic_message(sender_id, reply['data'])

						elif reply['type'] == 'none':
							bot.send_button_message(sender_id, "Sorry, I didn't understand. :(", reply['data'])

						else:
							bot.send_text_message(sender_id, reply['data'])					

						
				elif messaging_event.get('postback'):
					# HANDLE POSTBACKS HERE
					payload = messaging_event['postback']['payload']
					if payload ==  'SHOW_HELP':
						bot.send_quickreply(sender_id, HELP_MSG, news_categories)


	return "ok", 200


def set_greeting_text():
	headers = {
		'Content-Type':'application/json'
		}
	data = {
		"setting_type":"greeting",
		"greeting":{
			"text":"Hi {{user_first_name}}! I am news bot"
			}
		}
	ENDPOINT = "https://graph.facebook.com/v2.8/me/thread_settings?access_token=%s"%(FB_ACCESS_TOKEN)
	r = requests.post(ENDPOINT, headers = headers, data = json.dumps(data))
	print(r.content)


def set_persistent_menu():
	headers = {
		'Content-Type':'application/json'
		}
	data = {
		"setting_type":"call_to_actions",
		"thread_state" : "existing_thread",
		"call_to_actions":[
			{
				"type":"web_url",
				"title":"Meet the developer",
				"url":"https://fb.me/nikhilksingh97" 
			},
			{
				"type":"postback",
				"title":"Help",
				"payload":"SHOW_HELP"
			}]
		}
	ENDPOINT = "https://graph.facebook.com/v2.8/me/thread_settings?access_token=%s"%(FB_ACCESS_TOKEN)
	r = requests.post(ENDPOINT, headers = headers, data = json.dumps(data))
	print(r.content)


# set_persistent_menu()
# set_greeting_text()

if __name__ == "__main__":
	app.run(port=8000, use_reloader = True)