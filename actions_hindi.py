#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 30 10:37:42 2019

@author: tarun.bhavnani@dev.smecorner.com

one counter for last uttered, in case of repeat the bot still is on the last utterance
one counter for the previous action as well in case of rep


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
import datetime
nlp= spacy.load("en")

df = pd.read_excel('data_los.xlsx')



logger = logging.getLogger(__name__)



class ActionDefaultFallback(Action):
    def name(self):
        #return "action_question_counter"
        return 'action_default_fallback'
    def run(self, dispatcher, tracker, domain):
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
        digits=[i for i in re.findall('\d+', last_message )]
        date= next(tracker.get_latest_entity_values("DATE"), None)
        cardinal= next(tracker.get_latest_entity_values("CARDINAL"), None)
        #dispatcher.utter_message(current)
        #dispatcher.utter_message(counter)
        dispatcher.utter_message(last_intent)
 
        
        #before interview start
        #interview state turns to "started if details are fetched in action fetch details"
        
        if interview_state == "start":
          if last_intent=="greet":         
            dispatcher.utter_message("अब हम पीडी शुरू करने के लिए आगे बढ़ेंगे। यदि आप किसी भी समय इंटरव्यू से बाहर निकलना चाहते हैं, तो 'stop' इनपुट करें.")
            counter="action_interview_start"
            return[FollowupAction(counter)]
          elif counter !="action_interview_start":
            
            dispatcher.utter_message("शुरू करने के लिए कृपया 'Hi' इनपुट करें.")
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
            dispatcher.utter_message("कृपया उत्तर को खाली न छोड़ें, मैं फिर पूछूंगा.")
            return[FollowupAction(current)]
          
          #repeat
          
          if (last_intent=="repeat") or (last_message=="what"):
            dispatcher.utter_message("मैं फिर पूछूंगा.")           
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
        

          #staring the interview with 12345

          if current=="action_fetch_details":
            user_name= last_message
            return[FollowupAction(counter),SlotSet('user_name', user_name) ]  
        
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
#          if current=="action_fetch_details":
#            user_name= last_message
#            return[FollowupAction(counter),SlotSet('user_name', user_name) ]  
            
          
          if current=="action_stop_check":
            if last_intent== "affirm":
              counter= "action_stop"
            else:
              dispatcher.utter_message("हम PD जारी रखेंगे।")
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
               dispatcher.utter_message("सर्विस प्रोवाइडर!")
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
               dispatcher.utter_message("कृपया जवाब दें!")
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
               dispatcher.utter_message("आपके समय के लिए धन्यवाद!")
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
           #dispatcher.utter_message("PD शुरू करने के लिए कृपया अपना ID/सेल नंबर इनपुट करें। डेमो के लिए 12345 का प्रयोग करें!")
           dispatcher.utter_message("PD शुरू करने के लिए कृपया 12345 इनपुट करें।")
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
         if (user_name=="Dear" and user_cell=="12345"):
                    dispatcher.utter_message("कृपया अपना पूरा नाम इनपुट करें")
                    return[FollowupAction('action_listen'),SlotSet('user_cell', user_cell),SlotSet('interview_state', "started"),SlotSet('current', "action_fetch_details"),SlotSet('counter', "action_business_kind")]
                    
         if n>1:
                    dispatcher.utter_message("1 से अधिक सेल की पहचान !. कृपया केवल पंजीकृत ID/सेल नंबर प्रदान करें")
                    user_cell='none'
                    return[FollowupAction('action_interview_start')]
         elif n==1:
                    user_name=str(df[df.applicant_1_phone==int(user_cell)].last_name.item())  
                    dispatcher.utter_message("नमस्ते {}, अब हम PD शुरू करेंगे!".format(user_name))
                    #return[SlotSet('user_name', user_name),SlotSet('user_cell', user_cell)]
                    #from rasa_core_sdk.events import FollowupAction
                    return[FollowupAction('action_business_kind'),SlotSet('interview_state', "started"),SlotSet('user_name', user_name), SlotSet('user_cell', user_cell)]
         else:
                    dispatcher.utter_message("Ref आईडी रजिस्टर्ड नहीं है। कृपया रजिस्टर्ड आईडी इनपुट करें या अपने  इंटरव्यू को पुनर्निर्धारित करने के लिए SMEcorner हेल्पडेस्क से संपर्क करें। धन्यवाद!")
                    return[FollowupAction('action_interview_start')]
        except:
          dispatcher.utter_message("Ref आईडी रजिस्टर्ड नहीं है। कृपया रजिस्टर्ड आईडी इनपुट करें या अपने  इंटरव्यू को पुनर्निर्धारित करने के लिए SMEcorner हेल्पडेस्क से संपर्क करें। धन्यवाद!")
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
      if len(directors)>5:#this is the length of sentence not the number of directors
        dispatcher.utter_message("रिकॉर्ड के अनुसार: {} कंपनी के डाइरेक्टर(s) हैं, कृपया इसे confirm करें!".format(directors))
      else:
        dispatcher.utter_message("कृपया कंपनी के डाइरेक्टर का विवरण दे")
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
      if directors!="nan":
       if len(directors)>2:#this is the length of sentence not the number of directors
         dispatcher.utter_message("अपने रिकॉर्ड के अनुसार: {} पार्टनर हैं। कृपया इसकी पुष्टि करें और संबंधित मालिकी के बारे में भी सूचित करें!!".format(directors))
       else:
         pass
      else:
         dispatcher.utter_message("क्या आप कृपया वेंचर में पार्टनरों के नाम और उनसे संबंधित मालिकी  की जानकारी दे सकते हैं?")

      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter= "action_partner_explain"
      current="action_partner"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionPartnerExplain(Action):
    
    def name(self):
        return "action_partner_explain"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("कौन से सभी पार्टनर कारोबार में सक्रिय हैं। कृपया जानकारी दे")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_business_years"
      current="action_partner_explain"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionPublic(Action):
    
    def name(self):
        return "action_public"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("कंपनी में आपकी हिस्सेदारी क्या है?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_public2"
      current="action_public"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionPublic2(Action):
    
    def name(self):
        return "action_public2"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("यह किसी भी शेयर बाजार में सूचीबद्ध/listed है?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_business_years"
      current="action_public2"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionBusinessYears(Action):
    
    def name(self):
        return "action_business_years"
    def run(self, dispatcher, tracker, domain):
        user_name = tracker.get_slot('user_name')
        dispatcher.utter_message("आपको इस कारोबार में कितने साल हो गये हैं {}?".format(user_name))
        #ActionSave.run('action_save',dispatcher, tracker, domain)
        counter="action_business_years_explain"
        current="action_business_years"
        return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]


"""
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
        
        elif (len(digit)==1) and (len(digit[0])>3):
            if int(digit[0]) in range(1950,2019):
              #import datetime
              now = datetime.datetime.now()
              years=now.year - int(digit[0])
              
            
        else: 
          dispatcher.utter_message("{} Did you work in any other venture before this?".format(user_name))
          return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current)]
        #ActionSave.run('action_save',dispatcher, tracker, domain)
        
        
"""
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
        date= next(tracker.get_latest_entity_values("DATE"), None)
        #cardinal= next(tracker.get_latest_entity_values("CARDINAL"), None)
        
        
        if date:
          if "years" in date:
            #years=re.findall('\d+', date )
            try:
              years= int(re.findall('\d+', date)[0])
            except:
              try:
                years= w2n.word_to_num(date.split()[0])##################################################################3
              except:
                years=0
          elif "months" in date:
            try:
              years= round(int(re.findall('\d+', date)[0])/12)
            except:
              try:
                years= round(int(w2n.word_to_num(date.split()[0]))/12)
              except:
                years=0
          else:
            years=0
        
        else:
          digit=re.findall('\d+', last_message )
          if (len(digit)==1) and (len(digit[0])<3):
            years= int(digit[0])
          elif (len(digit)==1) and (len(digit[0])>3):
            if int(digit[0]) in range(1950,2019):
              now = datetime.datetime.now()
              years=now.year - int(digit[0])
            else:
              years= 0
          else:
            years= 0
        
        if years==0:
          dispatcher.utter_message("क्या आपने इससे पहले किसी और वेंचर में काम किया है?".format(user_name))
          return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current)]
        elif age-years>22:
          dispatcher.utter_message("आप इस कारोबार में लगभग {} वर्षों से काम कर रहे हैं, इस वेंचर में काम करने से पहले  आप  क्या काम  कर रहे थे?".format(years))
          return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current)]
        elif 0<(age-years)<18:
          dispatcher.utter_message("{} साल,{} आप बहुत कम उम्र से कारोबार में हैं, यह किस पीढ़ी का व्यवसाय है?".format(years,user_name))
          return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current)]
        elif (age-years)<0:
          dispatcher.utter_message("कृपया फिर से उत्तर दें?".format(user_name))
          return[FollowupAction("action_business_years")]          
        else:
          dispatcher.utter_message("क्या आपने इससे पहले किसी और वेंचर में काम किया है?".format(user_name))
          return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current)]
        
          
          
        


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
      
      
      elif (last_intent=="fmcg") or (last_message=="fmcg"):
        industry="fmcg"
        nob="trader"
        counter="action_fmcg"
        return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction(counter), SlotSet('industry', industry),SlotSet('nob', nob)  ]
      
      
      elif (last_intent=="hotel") or (last_message=="hotel"):
        industry="hotel"
        nob="hotel"
        counter="action_hotel"            
        return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction(counter), SlotSet('industry', industry),SlotSet('nob', nob)  ]

      elif (last_intent=="footwear") or (last_message=="footwear"):
        industry="footwear"
        nob="trader"
        counter="action_footwear"            
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
        return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction("action_listen"), SlotSet('industry', industry)]
    
      
            
 


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
      dispatcher.utter_message("इंटरव्यू खत्म हो गया है और दर्ज/रेकार्ड हो गया है ")
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
      
      
      dispatcher.utter_message("किस तरह के गारमेंट्स?")
      counter="action_decide_flow"
      return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction("action_listen")]
      

class ActionFootwear(Action):
    
    def name(self):
        return "action_footwear"
    def run(self, dispatcher, tracker, domain):
      current="action_footwear"
      #counter="action_hotel"
      #see why we have current as decide flow!!
      #industry= tracker.get_slot("industry")
      #last_intent= tracker.latest_message['intent'].get('name')
      #last_message= tracker.latest_message['text']
      
      #buttons = [{'title': 'Retail/Wholesale', 'payload': 'trader'}, {'title': 'Job-Work', 'payload': 'manu'}] 
      buttons = [{'title': 'रीटेल/होलसेल', 'payload': 'trader'}, {'title': 'जॉब-वर्क', 'payload': 'manu'}] 
      dispatcher.utter_button_message(" आपके व्यवसाय किस प्रकार का है?", buttons)
      
    #  dispatcher.utter_message("What kind of garments?")
      counter="action_footwear2"
      return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionFootwear2(Action):
    
    def name(self):
        return "action_footwear2"
    def run(self, dispatcher, tracker, domain):
      current="action_footwear2"
      #counter="action_hotel"
      #see why we have current as decide flow!!
      #industry= tracker.get_slot("industry")
      #last_intent= tracker.latest_message['intent'].get('name')
      last_intent= tracker.latest_message['intent'].get('name')
      last_message= tracker.latest_message['text']
      if (last_message=="trader") or (last_intent=="trader"):
        #dispatcher.utter_message("Do you have any tie-ups with Swiggy, UberEats, Zomato etc. Please specify.")
        counter="action_footwear3"
        nob="trader"
        return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction(counter),SlotSet('nob', nob)]
      elif (last_message=="manu") or (last_intent=="manu"):
        counter="action_footwear20"
        nob="manu"
        return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction(counter),SlotSet('nob', nob)]
      else:
        dispatcher.utter_message("Not Understood!")
        counter= "action_footwear"
        return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction(counter)]



class ActionFootwear3(Action):
    
      def name(self):
         return "action_footwear3"
      def run(self, dispatcher, tracker, domain):
        current="action_footwear3"
      
        buttons = [{'title': 'हाँ', 'payload': 'yes'}, {'title': 'नहीं', 'payload': 'no'}] 
        dispatcher.utter_button_message("क्या आपके पास कोई स्टॉक क्लीयरेंस सेल है?", buttons)
      
        #  dispatcher.utter_message("What kind of garments?")
        counter="action_footwear4"
        return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction("action_listen")]


class ActionFootwear4(Action):
    
      def name(self):
         return "action_footwear4"
      def run(self, dispatcher, tracker, domain):
        current="action_footwear4"
        counter="action_trader3"
        last_intent= tracker.latest_message['intent'].get('name')
        #last_message= tracker.latest_message['text']
        if last_intent=="affirm":
          dispatcher.utter_message("सेल के दौरान मार्जिन क्या हैं?")
          return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction("action_listen")]
        
        
        elif last_intent=="deny":
          dispatcher.utter_message("आप स्टॉक कैसे क्लियर करते हैं?")
          return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction("action_listen")]
        
        else:
          dispatcher.utter_message("Not Understood!")
          counter= "action_footwear3"
          return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction(counter)]



class ActionFootwear20(Action):
    
      def name(self):
         return "action_footwear20"
      def run(self, dispatcher, tracker, domain):
        current="action_footwear20"
      
        buttons = [{'title': 'हाँ', 'payload': 'yes'}, {'title': 'नहीं', 'payload': 'no'}] 
        dispatcher.utter_button_message("क्या आप कुछ fixed ग्राहकों के लिए manufacture करते हैं?", buttons)
      
        #  dispatcher.utter_message("What kind of garments?")
        counter="action_footwear21"
        return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction("action_listen")]

class ActionFootwear21(Action):
    
      def name(self):
         return "action_footwear21"
      def run(self, dispatcher, tracker, domain):
        current="action_footwear21"
        counter="action_manu"
        last_intent= tracker.latest_message['intent'].get('name')
        #last_message= tracker.latest_message['text']
        if last_intent=="affirm":
          dispatcher.utter_message("कृपया उनका नाम और एक सालाना उनसे मिलने वाले व्यापार आदेश के बारे बताएं?")
          return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction("action_listen")]
        
        
        elif last_intent=="deny":
          dispatcher.utter_message("अपने orders का source बताएं!")
          return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction("action_listen")]
        
        else:
          dispatcher.utter_message("Not Understood!")
          counter= "action_footwear20"
          return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction(counter)]




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
      
      
      dispatcher.utter_message("किस तरह के chemicals?\n-Inorganic\n-Organic")
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
      
      
      dispatcher.utter_message("ये सभी केमिकल कहाँ प्रयोग किए जाते हैं?")
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
      return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction(counter)]


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
      
      
      dispatcher.utter_message("आप किस तरह का खाना बनाते हैं?")
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
      buttons = [{'title': 'हाँ', 'payload': 'yes'}, {'title': 'नहीं', 'payload': 'no'}] 
      dispatcher.utter_button_message("क्या आप होम डिलीवरी करते हैं?", buttons)
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
        dispatcher.utter_message("क्या आपके पास Swiggy, UberEats, Zomato आदि के साथ कोई टाई-अप है, कृपया विवरण दे।")
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
      
      
      dispatcher.utter_message("weekdays और weekends में generated revenue में कोई अंतर है। कृपया explain करें।")
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
      
      
      dispatcher.utter_message("क्या आप अल्कोहॉल भी सर्विस करते हैं?")
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
      
      
      dispatcher.utter_message("कार्ड स्वाइप / ऑनलाइन पेमेंट  के माध्यम से रोजाना कितना प्रतिशत व्यवसाय उत्पन्न होता है?")
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
      last_message= tracker.latest_message['text']
      last_message= last_message.lower()
      if (last_intent=="affirm") or (last_message=="inhouse") or (last_intent=="inhouse"):
        #dispatcher.utter_message("Do you have any tie-ups with Swiggy, UberEats, Zomato etc. Please specify.")
        counter="action_manu3"
        return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction(counter)]
      
      elif (last_intent=="deny") or (last_message=="outsourced") or (last_intent=="outsource"):
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
      
      
      dispatcher.utter_message("manufacture unit कहां है, कृपया पता बताये( सभी यदि अधिक हो तो)")
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
      
      
      dispatcher.utter_message("आप manufacture unit की देखरेख कैसे करते हैं")
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
      
      
      dispatcher.utter_message("आपके पास दिए गए manufacturing स्थानों में कितनी मशीनें हैं {}?".format(user_name))
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
      
      
      dispatcher.utter_message("manufacturing स्थान/स्थानों में कितने मज़दूर काम करते हैं")
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
        dispatcher.utter_message("मज़दूर एक शिफ्ट या डबल शिफ्ट में काम कर रहे हैं?")
        return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction("action_listen")]
      else:
        return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction(counter)]


class ActionManu8(Action):
    
    def name(self):
        return "action_manu8"
    def run(self, dispatcher, tracker, domain):
      current="action_manu8"
      
      #see why we have current as decide flow!!
      #industry= tracker.get_slot("industry")
      #last_intent= tracker.latest_message['intent'].get('name')
      #last_message= tracker.latest_message['text']
      
      
      dispatcher.utter_message("उत्पाद के लिए कुल क्षमता क्या है और औसत उपयोग क्या है?")
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
      
      
      dispatcher.utter_message("कृपया उन manufacturers का नाम बताये करें जहाँ आप अपने उत्पादन को आउटसोर्स करते हैं, या समझाएँ।")
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
      
      #dispatcher.utter_message("Do you have any authorized dealership of any product? ")
      buttons = [{'title': 'हाँ', 'payload': 'yes'}, {'title': 'नहीं', 'payload': 'no'}] 
      dispatcher.utter_button_message("क्या आपके पास किसी उत्पाद की कोई authorized डीलरशिप है? ", buttons)
      
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current)]
            
class ActionTrader4(Action):
    
    def name(self):
        return "action_trader4"
    def run(self, dispatcher, tracker, domain):
      #dispatcher.utter_message("What kind of Trader are you into:\n-Retail\n-Wholesale\n-Both retail and wholesale")
      current="action_trader4"
      counter="action_trader5"
      
      last_message= tracker.latest_message['text']
      
      last_intent= tracker.latest_message['intent'].get('name')
        #last_message= tracker.latest_message['text']
      if last_intent=="affirm":
        dispatcher.utter_message("डीलरशिप वाले उत्पाद कौन कौन से हैं?")
        return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction("action_listen")]
        
        
      elif last_intent=="deny":
        #dispatcher.utter_message("How do you clear the stock?")
        return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction(counter)]
        
      else:
        dispatcher.utter_message("Not Understood!")
        counter= "action_trader3"
        return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction(counter)]

      
      
      
      
      
      
      
      
      
      trader_type=tracker.get_slot("trader_type")
        
      if trader_type=="wholesale":
        dispatcher.utter_message("क्या आपकी कोई डेली रीटेल सेल/दैनिक गाल्ला है? यदि हाँ तो कितना?")
      else:
        dispatcher.utter_message("डेली रीटेल सेल या दैनिक गाल्ला क्या है")
      
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
      
      dispatcher.utter_message("आप अपने माल कहां रखते हैं")
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current)]

        




class ActionSpOrder(Action):
    
    def name(self):
        return "action_sp_order"
    def run(self, dispatcher, tracker, domain):
      current="action_sp_order"
      counter="action_sp_order2"
      dispatcher.utter_message("आपके हाथ में orders/contracts क्या हैं")
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionSpOrder2(Action):
    
    def name(self):
        return "action_sp_order2"
    def run(self, dispatcher, tracker, domain):
      current="action_sp_order2"
      counter="action_credit"
      dispatcher.utter_message("क्या ये orders हर साल रिन्यू  होते हैं")      
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
      
      dispatcher.utter_message("क्या कोई विशेष पार्टी हैं जिनसे आप अपना माल / कच्चा माल खरीदते हैं? कृपया उनका नाम बताएं?")
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
      
      dispatcher.utter_message("आपके सप्लायर के साथ पेमेंट  की क्या शर्तें  हैं?")
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
      
      dispatcher.utter_message("आज के अनुसार कितना लेनदार बकाया /ट्रेड payable है या आज के अनुसार क्रेडिट पोजीशन क्या है?")
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
      
      dispatcher.utter_message("स्टॉक का दिनों में क्या स्तर है, जो सामान्य रूप से बनाए रखा जाता है(Stock levels in days)?")
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
        
        dispatcher.utter_message("कृपया अपने खरीदारों / ग्राहकों के साथ भुगतान/पेमेंट की शर्तों की व्याख्या करें।")
        
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
      
      dispatcher.utter_message("तारीख के अनुसार व्यापार प्राप्य कितना है(Trade Receivables)।")
      
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current)]
      



class ActionMonthlySales(Action):
    
    def name(self):
        return "action_monthly_sales"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("मासिक बिक्री क्या है?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_turnover"
      current="action_monthly_sales"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionTurnover(Action):
    
    def name(self):
        return "action_turnover"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("इस साल के अप्रैल से अब तक का कुल बिक्री/टर्न-ओवर क्या है और पूरे साल के लिए क्या उम्मीद है?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_cash"
      current="action_turnover"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionCash(Action):
    
    def name(self):
        return "action_cash"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("कुल मिलाकर बिक्री का कितना प्रतिशत नकद में है?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_gross_margins"
      current="action_cash"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionGrossMargins(Action):
    
    def name(self):
        return "action_gross_margins"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("व्यवसाय में कुल मार्जिन(gross margin) क्या हैं?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_employees"
      current="action_gross_margins"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionEmployees(Action):
    
    def name(self):
        return "action_employees"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("आपके यहां कितने कर्मचारी हैं?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_gst_status"
      current="action_employees"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]




class ActionGstStatus(Action):
    
    def name(self):
        return "action_gst_status"
    def run(self, dispatcher, tracker, domain):

      buttons = [{'title': 'हाँ', 'payload': 'yes'}, {'title': 'नहीं', 'payload': 'no'}] 
      dispatcher.utter_button_message("क्या आपने नवीनतम जीएसटी(gst) बिलों का भुगतान किया है?", buttons)
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_loan_amount"
      current="action_gst_status"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionLoanAmount(Action):
    
    def name(self):
        return "action_loan_amount"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("आपको कितना लोन चाहिए?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_end_use"
      current="action_loan_amount"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionEndUse(Action):
    
    def name(self):
        return "action_end_use"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("आप लोन राशि का उपयोग कैसे करेंगे?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_ubl"
      current="action_end_use"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]


class ActionUBL(Action):
    
    def name(self):
        return "action_ubl"
    def run(self, dispatcher, tracker, domain):
      current="action_ubl"
      counter="action_ubl_enquiry"
      user_cell=tracker.get_slot('user_cell')
      try:
       loan_amt=int(df[df.applicant_1_phone==int(user_cell)].ubl.item())
       loan_num=int(df[df.applicant_1_phone==int(user_cell)].ubl_num.item())
       #loan_amt=200000
       #loan_num=6
       dispatcher.utter_message("According to my knowledge, you have a current outstanding ubl of {} in {} different loans. Please explain if anything has changed.".format(loan_amt, loan_num))
       return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]
      except:
        pass
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      
      return [SlotSet('counter', counter),FollowupAction(counter),SlotSet('current', current) ]





class ActionUBLEnquiry(Action):
    
    def name(self):
        return "action_ubl_enquiry"
    def run(self, dispatcher, tracker, domain):
      current="action_ubl_enquiry"
      counter="action_bto"
      user_cell=tracker.get_slot('user_cell')
      try:
       enquiry=int(df[df.applicant_1_phone==int(user_cell)].ubl_enquiry.item())  
       #put scop for 0 enquiry
       dispatcher.utter_message("""You have applied for a UBL at {} different loan providers. Why have you not taken loan from any one of the other {}""".format(enquiry, enquiry-1))
       return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]
       #ActionSave.run('action_save',dispatcher, tracker, domain)
      except:
        pass
      
      return [SlotSet('counter', counter),FollowupAction(counter),SlotSet('current', current) ]




class ActionBTO(Action):
    
    def name(self):
        return "action_bto"
    def run(self, dispatcher, tracker, domain):
      counter="action_ccod"
      current="action_bto"
#      BTO=1.5
      user_cell=tracker.get_slot('user_cell')
      
      try:
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
      except:
        pass
      return[FollowupAction(counter),SlotSet('counter', counter),SlotSet('current', current) ]

       



class ActionCCOD(Action):
    
    def name(self):
        return "action_ccod"
    def run(self, dispatcher, tracker, domain):
      counter="action_emi_bounce"
      current="action_ccod"
      #ccod = 1
      user_cell=tracker.get_slot('user_cell')
      try:
       ccod=int(df[df.applicant_1_phone==int(user_cell)].ccod_dep.item())  

       if ccod==1:
         dispatcher.utter_message("Why CC/OD is depleating in the last 6 months?")
        # ActionSave.run('action_save',dispatcher, tracker, domain)
         return[SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ] 
       else:
        return [FollowupAction(counter),SlotSet('counter', counter),SlotSet('current', current) ]
      except:
        pass
      return [FollowupAction(counter),SlotSet('counter', counter),SlotSet('current', current) ]


class ActionEMIBounce(Action):
    
    def name(self):
        return "action_emi_bounce"
    def run(self, dispatcher, tracker, domain):
      counter="action_family"
      current="action_emi_bounce"
#      emi_bounce=3
      user_cell=tracker.get_slot('user_cell')
      try:
       emi_bounce=int(df[df.applicant_1_phone==int(user_cell)].emi_bounce_6.item())  
      

       if emi_bounce > 0:
        dispatcher.utter_message("You have bounced on your emis {} times in the past year. Can you please explain".format(emi_bounce))
        #ActionSave.run('action_save',dispatcher, tracker, domain)
        return[SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current)]
       else:
        return[FollowupAction("action_default_fallback"),SlotSet('counter', counter),SlotSet('current', current)]
      except:
        pass
      return[FollowupAction("action_default_fallback"),SlotSet('counter', counter),SlotSet('current', current)]
       


class ActionFamily(Action):
    
    def name(self):
        return "action_family"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("यह अंतिम अनुभाग है। मैं परिवार से संबंधित कुछ सवाल पूछूंगा!")
      dispatcher.utter_message("आप कहां रहते हैं?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_family2"
      current="action_family"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]
    
class ActionFamily2(Action):
    
    def name(self):
        return "action_family2"
    def run(self, dispatcher, tracker, domain):
      
      buttons = [{'title': 'हाँ' , 'payload': 'self'}, {'title': 'नहीं,यह किराए पर है ', 'payload': 'rent'},{'title': 'पारिवारिक', 'payload': 'family'}] 
      dispatcher.utter_button_message("क्या आप वर्तमान में रहने वाले घर के मालिक हो?", buttons)
      
      
      #ActionSave.run('action_save',dispatcher, tracker, domain)#मैं इसका मालिक हूँ' परिवार  का कोई व्यक्ति इसका मालिक है
      counter="action_family3"
      current="action_family2"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]


class ActionFamily3(Action):
    
    def name(self):
        return "action_family3"
    def run(self, dispatcher, tracker, domain):
      
      
      current= "action_family3"
      last_intent= tracker.latest_message['intent'].get('name')
      last_message= tracker.latest_message['text']
      if (last_message=="self"):
        dispatcher.utter_message("आप इस घर में कब शिफ्ट हुए?")
        counter="action_family4"
        
        return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction("action_listen")]
      elif (last_message=="rent"):
        dispatcher.utter_message("आप कब से इस घर में रह रहे हैं?")
        counter="action_family4"
        return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction("action_listen")]
      elif (last_message=="family"):
        dispatcher.utter_message("आप कब से इस घर में रह रहे हैं?")
        counter="action_family4"
        return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction("action_listen")]
      else:
        dispatcher.utter_message("Not Understood!")
        counter= "action_family2"
        return [SlotSet('current', current),SlotSet('counter', counter),FollowupAction(counter)]


class ActionFamily4(Action):
    
    def name(self):
        return "action_family4"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("आपके परिवार में कितने सदस्य हैं?")
      #dispatcher.utter_message("Where do you stay?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_family5"
      current="action_family4"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]

class ActionFamily5(Action):
    
    def name(self):
        return "action_family5"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("क्या आपके परिवार का कोई और सदस्य है, जो अलग स्रोत से कमाता है? ")
      #dispatcher.utter_message("Where do you stay?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      current="action_family5"
      counter="action_ref"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]


class ActionRef(Action):
    
    def name(self):
        return "action_ref"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("इंटरव्यू लगभग समाप्त हो गया है।")
      dispatcher.utter_message("कृपया अपना रेफ-रेंस आईडी इनपुट करें")
      #dispatcher.utter_message("Where do you stay?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      current="action_ref"
      counter="action_ref2"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]

class ActionRef2(Action):
    
    def name(self):
        return "action_ref2"
    def run(self, dispatcher, tracker, domain):
      buttons = [{'title': 'क्रेडिट मैनेजर द्वारा सहायता प्रदान की गई', 'payload': 'Credit Manager assist'}, {'title': 'क्रेडिट मैनेजर ने इंटरव्यू दिया', 'payload': 'Credit Manager'},{'title': 'खुद बिना किसी सहायता के', 'payload': 'Client'}] 
      dispatcher.utter_button_message("आपने इंटरव्यू कैसे लिया?", buttons)
      #dispatcher.utter_message("Where do you stay?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      current="action_ref2"
      counter="end"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]
        
