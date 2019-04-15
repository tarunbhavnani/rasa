#os.chdir('/home/tarun.bhavnani@dev.smecorner.com/Desktop/final_bot/final_bot2')
from rasa_core.channels.slack import SlackInput
from rasa_core.agent import Agent
from rasa_core.interpreter import RasaNLUInterpreter
import yaml
from rasa_core.utils import EndpointConfig
from rasa_core.tracker_store import MongoTrackerStore


nlu_interpreter = RasaNLUInterpreter('./models/nlu/default/latest_nlu')

core='./models/dialogue'

action_endpoint = EndpointConfig(url="http://localhost:5055/webhook")

db= MongoTrackerStore(domain="domain.yml",host='mongodb://localhost:27017', db='rasa', username="smeuser", 
			password="Al+erna+e",collection="conversations",event_broker=None)


agent = Agent.load(path=core, interpreter = nlu_interpreter, action_endpoint = action_endpoint,tracker_store=db)


#input_channel = SlackInput('xoxb-542065604356-542500977682-faR2rS0xAcTANpn4wAU8hAiF') #your bot user authentication token
input_channel = SlackInput('xoxb-token') #your bot user authentication token
agent.handle_channels([input_channel], 5004, serve_forever=True)
 
#https://c1b4869e.ngrok.io/webhooks/slack/webhook

#all these three run
# actions
# run_app
# ngrok server

#see all at
#https://towardsdatascience.com/building-a-conversational-chatbot-for-slack-using-rasa-and-python-part-2-ce7233f2e9e7

   #https://35d3861e.ngrok.io/webhooks/slack/webhook


#docker run -v $(pwd):/app/project -v $(pwd)/models/rasa_core:/app/models rasa/rasa_core:latest train --domain project/domain.yml --stories project/data/stories.md --out models
"""
   #fb: page-access-token: 
   EAAWvofdG0MABAJtr3Rx41WMnqm4q57i2ILNCHzeeCRKrc7h6Xb6DwUhTqXLtdyxZB19SX5joL9gFsWIGZCuAuBkLwj59QxDTCpUGyRdvjEACOsgAdUBZCU3TKVeXn4srZAlDnXFC764MQKeDyZBmpDVvYyWZBMxlVUzIowaIH4VwZDZD
   #app secret
   54923c84f00be9c37fcdd82caabc03de
   
"""
