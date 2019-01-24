from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging
import warnings

logger = logging.getLogger(__name__)
#os.chdir('/home/tarun.bhavnani@dev.smecorner.com/Desktop/latest_bot/latest_bot/interview')

from rasa_nlu.training_data import load_data
from rasa_nlu import config
from rasa_nlu.model import Trainer
from rasa_nlu.model import Metadata, Interpreter
import json

import logging
import rasa_core
from rasa_core import utils
from rasa_core.agent import Agent
from rasa_core.train import online
from rasa_core.policies.keras_policy import KerasPolicy
from rasa_core.policies.memoization import MemoizationPolicy
from rasa_core.policies.fallback import FallbackPolicy

from rasa_core.interpreter import RasaNLUInterpreter
from rasa_core.utils import EndpointConfig
from rasa_core.run import serve_application

logger = logging.getLogger(__name__)
fallback = FallbackPolicy(fallback_action_name="action_default_fallback",
                          core_threshold=0.3,
                          nlu_threshold=0.3)



#########################333
class RestaurantAPI(object):
    def search(self, info):
        return "papi's pizza place"



def train_nlu(data="data/nlu_data.md", configs="config.yml", model_dir="models/nlu"):
	training_data = load_data(data)
	trainer = Trainer(config.load(configs))
	trainer.train(training_data)
	model_directory = trainer.persist(model_dir, fixed_model_name = 'latest_nlu')
	
def train_dialogue(domain_file = 'domain.yml',
					model_path = './models/dialogue',
					training_data_file = './data/stories.md'):
					
	agent = Agent(domain_file, policies = [MemoizationPolicy(), KerasPolicy(), fallback])
	data = agent.load_data(training_data_file)	
	agent.train(
				data,
				epochs = 300,
				batch_size = 50,
				validation_split = 0.2)
				
	agent.persist(model_path)
	return agent
	
def run_bot(serve_forever=True):
	interpreter = RasaNLUInterpreter('./models/nlu/default/latest_nlu')
	action_endpoint = EndpointConfig(url="http://localhost:5055/webhook")
	agent = Agent.load('./models/dialogue', interpreter=interpreter, action_endpoint=action_endpoint)
	rasa_core.run.serve_application(agent ,channel='cmdline')
		
	return agent
	

def run_online(domain_file="domain.yml",training_data_file="data/stories.md"):
    interpreter = RasaNLUInterpreter('models/nlu/default/latest_nlu')
    action_endpoint = EndpointConfig(url="http://localhost:5055/webhook")						  
    agent = Agent(domain_file,
                  policies=[MemoizationPolicy(max_history=2), KerasPolicy(), fallback],
                  interpreter=interpreter,
				  action_endpoint=action_endpoint)
    				  
    data = agent.load_data(training_data_file)
    agent.train(data,
                       batch_size=50,
                       epochs=200,
                       max_training_samples=300)				   
    online.serve_agent(agent)
    return agent


###run bot!########################################################################
if __name__ == '__main__':
    utils.configure_colored_logging(loglevel="INFO")

    parser = argparse.ArgumentParser(
            description='starts the bot')

    parser.add_argument(
            'task',
            choices=["train-nlu", "train-dialogue", "run","run-online"],
            help="what the bot should do - e.g. run or train?")
    task = parser.parse_args().task

    # decide what to do based on first parameter of the script
    if task == "train-nlu":
        train_nlu()
    elif task == "train-dialogue":
        train_dialogue()
    elif task =="run":
        run_bot()
    elif task=="run-online":
      run_online()
        
    
#python bot.py train-nlu
#python bot.py train-dialogue
#python bot.py run
#python -m rasa_core.train --online -o models/dialogue -d domain.yml -s data/stories.md --endpoints endpoints.yml
        
        
