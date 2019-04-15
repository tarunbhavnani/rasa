from rasa_core.channels.facebook import FacebookInput
from rasa_core.agent import Agent
from rasa_core.interpreter import RegexInterpreter
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

input_channel = FacebookInput(
        fb_verify="rasa_check_tarun",
        # you need tell facebook this token, to confirm your URL
        fb_secret="54923c84f00be9c37fcdd82caabc03de",  # your app secret
        fb_access_token="EAAWvofdG0MABAJtr3Rx41WMnqm4q57i2ILNCHzeeCRKrc7h6Xb6DwUhTqXLtdyxZB19SX5joL9gFsWIGZCuAuBkLwj59QxDTCpUGyRdvjEACOsgAdUBZCU3TKVeXn4srZAlDnXFC764MQKeDyZBmpDVvYyWZBMxlVUzIowaIH4VwZDZD"
        # token for the page you subscribed to
        )

# set serve_forever=True if you want to keep the server running
agent.handle_channels([input_channel], 5004, serve_forever=True)