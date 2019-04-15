#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 30 10:37:42 2019

@author: tarun.bhavnani@dev.smecorner.com
"""

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
from rasa_core_sdk.events import ActionReverted
from rasa_core_sdk.events import FollowupAction
from rasa_core.interpreter import RasaNLUInterpreter
import pandas as pd
import xlrd
import re
from word2number import w2n
from word2number import w2n
import nltk
import spacy
nlp= spacy.load("en")

df = pd.read_excel('data_los.xlsx')
df_counter=pd.read_csv('df_counter.csv')
df_counter['ans']=""
df_slots=pd.read_csv("df_slots.csv")

def extract_names(text):
  text_nlp= nlp(text)
  text_nlp= [(i.text, i.tag_) for i in text_nlp]
  grammar = "NP: {<JJ>*<NN>+|<VB>*<NN>+}"
  grammar = "NP: {<NN>+}"
  cp = nltk.RegexpParser(grammar)
  names=[]
  result= cp.parse(text_nlp) 
  #print(result)
  for subtree in result.subtrees(filter=lambda t: t.label() == 'NP'):    
    name=""
    for i in range(len(subtree)):
      name=name+" "+subtree[i][0]
    names.append(name[1:])
  return(names)

def extract_number(text):
  date=[]
  digits=[i for i in re.findall('\d+', text )]
  intr = RasaNLUInterpreter("./models/nlu/default/latest_nlu")
  io=intr.parse(text)
  for i in range(len(io['entities'])):
    if io['entities'][i]['entity']=='DATE' or io['entities'][i]['entity']=="CARDINAL":
      date.append(io['entities'][i]['value'])

  return digits, date


extract_names("what are you doing in paris")

logger = logging.getLogger(__name__)


"""
precedence of events in action default
1) before interview start

2) after interview start
  - intent: if intents deserves a reaction, continue with current/counter as fit
  - if the question leeds to choices then we bifurcate according to choices in action default using current
  - if just digestion question then we follow with counter through action default
"""

class ActionDefaultFallback(Action):
    def name(self):
        #return "action_question_counter"
        return 'action_default_fallback'
    def run(self, dispatcher, tracker, domain):
        #text= tracker.latest_message['text']
        #interpreter = RasaNLUInterpreter('./models/nlu/default/latest_nlu')
        #last_intent=interpreter.parse(text)['intent_ranking'][0]
        
        counter= tracker.get_slot('counter')
        current=tracker.get_slot('current')
        bkind= tracker.get_slot("bkind")
        nob= tracker.get_slot("nob")
        industry=tracker.get_slot("industry")
        interview_state= tracker.get_slot("interview_state")
        last_intent= tracker.latest_message['intent'].get('name')
        
        last_message= tracker.latest_message['text']
        last_message= last_message.lower()
        user_name= tracker.get_slot("user_name")
        names=extract_names(last_message)
        
        
        digits=[i for i in re.findall('\d+', last_message )]
        
        #num= extract_number(last_message)
        date= next(tracker.get_latest_entity_values("DATE"), None)
        #dispatcher.utter_message("last entity is DATE:{}".format(date))
        cardinal= next(tracker.get_latest_entity_values("CARDINAL"), None)
        #dispatcher.utter_message("last entity is CARDINAL:{}".format(cardinal))
        
        #intr = RasaNLUInterpreter("./models/nlu/default/latest_nlu")
        #io=intr.parse(last_message)
        #for i in range(len(io['entities'])):
        #  if io['entities'][i]['entity']=='DATE' or io['entities'][i]['entity']=="CARDINAL":
        #    dispatcher.utter_message(io['entities'][i]['value'])

        #latest_ent= tracker.get_latest_entity_values("DATE")
        #dispatcher.utter_message(latest_ent)
        
        
        #dispatcher.utter_message(something)
        
        #dispatcher.utter_message(last_message)
        #dispatcher.utter_message(last_intent)
        #dispatcher.utter_message(current)
        #dispatcher.utter_message(counter)
        #dispatcher.utter_message("bkind is:{}".format(bkind))
        #dispatcher.utter_message("nob is:{}".format(nob))
        #dispatcher.utter_message(last_message)
        #dispatcher.utter_message("industry is:{}".format(industry))
        #dispatcher.utter_message(interview_state)
        #dispatcher.utter_message("digits:{}".format(digits))
        #dispatcher.utter_message("names:{}".format(names))
        #gh=tracker.get_latest_input_channel()
        #dispatcher.utter_message(gh)
        #hj=tracker.latest_action_name()
        #dispatcher.utter_message(hj)
 
        
        #before interview start
        #interview state turns to "started if details are fetched in action fetch details"
        
        if interview_state == "start":
          if last_intent=="greet":         
            dispatcher.utter_message("We will now proceed to start the PD. Enter 'stop' if you want to exit the interview at any time!")
            counter="action_interview_start"
            return[FollowupAction(counter)]
          elif counter !="action_interview_start":
            
            dispatcher.utter_message("To start kindly enter 'hi' ")
            counter="action_listen"
            return[FollowupAction(counter)]

        
        #interview starter
        if current==counter=="action_interview_start":
          counter="action_fetch_details"
          return[FollowupAction(counter)]
        
        
        #after interview start
        if interview_state=="started":
          
          
          #check for intents that are out of scope for interview!
          #in these we followup with the same question
          
          #blank reply
          
          if len(last_message)==0:
            dispatcher.utter_message("Please dont leave replies blank, ill ask again!!")
            return[FollowupAction(current)]
          
          #repeat
          
          if (last_intent=="repeat") or (last_message=="what"):
            dispatcher.utter_message("I will ask again!!")           
            return[FollowupAction(current)]
          
          #chitchat
          
          if last_intent=="chitchat":
            #dispatcher.utter_message("This is an interview, ill ask again!!")
            dispatcher.utter_template("utter_chitchat", tracker)
            return[FollowupAction(current)]
          
          
          #greet
          
          if last_intent=="greet":
            #dispatcher.utter_message("This is an interview, ill ask again!!")
            dispatcher.utter_template("utter_greet", tracker)
            return[FollowupAction(current)]        

          
          #thank
          
          if last_intent=="thank":
            dispatcher.utter_template("utter_thanks", tracker)
            return[FollowupAction(current)]
        
        
          #goodbye
          
          if last_intent=="goodbye":
            #dispatcher.utter_message("Goodbye {}".format(user_name))
            #counter="action_stop_check"
            return[FollowupAction("action_stop_check")]
        
        
          #stop
          
          if (last_message=="stop") or (last_intent=="stop"):
            #dispatcher.utter_message("Goodbye {}".format(user_name))
            #counter="action_stop_check"
            return[FollowupAction("action_stop_check")]
          
          
          
          #now we will look for currents and their followups
          #most;y followup are defined in the action itself and 
          #action default just follows up with tyhe counter specified.
          
          #we deal with current only incase the answer is not just digestion.
          #we parse the answer and set the counter in each case.
          
          
          #stop interview
          
          if current=="action_stop_check":
            if last_intent== "affirm":
              counter= "action_stop"
            else:
              dispatcher.utter_message("We will continue.")
              #will use the same current and ask again.
              #note thatw e have put the current in counter in action_stop_check for a recall.
            return[FollowupAction(counter)]  

          #if counter=="action_stop":
          #  return[FollowupAction(counter)]  
          
                   
          
          #business kind
          
          if current=="action_business_kind":
            if (last_intent=="pvt") or (last_message=="private"):
               #dispatcher.utter_message("Got it u meant private!")
               counter="action_private"
               bkind="private"
            elif (last_intent== "public") or (last_message=="public"):
               #dispatcher.utter_message("Got it u meant public!")
               counter= "action_public"
               bkind="public"
            elif (last_intent=="prop") or (last_message=="prop"):
             #dispatcher.utter_message("Got it u meant proprietery!")
               counter="action_business_years"
               bkind="prop"
            elif (last_intent== "partnership") or (last_message=="partnership"):
             #dispatcher.utter_message("Got it u meant partnership!")
               counter="action_partner"
               bkind="partnership"
            else:
               dispatcher.utter_message("Not understood!")
               counter="action_business_kind"
            return[FollowupAction(counter),SlotSet('bkind', bkind)]
         
          
          
          #Nature of business!!
          
          if current == "action_nob":
             
             if (last_intent=="manufacturing") or (last_message=="manufacturing"):
               #dispatcher.utter_message("Manufacturing!")
               nob="manu"
               #counter= "action_industry_followup"
               return[FollowupAction(counter),SlotSet('nob', nob)]
               #counter= "action_manu_loc"
             elif (last_intent=="SP") or (last_message=="SP"):
               dispatcher.utter_message("Service Provider!")
               nob="sp"
               #counter= "action_industry_followup"
               return[FollowupAction(counter),SlotSet('nob', nob)]
               #counter= "action_sp_order"
             elif (last_intent== "trader") or (last_message=="trader"):
               dispatcher.utter_message("Trader!")
               nob="trader"
               #counter= "action_industry_followup"
               return[FollowupAction(counter),SlotSet('nob', nob)]
               #counter= "action_trader"
             else:
               dispatcher.utter_message("Kindly answer!")
               dispatcher.utter_template("utter_ask_nob", tracker)
               return[FollowupAction("action_listen")]

          
          




#          if current== "action_manu":
#            if last_intent=="affirm":
#              counter="action_manu_loc"
#              return[FollowupAction(counter)]
#            elif last_intent=="deny":
#              counter="action_manu_out"
#            else:
#              dispatcher.utter_message("Not understood!")
#              counter="action_manu"
#            return[FollowupAction(counter)]
            
          
          
          
          #if current == "action_trader":
          #  counter="action_trader_auth"
          #  return[FollowupAction(counter),SlotSet('trader_type', last_message)]
            
            
                   
            
           
          if counter=="end":
               dispatcher.utter_message("Thanks for your time!!")
               return[FollowupAction("action_stop")]
        
        
        return[FollowupAction(counter)]
        

#1)

class Actioninterviewstart(Action):
    def name(self):
        return 'action_interview_start'
    def run(self, dispatcher, tracker, domain):
      counter='action_interview_start'
      current="action_interview_start"
      user_name = tracker.get_slot('user_name')
      user_cell=tracker.get_slot('user_cell')
        
      if (user_name=="Dear" and user_cell=="none"):
           dispatcher.utter_message("Kindly input your registration id- cell number to begin the interview. Use 7838930304 for Demo!")
           return[FollowupAction("action_listen"),SlotSet('counter', counter),SlotSet('current', current) ]
      else:
           dispatcher.utter_message("Continue plz.")
           return[FollowupAction("action_default_fallback")]
        


#2)

class ActionFetchDetails(Action):
    def name(self):
        return 'action_fetch_details'
    def run(self, dispatcher, tracker, domain):
        #this_action='action_interview_start'
        user_name = tracker.get_slot('user_name')
        user_cell=tracker.get_slot('user_cell')
        last_message= tracker.latest_message['text']

        try:
         n=0
         for i in last_message.split():
                if i in df['applicant_1_phone'].fillna(0).astype(int).astype(str).values.tolist():
                    user_cell=i
                    n+=1
         if n>1:
                    dispatcher.utter_message("more than 1 cell identified!. Please provide only the registered cell number")
                    user_cell='none'
                    return[FollowupAction('action_interview_start')]
         elif n==1:
                    user_name=str(df[df.applicant_1_phone==int(user_cell)].last_name.item())  
                    dispatcher.utter_message("Hello {}, we will start the PD discussion now!".format(user_name))
                    #return[SlotSet('user_name', user_name),SlotSet('user_cell', user_cell)]
                    #from rasa_core_sdk.events import FollowupAction
                    return[FollowupAction('action_business_kind'),SlotSet('interview_state', "started"),SlotSet('user_name', user_name), SlotSet('user_cell', user_cell)]
         else:
                    dispatcher.utter_message("Ref ID not registered. Please re-enter the registered id or contact SMEcorner helpdesk to reschedule your interview. Thanks!")
                    return[FollowupAction('action_interview_start')]
        except:
          dispatcher.utter_message("Ref ID not registered. Please re-enter the registered id or contact SMEcorner helpdesk to reschedule your interview. Thanks!")
          return[FollowupAction('action_interview_start')]



#3)
          
class ActionBusinessKind(Action):
    
    def name(self):
        return "action_business_kind"
    def run(self, dispatcher, tracker, domain):
      #dispatcher.utter_message("What kind of business do you have?\n-Private ltd(pvt)\n-Public ltd(pub)\n-Proprietery(prop)\n-Partnership(partner)")
      dispatcher.utter_template("utter_ask_business_kind", tracker)
      current="action_business_kind"
      counter= "action_default_fallback"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]




#4) business_kind-->default fallback--> all these -->business_years-->industry_type

class ActionPrivate(Action):
    
    def name(self):
        return "action_private"
    def run(self, dispatcher, tracker, domain):
      user_cell= tracker.get_slot("user_cell")
      directors=str(df[df.applicant_1_phone==int(user_cell)].directors.item())
      if len(directors)>2:#this is the length of sentence not the number of directors
        dispatcher.utter_message("As per your records: {} are the directors of the company. Please confirm this!".format(directors))
      else:
        dispatcher.utter_message("Please specify the directors in the company")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      current="action_private"
      counter="action_business_years"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionPartner(Action):
    
    def name(self):
        return "action_partner"
    def run(self, dispatcher, tracker, domain):
      user_cell= tracker.get_slot("user_cell")
      #dispatcher.utter_message("Can you please name the partners and their respective ownership in the venture?")
      directors=str(df[df.applicant_1_phone==int(user_cell)].directors.item())
      if len(directors)>2:#this is the length of sentence not the number of directors
        dispatcher.utter_message("As per your records: {} are the partners. Please confirm this and also inform about the respective ownership!".format(directors))
      else:
        dispatcher.utter_message("Can you please name the partners and their respective ownership in the venture?")

      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter= "action_partner_explain"
      current="action_partner"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionPartnerExplain(Action):
    
    def name(self):
        return "action_partner_explain"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("Which all partners are actively involved in business.Please explain")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_business_years"
      current="action_partner_explain"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionPublic(Action):
    
    def name(self):
        return "action_public"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("What is your shareholding in the company?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_public2"
      current="action_public"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionPublic2(Action):
    
    def name(self):
        return "action_public2"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("Is it listed on any stock market?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_business_years"
      current="action_public2"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionBusinessYears(Action):
    
    def name(self):
        return "action_business_years"
    def run(self, dispatcher, tracker, domain):
        user_name = tracker.get_slot('user_name')
        dispatcher.utter_message("How many years have you been in the business {}".format(user_name))
        #ActionSave.run('action_save',dispatcher, tracker, domain)
        counter="action_business_years_explain"
        current="action_business_years"
        return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionBusinessYearsExplain(Action):
    
    def name(self):
        return "action_business_years_explain"
    def run(self, dispatcher, tracker, domain):
        
        current="action_business_years_explain"
        counter="action_industry_type"
        user_name = tracker.get_slot('user_name')
        user_cell = tracker.get_slot('user_cell')
        age= int(df[df.applicant_1_phone==int(user_cell)].age.item())  
        last_message= tracker.latest_message['text']
        
        digit=re.findall('\d+', last_message )
        
        #below means one digit extarcted and its in 2 digits i.e not some year like 2015
        if (len(digit)==1) and (len(digit[0])<3):
          if (age-int(digit[0]))>22:
            dispatcher.utter_message("{} what was it that you were working in, before this venture?".format(user_name))
            return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current)]
            
          elif 0<(age-int(digit[0]))<18:
            dispatcher.utter_message("{} you have been in the business from a very young age, which generationg business is this?".format(user_name))
            return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current)]
            
          elif (age-int(digit[0]))<0:
            dispatcher.utter_message("{} you cant be working in the business before you were born. Please answer again?".format(user_name))
            return[FollowupAction("action_business_years")]
            
          else:
            dispatcher.utter_message("{} Did you work in any other venture before this?".format(user_name))
            return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current)]
            
        else: 
          dispatcher.utter_message("{} Did you work in any other venture before this?".format(user_name))
          return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current)]
        #ActionSave.run('action_save',dispatcher, tracker, domain)
        
        
        


####################################################################################
####################################################################################



#5)

class ActionIndustryType(Action):
    
    def name(self):
        return "action_industry_type"
    def run(self, dispatcher, tracker, domain):
      #dispatcher.utter_message("What is the industry type?\nTextile\n-Garments\n-coaching\n-paper\n-Electronics\n-Fmcg\n-Groceries\n-Any other plz specify")
      dispatcher.utter_template("utter_ask_industry", tracker)
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      current="action_industry_type"
      counter="action_industry_followup"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionNob(Action):
    
    def name(self):
        return "action_nob"
    def run(self, dispatcher, tracker, domain):
      #dispatcher.utter_message("What is the nature of business:\n-Manufacturing(Manu)\n-Trader(retail/wholesale)\n-Service-Provider(SP)")
      dispatcher.utter_template("utter_ask_nob",tracker)
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      current="action_nob"
      counter="action_default_fallback"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]











class ActionIndustryFollowup(Action):
    
    def name(self):
        return "action_industry_followup"
    def run(self, dispatcher, tracker, domain):
      current="action_industry_followup"
      #counter="action_industry_followup"
      industry= tracker.get_slot("industry")
      last_intent= tracker.latest_message['intent'].get('name')
      last_message= tracker.latest_message['text']

      
      if (last_intent=="garments") or (last_message=="garments"):
        industry="garments"
        dispatcher.utter_template("utter_ask_nob", tracker)
        current='action_nob'
        counter="action_garments"
        return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction("action_listen"), SlotSet('industry', industry) ]
        
            
      elif (last_intent=="chemical") or (last_message=="chemical"):
        industry="chemical"
        nob="trader"
        counter="action_chemical"
        return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction(counter), SlotSet('industry', industry),SlotSet('nob', nob)  ]    
      
      
      elif (last_intent=="fmcg") or last_message=="fmcg":
        industry="fmcg"
        nob="trader"
        counter="action_fmcg"
        return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction(counter), SlotSet('industry', industry),SlotSet('nob', nob)  ]
      
      
      elif (last_intent=="hotel") or last_message=="hotel":
        industry="hotel"
        nob="hotel"
        counter="action_hotel"            
        return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction(counter), SlotSet('industry', industry),SlotSet('nob', nob)  ]
            #elif last_intent=="electronics":
            #  industry="electronics"
            
            #elif last_intent=="groceries":
            #  industry="groceries"
            
            #elif last_intent=="paper":
            #  industry="paper"
            
      else:
        industry="other"
        dispatcher.utter_template("utter_ask_nob", tracker)
        current="action_nob"
        counter= "action_decide_flow"
        return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction(counter), SlotSet('industry', industry)]
    
      
            
 


class ActionDecideFlow(Action):
    
    def name(self):
        return "action_decide_flow"
    def run(self, dispatcher, tracker, domain):
      nob= tracker.get_slot("nob")
      #current= tracker.get_slot("current")
      if nob == "manu":
        counter="action_manu"
        return [FollowupAction(counter)]
      elif nob=="sp":
        counter="action_sp_order"
        return [FollowupAction(counter)]
      elif nob=="trader":
        counter="action_trader"
        return [FollowupAction(counter)]
      else:
        dispatcher.utter_message("Something is wrong I dont know the nature of business!!")
        dispatcher.utter_template("utter_ask_nob", tracker)
        current="action_nob"
        counter= "action_decide_flow"
        return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionStop(Action):
    
    def name(self):
        return "action_stop"
    def run(self, dispatcher, tracker, domain):
      user_name= tracker.get_slot("user_name").split()[0]
      dispatcher.utter_message("Goodbye {}".format(user_name))
      dispatcher.utter_message("The interview is over and recorded {}".format(user_name))
      #tracker.export_stories_to_file()
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_stop"
      current="action_stop"
      return [SlotSet('counter', counter),FollowupAction("action_restart"),SlotSet('current', current) ]
 

class ActionStopCheck(Action):
    
    def name(self):
        return "action_stop_check"
    def run(self, dispatcher, tracker, domain):
      #user_name= tracker.get_slot("user_name")
      dispatcher.utter_template("utter_stop_check", tracker)
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter=tracker.get_slot("current")
      current="action_stop_check"
      return [FollowupAction("action_listen"),SlotSet('current', current),SlotSet('counter', counter) ]



"""
class ActionChitchat(Action):
    def name(self):
        return("action_chitchat")
    def run(self, tracker, dispatcher, domain):
      name= tracker.get_name("user_name")
      dispatcher.utter_message("Cut the chitchat and finish your interview {}".format(name))
      current= tracker.get_slot("current")
      return[FollowupAction(current)]
"""


#######################################################################################################################3
"followup qs from action_business_kind, leads to action_nob"
##################################################################################################################      

class ActionGarments(Action):
    
    def name(self):
        return "action_garments"
    def run(self, dispatcher, tracker, domain):
      current="action_garments"
      #counter="action_hotel"
      #see why we have current as decide flow!!
      #industry= tracker.get_slot("industry")
      #last_intent= tracker.latest_message['intent'].get('name')
      #last_message= tracker.latest_message['text']
      
      
      dispatcher.utter_message("What kind of garments?")
      counter="action_decide_flow"
      return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction("action_listen")]
      

class ActionChemical(Action):
    
    def name(self):
        return "action_chemical"
    def run(self, dispatcher, tracker, domain):
      current="action_chemical"
      #counter="action_hotel"
      #see why we have current as decide flow!!
      #industry= tracker.get_slot("industry")
      #last_intent= tracker.latest_message['intent'].get('name')
      #last_message= tracker.latest_message['text']
      
      
      dispatcher.utter_message("What kind of chemicals?\n-Inorganic\n-Organic")
      counter="action_chemical2"
      return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction("action_listen")]

class ActionChemical2(Action):
    
    def name(self):
        return "action_chemical2"
    def run(self, dispatcher, tracker, domain):
      current="action_chemical2"
      #counter="action_hotel"
      #see why we have current as decide flow!!
      #industry= tracker.get_slot("industry")
      #last_intent= tracker.latest_message['intent'].get('name')
      #last_message= tracker.latest_message['text']
      
      
      dispatcher.utter_message("Where all are these chemicals used?")
      counter="action_decide_flow"
      return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction("action_listen")]


class Actionfmcg(Action):
    
    def name(self):
        return "action_fmcg"
    def run(self, dispatcher, tracker, domain):
      current="action_fmcg"
      #counter="action_hotel"
      #see why we have current as decide flow!!
      #industry= tracker.get_slot("industry")
      #last_intent= tracker.latest_message['intent'].get('name')
      #last_message= tracker.latest_message['text']
      
      
      #dispatcher.utter_message("Do you have any product's authorized dealership? Kindly name if any!")
      counter="action_decide_flow"
      return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction("action_listen")]


class ActionHotel(Action):
    
    def name(self):
        return "action_hotel"
    def run(self, dispatcher, tracker, domain):
      current="action_hotel"
      #counter="action_hotel"
      #see why we have current as decide flow!!
      #industry= tracker.get_slot("industry")
      #last_intent= tracker.latest_message['intent'].get('name')
      #last_message= tracker.latest_message['text']
      
      
      dispatcher.utter_message("What kind of food do you offer?")
      counter="action_hotel2"
      return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction("action_listen")]


class ActionHotel2(Action):
    
    def name(self):
        return "action_hotel2"
    def run(self, dispatcher, tracker, domain):
      current="action_hotel2"
      #counter="action_hotel"
      #see why we have current as decide flow!!
      #industry= tracker.get_slot("industry")
      #last_intent= tracker.latest_message['intent'].get('name')
      #last_message= tracker.latest_message['text']
      
      
      dispatcher.utter_message("Do you provide home delivery?\n-Yes\n-No")
      counter="action_hotel3"
      return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionHotel3(Action):
    
    def name(self):
        return "action_hotel3"
    def run(self, dispatcher, tracker, domain):
      current="action_hotel3"
      #counter="action_hotel"
      #see why we have current as decide flow!!
      #industry= tracker.get_slot("industry")
      last_intent= tracker.latest_message['intent'].get('name')
      #last_message= tracker.latest_message['text']
      if last_intent=="affirm":
        dispatcher.utter_message("Do you have any tie-ups with Swiggy, UberEats, Zomato etc. Please specify.")
        counter="action_hotel4"
        return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction("action_listen")]
      elif last_intent=="deny":
        counter="action_hotel4"
        return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction(counter)]
      else:
        dispatcher.utter_message("Not Understood!")
        counter= "action_hotel2"
        return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction(counter)]



class ActionHotel4(Action):
    
    def name(self):
        return "action_hotel4"
    def run(self, dispatcher, tracker, domain):
      current="action_hotel4"
      #counter="action_hotel"
      #see why we have current as decide flow!!
      #industry= tracker.get_slot("industry")
      #last_intent= tracker.latest_message['intent'].get('name')
      #last_message= tracker.latest_message['text']
      
      
      dispatcher.utter_message("Is there any difference in revenue generated on weekdays and weekends. Kindly explain.")
      counter="action_hotel5"
      return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction("action_listen")]


class ActionHotel5(Action):
    
    def name(self):
        return "action_hotel5"
    def run(self, dispatcher, tracker, domain):
      current="action_hotel5"
      #counter="action_hotel"
      #see why we have current as decide flow!!
      #industry= tracker.get_slot("industry")
      #last_intent= tracker.latest_message['intent'].get('name')
      #last_message= tracker.latest_message['text']
      
      
      dispatcher.utter_message("Do you also serve alchohol?")
      counter="action_hotel6"
      return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction("action_listen")]


class ActionHotel6(Action):
    
    def name(self):
        return "action_hotel6"
    def run(self, dispatcher, tracker, domain):
      current="action_hotel6"
      #counter="action_hotel"
      #see why we have current as decide flow!!
      #industry= tracker.get_slot("industry")
      #last_intent= tracker.latest_message['intent'].get('name')
      #last_message= tracker.latest_message['text']
      
      
      dispatcher.utter_message("What percentage of revenue generated daily is through card swipe/Online payment?")
      counter="action_credit"
      return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionManu(Action):
    
    def name(self):
        return "action_manu"
    def run(self, dispatcher, tracker, domain):
      current="action_manu"
      
      #see why we have current as decide flow!!
      #industry= tracker.get_slot("industry")
      #last_intent= tracker.latest_message['intent'].get('name')
      #last_message= tracker.latest_message['text']
      
      
      dispatcher.utter_template("utter_ask_manu", tracker)#inhouse/outsourced
      counter="action_manu2"
      return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction("action_listen")]

class Actionmanu2(Action):
    
    def name(self):
        return "action_manu2"
    def run(self, dispatcher, tracker, domain):
      current="action_manu2"
      #counter="action_hotel"
      #see why we have current as decide flow!!
      #industry= tracker.get_slot("industry")
      last_intent= tracker.latest_message['intent'].get('name')
      #last_message= tracker.latest_message['text']
      if last_intent=="affirm":
        #dispatcher.utter_message("Do you have any tie-ups with Swiggy, UberEats, Zomato etc. Please specify.")
        counter="action_manu3"
        return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction(counter)]
      elif last_intent=="deny":
        counter="action_manu20"
        return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction(counter)]
      else:
        dispatcher.utter_message("Not Understood!")
        counter= "action_manu"
        return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction(counter)]


class ActionManu3(Action):
    
    def name(self):
        return "action_manu3"
    def run(self, dispatcher, tracker, domain):
      current="action_manu3"
      
      #see why we have current as decide flow!!
      #industry= tracker.get_slot("industry")
      #last_intent= tracker.latest_message['intent'].get('name')
      #last_message= tracker.latest_message['text']
      
      
      dispatcher.utter_message("Where is the manufacturing unit, please specify the address(all if more)")
      counter="action_manu4"
      return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction("action_listen")]


class ActionManu4(Action):
    
    def name(self):
        return "action_manu4"
    def run(self, dispatcher, tracker, domain):
      current="action_manu4"
      
      #see why we have current as decide flow!!
      #industry= tracker.get_slot("industry")
      #last_intent= tracker.latest_message['intent'].get('name')
      #last_message= tracker.latest_message['text']
      
      
      dispatcher.utter_message("How do you manage the oversee of manufacture unit.")
      counter="action_manu5"
      return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionManu5(Action):
    
    def name(self):
        return "action_manu5"
    def run(self, dispatcher, tracker, domain):
      current="action_manu5"
      
      #see why we have current as decide flow!!
      user_name= tracker.get_slot("user_name")
      #last_intent= tracker.latest_message['intent'].get('name')
      #last_message= tracker.latest_message['text']
      
      
      dispatcher.utter_message("How many machines do you have in the specified manufacturing locations {}?".format(user_name))
      counter="action_manu6"
      return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction("action_listen")]


class ActionManu6(Action):
    
    def name(self):
        return "action_manu6"
    def run(self, dispatcher, tracker, domain):
      current="action_manu6"
      
      #see why we have current as decide flow!!
      #industry= tracker.get_slot("industry")
      #last_intent= tracker.latest_message['intent'].get('name')
      #last_message= tracker.latest_message['text']
      
      
      dispatcher.utter_message("How many workers work in the manufacturing location(s)")
      counter="action_manu7"
      return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction("action_listen")]


class ActionManu7(Action):
    
    def name(self):
        return "action_manu7"
    def run(self, dispatcher, tracker, domain):
      current="action_manu7"
      
      #see why we have current as decide flow!!
      #industry= tracker.get_slot("industry")
      #last_intent= tracker.latest_message['intent'].get('name')
      last_message= tracker.latest_message['text']
      digits=[i for i in re.findall('\d+', last_message )]
      counter="action_manu8"  
      
      if len(digits)>0 and (0 not in digits):
        dispatcher.utter_message("Are the workers working single shifts or double shifts?")
        return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction("action_listen")]
      else:
        return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction("action_listen")]


class ActionManu8(Action):
    
    def name(self):
        return "action_manu8"
    def run(self, dispatcher, tracker, domain):
      current="action_manu8"
      
      #see why we have current as decide flow!!
      #industry= tracker.get_slot("industry")
      #last_intent= tracker.latest_message['intent'].get('name')
      #last_message= tracker.latest_message['text']
      
      
      dispatcher.utter_message("What is the total capacity for productions and what is the average utilization?")
      counter="action_credit"
      return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction("action_listen")]


class ActionManu20(Action):
    
    def name(self):
        return "action_manu20"
    def run(self, dispatcher, tracker, domain):
      current="action_manu20"
      
      #see why we have current as decide flow!!
      #industry= tracker.get_slot("industry")
      #last_intent= tracker.latest_message['intent'].get('name')
      #last_message= tracker.latest_message['text']
      
      
      dispatcher.utter_message("Please specify the manufacturers where you outsource your production, or explain otherwise.")
      counter="action_credit"
      return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction("action_listen")]


        
        




class ActionTrader(Action):
    
    def name(self):
        return "action_trader"
    def run(self, dispatcher, tracker, domain):
      #dispatcher.utter_message("What kind of Trader are you into:\n-Retail\n-Wholesale\n-Both retail and wholesale")
      current="action_trader"
      counter="action_trader2"
      #see why we have current as decide flow!!
      #industry= tracker.get_slot("industry")
      last_intent= tracker.latest_message['intent'].get('name')
      last_message= tracker.latest_message['text']
      
      dispatcher.utter_template("utter_ask_trader_type", tracker)
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current)]
      

class ActionTrader2(Action):
    
    def name(self):
        return "action_trader2"
    def run(self, dispatcher, tracker, domain):
      #dispatcher.utter_message("What kind of Trader are you into:\n-Retail\n-Wholesale\n-Both retail and wholesale")
      current="action_trader2"
      counter="action_trader3"
      #see why we have current as decide flow!!
      #industry= tracker.get_slot("industry")
      last_intent= tracker.latest_message['intent'].get('name')
      last_message= tracker.latest_message['text']
      
      if (last_intent=="retail") or (last_message=="retail"):
        trader_type="retail"
        
        #return [SlotSet('counter', counter),FollowupAction(counter),SlotSet('current', current), SlotSet('trader_type', trader_type)]
        
      elif (last_intent=="wholesale") or (last_message=="wholesale"):
        
        trader_type="wholesale"
          
        #return [SlotSet('counter', counter),FollowupAction(counter),SlotSet('current', current), SlotSet('trader_type', trader_type)]
        
      elif (last_message=="both"):
          
        trader_type="both"
          
        #return [SlotSet('counter', counter),FollowupAction(counter),SlotSet('current', current),  SlotSet('trader_type', trader_type)]
        
      else:
        dispatcher.utter_message("Not understood")
        counter="action_trader"
        return [SlotSet('counter', counter),FollowupAction(counter),SlotSet('current', current)]
      
      #dispatcher.utter_template("utter_ask_trader_type", tracker)
      return [SlotSet('counter', counter),FollowupAction(counter),SlotSet('current', current), SlotSet('trader_type', trader_type)]



class ActionTrader3(Action):
    
    def name(self):
        return "action_trader3"
    def run(self, dispatcher, tracker, domain):
      #dispatcher.utter_message("What kind of Trader are you into:\n-Retail\n-Wholesale\n-Both retail and wholesale")
      current="action_trader3"
      counter="action_trader4"
      last_intent= tracker.latest_message['intent'].get('name')
      last_message= tracker.latest_message['text']
      
      dispatcher.utter_message("Do you have any authorized dealership of any product? ")
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current)]
            
class ActionTrader4(Action):
    
    def name(self):
        return "action_trader4"
    def run(self, dispatcher, tracker, domain):
      #dispatcher.utter_message("What kind of Trader are you into:\n-Retail\n-Wholesale\n-Both retail and wholesale")
      current="action_trader4"
      counter="action_trader5"
      last_intent= tracker.latest_message['intent'].get('name')
      last_message= tracker.latest_message['text']
      trader_type=tracker.get_slot("trader_type")
        
      if trader_type=="wholesale":
        dispatcher.utter_message("Do you have any daily sale? if yes how much?")
      else:
        dispatcher.utter_message("What is the Daily walkin sale or the daily galla")
      
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current)]
      
class ActionTrader5(Action):
    
    def name(self):
        return "action_trader5"
    def run(self, dispatcher, tracker, domain):
      #dispatcher.utter_message("What kind of Trader are you into:\n-Retail\n-Wholesale\n-Both retail and wholesale")
      current="action_trader5"
      counter="action_credit"
      last_intent= tracker.latest_message['intent'].get('name')
      last_message= tracker.latest_message['text']
      
      dispatcher.utter_message("Where do you stock your goods/inventory?")
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current)]

        




class ActionSpOrder(Action):
    
    def name(self):
        return "action_sp_order"
    def run(self, dispatcher, tracker, domain):
      current="action_sp_order"
      counter="action_sp_order2"
      dispatcher.utter_message("What are the orders/contracts in hand")
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionSpOrder2(Action):
    
    def name(self):
        return "action_sp_order2"
    def run(self, dispatcher, tracker, domain):
      current="action_sp_order2"
      counter="action_credit"
      dispatcher.utter_message("Are these orders renewed every year")      
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]






################################################################################################
      
################################################################################################



class ActionCredit(Action):
    
    def name(self):
        #return "action_purchase_parties"
        return "action_credit"
    def run(self, dispatcher, tracker, domain):
      current="action_credit"
      counter="action_credit2"
      #see why we have current as decide flow!!
      #industry= tracker.get_slot("industry")
      
      #last_intent= tracker.latest_message['intent'].get('name')
      #last_message= tracker.latest_message['text']
      
      dispatcher.utter_message("Are there any specific parties you buy your goods/raw material from. Please name them?")
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current)]

class ActionCredit2(Action):
    
    def name(self):
        #return "action_purchase_parties"
        return "action_credit2"
    def run(self, dispatcher, tracker, domain):
      current="action_credit2"
      counter="action_credit3"
      #see why we have current as decide flow!!
      #industry= tracker.get_slot("industry")
      
      #last_intent= tracker.latest_message['intent'].get('name')
      #last_message= tracker.latest_message['text']
      
      dispatcher.utter_message("What are the payment terms with your suppliers?")
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current)]


class ActionCredit3(Action):
    
    def name(self):
        #return "action_purchase_parties"
        return "action_credit3"
    def run(self, dispatcher, tracker, domain):
      current="action_credit3"
      counter="action_credit4"
      #see why we have current as decide flow!!
      #industry= tracker.get_slot("industry")
      #last_intent= tracker.latest_message['intent'].get('name')
      #last_message= tracker.latest_message['text']
      
      dispatcher.utter_message("How much creditors outstanding/trade payable as of date OR what is the credit position as of date")
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current)]


class ActionCredit4(Action):
    
    def name(self):
        #return "action_purchase_parties"
        return "action_credit4"
    def run(self, dispatcher, tracker, domain):
      current="action_credit4"
      counter="action_debit"
      #see why we have current as decide flow!!
      #industry= tracker.get_slot("industry")
      #last_intent= tracker.latest_message['intent'].get('name')
      #last_message= tracker.latest_message['text']
      
      dispatcher.utter_message("What stock levels are maintained?")
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current)]



class ActionDebit(Action):
    
    def name(self):
        #return "action_purchase_parties"
        return "action_debit"
    def run(self, dispatcher, tracker, domain):
      current="action_debit"
      counter="action_debit2"
      
      industry= tracker.get_slot("industry")
      
      
      #last_intent= tracker.latest_message['intent'].get('name')
      #last_message= tracker.latest_message['text']
      
      
      if industry=="hotel":
        
        counter="action_monthly_sales"
        
        return [SlotSet('counter', counter),FollowupAction(counter),SlotSet('current', current)]
      
      else:
        
        dispatcher.utter_message("Please explain the payment terms with your buyers/clients.")
        
        return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current)]

class ActionDebit2(Action):
    
    def name(self):
        #return "action_purchase_parties"
        return "action_debit2"
    def run(self, dispatcher, tracker, domain):
      current="action_debit2"
      counter="action_monthly_sales"        
      
      #last_intent= tracker.latest_message['intent'].get('name')
      #last_message= tracker.latest_message['text']
      
      dispatcher.utter_message("How much is the outstanding debtor the trade receivables as of date.")
      
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current)]
      



class ActionMonthlySales(Action):
    
    def name(self):
        return "action_monthly_sales"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("Please specify the monthly sales.")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_turnover"
      current="action_monthly_sales"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionTurnover(Action):
    
    def name(self):
        return "action_turnover"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("What is the turnover till date from april this year and what is the expectation for the full year?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_cash"
      current="action_turnover"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionCash(Action):
    
    def name(self):
        return "action_cash"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("What is cash component of the overall sales?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_gross_margins"
      current="action_cash"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionGrossMargins(Action):
    
    def name(self):
        return "action_gross_margins"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("What are the gross margins in the business")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_employees"
      current="action_gross_margins"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionEmployees(Action):
    
    def name(self):
        return "action_employees"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("How many employees do you have?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_gst_status"
      current="action_employees"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]




class ActionGstStatus(Action):
    
    def name(self):
        return "action_gst_status"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("Have you paid the latest gst bills?\n-Yes\n-No")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_loan_amount"
      current="action_gst_status"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionLoanAmount(Action):
    
    def name(self):
        return "action_loan_amount"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("What kind of loan amount are you looking at?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_end_use"
      current="action_loan_amount"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionEndUse(Action):
    
    def name(self):
        return "action_end_use"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("What do you plan to do with the loan money?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_ubl"
      current="action_end_use"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]


class ActionUBL(Action):
    
    def name(self):
        return "action_ubl"
    def run(self, dispatcher, tracker, domain):
      current="action_ubl"
      user_cell=tracker.get_slot('user_cell')
      loan_amt=int(df[df.applicant_1_phone==int(user_cell)].ubl.item())  
      loan_num=int(df[df.applicant_1_phone==int(user_cell)].ubl_num.item())  
      #loan_amt=200000
      #loan_num=6
      dispatcher.utter_message("According to my knowledge, you have a current outstanding ubl of {} in {} different loans. Please explain if anything has changed.".format(loan_amt, loan_num))
            
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_ubl_enquiry"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]





class ActionUBLEnquiry(Action):
    
    def name(self):
        return "action_ubl_enquiry"
    def run(self, dispatcher, tracker, domain):
      current="action_ubl_enquiry"
      user_cell=tracker.get_slot('user_cell')
      enquiry=int(df[df.applicant_1_phone==int(user_cell)].ubl_enquiry.item())  
      #put scop for 0 enquiry
      dispatcher.utter_message("""You have applied for a UBL at {} different loan providers. Why have you not taken loan from any one of the other {}""".format(enquiry, enquiry-1))
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_bto"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]




class ActionBTO(Action):
    
    def name(self):
        return "action_bto"
    def run(self, dispatcher, tracker, domain):
      counter="action_ccod"
      current="action_bto"
#      BTO=1.5
      user_cell=tracker.get_slot('user_cell')
      BTO=int(df[df.applicant_1_phone==int(user_cell)].BTO.item())  
      

      if BTO>1:
       dispatcher.utter_message("Your BTO is {} Please explain why it is so high?".format(BTO))
       #ActionSave.run('action_save',dispatcher, tracker, domain)
       return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]
      elif BTO<0.4:
       dispatcher.utter_message("Your BTO is {}, Please explai wht is it so low?".format(BTO))
       #ActionSave.run('action_save',dispatcher, tracker, domain
       return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]
      else:
        #dispatcher.utter_message("bto is {}".format(BTO))
        return[FollowupAction(counter),SlotSet('counter', counter),SlotSet('current', current) ]

       



class ActionCCOD(Action):
    
    def name(self):
        return "action_ccod"
    def run(self, dispatcher, tracker, domain):
      counter="action_emi_bounce"
      current="action_ccod"
      #ccod = 1
      user_cell=tracker.get_slot('user_cell')
      ccod=int(df[df.applicant_1_phone==int(user_cell)].ccod_dep.item())  

      if ccod==1:
        dispatcher.utter_message("Why CC/OD is depleating in the last 6 months?")
       # ActionSave.run('action_save',dispatcher, tracker, domain)
        return[SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ] 
      else:
       return [FollowupAction(counter),SlotSet('counter', counter),SlotSet('current', current) ]



class ActionEMIBounce(Action):
    
    def name(self):
        return "action_emi_bounce"
    def run(self, dispatcher, tracker, domain):
      counter="end"
      current="action_emi_bounce"
#      emi_bounce=3
      user_cell=tracker.get_slot('user_cell')
      emi_bounce=int(df[df.applicant_1_phone==int(user_cell)].emi_bounce_6.item())  
      

      if emi_bounce > 0:
       dispatcher.utter_message("You have bounced on your emis {} times in the past year. Can you please explain".format(emi_bounce))
       #ActionSave.run('action_save',dispatcher, tracker, domain)
       return[SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current)]
      else:
       return[FollowupAction("action_default_fallback"),SlotSet('counter', counter),SlotSet('current', current)]
       





