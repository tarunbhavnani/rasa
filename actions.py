# -*- coding: utf-8 -*-
#exec('dispatcher.utter_template({}, tracker)'.format(a))
#eval('dispatcher.utter_template({}, tracker)'.format(a))


"""ReadMe: here all the questions are in ActionQuestionCounter. at each step this is called and depending on the counter value it puts a question 
and pulls the required to extract the answer. This action also updates the counter for the next question!!""" 
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import requests
import json
from rasa_core_sdk import Action
from rasa_core_sdk.events import SlotSet
from rasa_core_sdk.forms import FormAction
#from rasa_core.events import UserUtteranceReverted
from rasa_core_sdk.events import UserUtteranceReverted
import pandas as pd
import xlrd

df = pd.read_excel('data_los.xlsx')
df_counter=pd.read_csv('df_counter.csv')


logger = logging.getLogger(__name__)

class Actioninterviewstart(Action):
    def name(self):
        return 'action_interview_start'
    def run(self, dispatcher, tracker, domain):
        user_name = tracker.get_slot('user_name')
        user_cell=tracker.get_slot('user_cell')
        last_message= tracker.latest_message['text']
        counter=1
        #f len(df[df.applicant_1_phone==int(last_message)])>0:
        #   user_cell==last_message #or pluck user_cell out of last message!
        
        if (user_name!="Dear" and user_cell != "none"):
           dispatcher.utter_message("Please say {}!".format(user_name))
        else:
           n=0
           for i in last_message.split():
               if i in df['applicant_1_phone'].fillna(0).astype(int).astype(str).values.tolist():
                   user_cell=i
                   n+=1
                   if n>1:
                       dispatcher.utter_message("more than 1 cell identified!. Please provide only the registered cell number")
                       user_cell='none'
                       break

        
           if user_cell =="none":
               dispatcher.utter_message("Kindly input your interview reference id")
           else:
               try:
                 user_name=str(df[df.applicant_1_phone==int(user_cell)].last_name.item())
                 address=str(df[df.last_name==user_name].branch.item())
                 loan_requested=str(df[df.last_name==user_name].loan_requested.item())
                 org_name =str(df[df.last_name==user_name].company.item())
                 dispatcher.utter_message("Hello {}, we will start the PD discussion now!".format(user_name))
                 return[SlotSet('user_name', user_name),SlotSet('user_cell', user_cell),SlotSet('address', address),SlotSet('org_name', org_name),SlotSet('loan_requested', loan_requested),SlotSet('counter', counter)]
               except ValueError:
                 dispatcher.utter_message("Kindly check your refrence number, if it is {} then contact SMEhelp desk to reschedule the interview.".format(user_cell))
                 user_cell="none"
                 counter=0
                 return[SlotSet('user_name', user_name),SlotSet('user_cell', user_cell), SlotSet('counter', counter)]






class ActionAskFamily(Action):
    """All Family Questions"""

    def name(self):
        return "action_ask_family"

    def run(self, dispatcher, tracker, domain):
      counter= tracker.get_slot('counter')
      user_name = tracker.get_slot('user_name')
      
      message= df_counter[df_counter['counter']==counter].ques.item()
      dispatcher.utter_message(message)
        
      return [SlotSet('counter', counter)]
        
class ActionSaveFamily(Action):

    def name(self):
        return "action_save_family"

    def run(self, dispatcher, tracker, domain):
        family_stay=tracker.get_slot('family_stay')
        family_house_own=tracker.get_slot('family_house_own')
        family_members=tracker.get_slot('family_members')
        family_involve=tracker.get_slot('family_involve')
        family_involve_explain=tracker.get_slot('family_involve_explain')
        business_gist = tracker.get_slot('business_gist')
        business_office_location = tracker.get_slot('business_office_location')
        business_employees = tracker.get_slot('business_employees')
        business_premises = tracker.get_slot('business_premises')
        business_premises_duration = tracker.get_slot('business_premises_duration')
        business_duration = tracker.get_slot('business_duration')
        business_partner = tracker.get_slot('business_partner')
        business_pc_own = tracker.get_slot('business_pc_own')
        business_turnover_last = tracker.get_slot('business_turnover_last')
        business_turnover_now = tracker.get_slot('business_turnover_now')
        
         #the entity can be one of two entities from duckling,
         #number or amount-of-money
        counter= tracker.get_slot('counter')
        if counter==1:
          family_stay = next(tracker.get_latest_entity_values('location'), None)
          if not family_stay:
            family_stay = tracker.latest_message.get('text')
          counter=2
            #return [SlotSet('family_stay', family_stay), SlotSet('counter', counter)]   
        elif counter==2:
          intent = tracker.latest_message['intent'].get('name')
          family_house_own = tracker.latest_message.get('text')
          if intent in ['affirm', 'deny']:
            family_house_own=intent
          counter=3
            #return [SlotSet('family_house_own', family_house_own), SlotSet('counter', counter)]   
        elif counter==3:
          family_members = next(tracker.get_latest_entity_values('number'), None)
          if not family_members:
            family_members = tracker.latest_message.get('text')
          counter=4
            #return [SlotSet('family_members', family_members), SlotSet('counter', counter)]   
        elif counter==4:
          intent = tracker.latest_message['intent'].get('name')
          if intent =="affirm":
            family_involve=intent
            counter=5
            #return [SlotSet('family_involve', family_involve), SlotSet('counter', counter)]   
          elif intent=="deny":
            family_involve=intent
            counter=6
            #return [SlotSet('family_involve', family_involve), SlotSet('counter', counter)]   
          else:
            family_involve = tracker.latest_message.get('text')
            counter=6
            #return [SlotSet('family_involve', family_involve), SlotSet('counter', counter)]   
        elif counter==5:
          family_involve_explain=tracker.latest_message.get('text')
          counter=6
          #return [SlotSet('family_involve_explain', family_involve_explain), SlotSet('counter', counter)]   
        elif counter==6:
          business_gist= tracker.latest_message.get('text')
          counter=7
        
        elif counter==7:
          business_office_location= next(tracker.get_latest_entity_values('location'), None)
          if not business_office_location:
            business_office_location = tracker.latest_message.get('text')
          counter=8
        elif counter==8:
          business_employees = next(tracker.get_latest_entity_values('number'), None)
          if not business_employees:
            business_employees = tracker.latest_message.get('text')
          counter=9
        elif counter==9:
          intent = tracker.latest_message['intent'].get('name')
          if intent =="deny":
            business_premises =intent
            counter=10
          elif intent == "affirm":
            business_premises =intent
            counter=10
          else:
            business_premises= tracker.latest_message.get("text")
            counter=10
            
        elif counter==10:
          business_premises_duration=tracker.latest_message.get("text")
          counter=11
        
        elif counter==11:
          business_duration=tracker.latest_message.get("text")
          counter=12
          
        elif counter==12:
          intent = tracker.latest_message['intent'].get('name')
          if intent =="affirm":
            business_partner=intent
            counter=13
            #return [SlotSet('family_involve', family_involve), SlotSet('counter', counter)]   
          elif intent=="deny":
            business_partner=intent
            counter=14
            #return [SlotSet('family_involve', family_involve), SlotSet('counter', counter)]   
          else:
            business_partner = tracker.latest_message.get('text')
            counter=14
            
        elif counter==13:
          business_pc_own = next(tracker.get_latest_entity_values('number'), None)
          if not business_pc_own:
            business_pc_own = tracker.latest_message.get('text')
          counter=14
        elif counter==14:
          business_turnover_last=next(tracker.get_latest_entity_values('number'), None)
          if not business_turnover_last:
            business_turnover_last= tracker.latest_message.get('text')
          counter=15
        elif counter==15:
          business_turnover_now=next(tracker.get_latest_entity_values('number'), None)
          if not business_turnover_now:
            business_turnover_now= tracker.latest_message.get('text')
          counter=999
          
        
        else:
          dispatcher.utter_message("Thanks!tc!")
        return [SlotSet('family_stay', family_stay),
                SlotSet('family_house_own', family_house_own),
                SlotSet('family_members', family_members),
                SlotSet('family_involve', family_involve),
                SlotSet('family_involve_explain', family_involve_explain),
                SlotSet('business_gist', business_gist),
                SlotSet('business_office_location', business_office_location),
                SlotSet('business_employees', business_employees),
                SlotSet('business_premises', business_premises),
                #SlotSet('business_premises_duration', business_premises),
                SlotSet('business_premises_duration', business_premises_duration),
                SlotSet('business_duration', business_duration),
                SlotSet('business_partner', business_partner),
                SlotSet('business_pc_own', business_pc_own),
                SlotSet('business_turnover_last', business_turnover_last),
                SlotSet('business_turnover_now', business_turnover_now),
                SlotSet('counter', counter)]    
          
        

        
        
        
        
        
        
        

        








