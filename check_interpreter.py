
import os
os.chdir("/home/tarun.bhavnani@dev.smecorner.com/Desktop/final_bot/final_bot4")


from rasa_core.agent import Agent
from rasa_core.interpreter import RasaNLUInterpreter
interpreter = RasaNLUInterpreter("./models/nlu/default/latest_nlu")

agent = Agent.load("./models/dialogue",interpreter=interpreter)


agent.is_ready()
text="bla"
text="12 yrs"
text="12 years"
text="in 12 august 2015 "
text="since 1989"
text="since 319896778"
text="since 13 months"
text="since august 2018"
text="200 yrs"
io=interpreter.parse(text)
for i in range(len(io['entities'])):
  if io['entities'][0]['entity']=='DATE':
    print(io['entities'][0]['value'])

agent.handle_text(text)
agent.predict_next(text)


digits=[i for i in re.findall('\d+', text )]

if date:
  x months
  x years
  x days
  x weaks
  extract and convert to months/years
  
otehrwise extract digits




