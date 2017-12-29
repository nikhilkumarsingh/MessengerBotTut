import apiai
import json
import requests
from pymongo import MongoClient

############################  MONGODB INTEGRATION #################################

# mongoDB client
MONGODB_URI = os.environ.get("MONGODB_URI")
client = MongoClient(MONGODB_URI)
db = client.get_database("News")
news_records = db.news_records

def getRECORDS(user_id):
	"""
	function to fetch all news searches of a user
	"""
	records = news_records.find({"sender_id":user_id})
	return records

def pushRECORD(record):
	"""
	function to push news record to collection
	"""
	news_records.insert_one(record)
####################################################################################

# api.ai client 
APIAI_ACCESS_TOKEN = "APIAI_ACCESS_TOKEN"
ai = apiai.ApiAI(APIAI_ACCESS_TOKEN)

# endpoint of the news API
GNEWS_API_ENDPOINT = "https://gnewsapi.herokuapp.com"

# available news categories
news_categories = [('sports', 'sports news'), ('political', 'political news'), ('business', 'business news'), 
				   ('top stories', 'top stories news'), ('world', 'world news'), ('national', 'national news'), 
					('technology', 'technology news'), ('entertainment', 'entertainment news')]

# a help message
HELP_MSG = """
Hey! I am NewsBot. 
I can provide you news from all around the world in different languages, on different topics! 
Try any of these categories. :)
"""



def get_news(params):
	"""
	function to fetch news from news API
	"""
	params['news'] = params.get('news', "top stories")
	resp = requests.get(GNEWS_API_ENDPOINT, params = params)
	return resp.json()


def apiai_response(query, session_id):
	"""
	function to fetch api.ai response
	"""
	request = ai.text_request()
	request.lang='en'
	request.session_id=session_id
	request.query = query
	response = request.getresponse()
	return json.loads(response.read().decode('utf8'))


def parse_response(response):
	"""
	function to parse response and 
	return intent and its parameters
	"""
	result = response['result']
	params = result.get('parameters')
	intent = result['metadata'].get('intentName')
	return intent, params

	
def fetch_reply(query, session_id):
	"""
	main function to fetch reply for chatbot and 
	return a reply dict with reply 'type' and 'data'
	"""
	response = apiai_response(query, session_id)
	print(response)
	intent, params = parse_response(response)

	reply = {}

	
	if response['result']['action'].startswith('smalltalk'):
		reply['type'] = 'smalltalk'
		reply['data'] = response['result']['fulfillment']['speech']
		
	elif intent == "show_news":
		reply['type'] = 'news'

		params['sender_id'] = session_id
		# push news search record to mongoDB
		pushRECORD(params)

		articles = get_news(params)

		# create generic template
		news_elements = []

		for article in articles:
			element = {}
			element['title'] = article['title']
			element['item_url'] = article['link']
			element['image_url'] = article['img']
			element['buttons'] = [{
				"type":"web_url",
				"title":"Read more",
				"url":article['link']}]
			news_elements.append(element)

		reply['data'] = news_elements
	else:
		reply['type'] = 'none'
		reply['data'] = [{"type":"postback",
						  "payload": "SHOW_HELP",
						  "title":"Click here for help!"}]

	return reply


