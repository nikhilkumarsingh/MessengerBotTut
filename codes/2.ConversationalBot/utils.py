import apiai
import json


# api.ai client 
APIAI_ACCESS_TOKEN = "APIAI_ACCESS_TOKEN"
ai = apiai.ApiAI(APIAI_ACCESS_TOKEN)


def apiai_response(query, session_id):
	"""
	function to fetch api.ai response
	"""
	request = ai.text_request()
	request.lang = 'en'
	request.session_id = session_id
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
	return a reply
	"""
	response = apiai_response(query, session_id)
	print(response)
	intent, params = parse_response(response)

	

	if response['result']['action'].startswith('smalltalk'):
		reply = response['result']['fulfillment']['speech']
	elif intent == "show_news":
		reply = "Ok, I will show you {} news!".format(params.get('news'))
	else:
		reply = "Sorry, I didn't understand!"
		
	return reply
