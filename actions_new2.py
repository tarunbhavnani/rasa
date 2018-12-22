
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
df_counter['ans']=""
df_slots=pd.read_csv("df_slots.csv")

logger = logging.getLogger(__name__)

class Actioninterviewstart(Action):
    def name(self):
        return 'action_interview_start'
    def run(self, dispatcher, tracker, domain):
        this_action='action_interview_start'
        user_name = tracker.get_slot('user_name')
        user_cell=tracker.get_slot('user_cell')
        last_message= tracker.latest_message['text']
        #counter=1
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
                 return[SlotSet('user_name', user_name),SlotSet('user_cell', user_cell),SlotSet('address', address),SlotSet('org_name', org_name),SlotSet('loan_requested', loan_requested),SlotSet('last_action', this_action)]
               except ValueError:
                 dispatcher.utter_message("Kindly check your refrence number, if it is {} then contact SMEhelp desk to reschedule the interview.".format(user_cell))
                 user_cell="none"
                 #counter=0
                 return[SlotSet('user_name', user_name),SlotSet('user_cell', user_cell), SlotSet('last_action', this_action)]






class ActionBusinessKind(Action):
    
    def name(self):
        return "action_business_kind"

    def run(self, dispatcher, tracker, domain):
      
      last_action= tracker.get_slot('this_action')
      this_action="action_business_kind"
      
      dispatcher.utter_message("What kind of business do you have?\n 1) Proprietership \n 2) Partnership \n 3) Private Ltd. \n 4) Public Ltd.")
      ActionSave.run('action_save',dispatcher, tracker, domain)
  
      return [SlotSet('last_action', last_action), SlotSet('this_action', this_action)]



class ActionFamilyStay(Action):
    
    def name(self):
        return "action_family_stay"

    def run(self, dispatcher, tracker, domain):
    
      last_action= tracker.get_slot('this_action')
      this_action="action_family_stay"
      
      dispatcher.utter_message("Where do you stay?")
      ActionSave.run('action_save',dispatcher, tracker, domain)
      
      return [SlotSet('last_action', last_action), SlotSet('this_action', this_action)]


class ActionFamilyHouseOwn(Action):

    def name(self):
        return "action_family_house_own"

    def run(self, dispatcher, tracker, domain):

      last_action= tracker.get_slot('this_action')
      this_action="action_family_house_own"
      dispatcher.utter_message("Do you own the house?")
      ActionSave.run('action_save',dispatcher, tracker, domain)
  
      return [SlotSet('last_action', last_action), SlotSet('this_action', this_action)]


class ActionSave(Action):
    def name(self):
          return "action_save"

    def run(self, dispatcher, tracker, domain):
      
      last_action= tracker.get_slot('this_action')
      
      if last_action=='action_family_stay':
        family_stay = next(tracker.get_latest_entity_values('location'), None)
        if not family_stay:
          family_stay = tracker.latest_message.get('text')
        
        df_slots['slot_value'][df_slots.slot_action==last_action]=family_stay
        return [family_stay]   
    
        
        
      elif last_action=='action_family_house_own':
        dispatcher.utter_message(last_action)
        family_house_own=tracker.get_slot('family_house_own')
        #if not family_house_own:
        if family_house_own=='none':
          intent = tracker.latest_message['intent'].get('name')
          family_house_own = tracker.latest_message.get('text')
          if intent in ['affirm', 'deny']:
            family_house_own=intent
        df_slots['slot_value'][df_slots.slot_action==last_action]=family_house_own      
        return [family_house_own]   
      
      
      
      elif last_action=='action_business_kind':
        dispatcher.utter_message(last_action)
        action_business_kind=tracker.get_slot('action_business_kind')
        #if not action_business_kind:
        if action_business_kind=='none':
          #intent = tracker.latest_message['intent'].get('name')
          action_business_kind = tracker.latest_message.get('text')
        df_slots['slot_value'][df_slots.slot_action==last_action]=action_business_kind 
        return [action_business_kind]   
      
      #else:
      #  return[]
      
        
        
  
          ####
          
class ActionBusinessKind(Action):
      
      def name(self):
          return "action_business_kind"
      
      def run(self, dispatcher, tracker, domain):
        
        last_action= tracker.get_slot('this_action')
        this_action="action_business_kind"
        
        dispatcher.utter_message("What kind of business do you have?\n 1) Proprietership \n 2) Partnership \n 3) Private Ltd. \n 4) Public Ltd.")
        ActionSave.run('action_save',dispatcher, tracker, domain)
        
        return [SlotSet('last_action', last_action), SlotSet('this_action', this_action)]
  
  

class ActionProp(Action):
      
      def name(self):
          return "action_prop"
      
      def run(self, dispatcher, tracker, domain):
        
        last_action= tracker.get_slot('this_action')
        this_action="action_prop"
        dispatcher.utter_message('Can you please name the partners and their respective shareholding pattern?')
        ActionSave.run('action_save',dispatcher, tracker, domain)
        
        return [SlotSet('last_action', last_action), SlotSet('this_action', this_action)]
  
  

class ActionPrivate(Action):
      
      def name(self):
          return "action_private"
      
      def run(self, dispatcher, tracker, domain):
        
        last_action= tracker.get_slot('this_action')
        this_action="action_private"
        
        dispatcher.utter_message('Can you please name the Directors and their respective shareholding pattern?')
        ActionSave.run('action_save',dispatcher, tracker, domain)
        
        return [SlotSet('last_action', last_action), SlotSet('this_action', this_action)]
  
  

class ActionBusinessYears(Action):
      
      def name(self):
          return "action_business_years"
      
      def run(self, dispatcher, tracker, domain):
        
        last_action= tracker.get_slot('this_action')
        this_action="action_business_years"
        dispatcher.utter_message('How many years have you been in this business?')
        ActionSave.run('action_save',dispatcher, tracker, domain)
        
        return [SlotSet('last_action', last_action), SlotSet('this_action', this_action)]
  
  

class ActionBusinessIndustry(Action):
      
      def name(self):
          return "action_business_industry"
      
      def run(self, dispatcher, tracker, domain):
        
        last_action= tracker.get_slot('this_action')
        this_action="action_business_industry"
        
        dispatcher.utter_message('what is the industry type? \n 1)textiles\n 2)groceries\n 3)electronics\n 4) Others')
        ActionSave.run('action_save',dispatcher, tracker, domain)
        
        return [SlotSet('last_action', last_action), SlotSet('this_action', this_action)]
  
  
    
class ActionBusinessNature(Action):
      
      def name(self):
          return "action_business_nature"
      
      def run(self, dispatcher, tracker, domain):
        
        last_action= tracker.get_slot('this_action')
        this_action="action_business_nature"
        
        dispatcher.utter_message('what is the nature of the business:\n 1) Manufacturing\n 2) Trader\n 3)Service')
        ActionSave.run('action_save',dispatcher, tracker, domain)
        
        return [SlotSet('last_action', last_action), SlotSet('this_action', this_action)]
  
  

class ActionBusinessManufactureLocation(Action):
      
      def name(self):
          return "action_business_manufacture_location"
      
      def run(self, dispatcher, tracker, domain):
        
        last_action= tracker.get_slot('this_action')
        this_action="action_business_manufacture_location"
        
        dispatcher.utter_message('where is the manu unit')
        ActionSave.run('action_save',dispatcher, tracker, domain)
        
        return [SlotSet('last_action', last_action), SlotSet('this_action', this_action)]
  
  

class ActionBusinessManufactureMachines(Action):
      
      def name(self):
          return "action_business_manufacture_machines"
      
      def run(self, dispatcher, tracker, domain):
        
        last_action= tracker.get_slot('this_action')
        this_action="action_business_manufacture_machines"
        
        dispatcher.utter_message('how many machines')
        ActionSave.run('action_save',dispatcher, tracker, domain)
        
        return [SlotSet('last_action', last_action), SlotSet('this_action', this_action)]
  
  

class ActionBusinessManufactureCap(Action):
      
      def name(self):
          return "action_business_manufacture_cap"
      
      def run(self, dispatcher, tracker, domain):
        
        last_action= tracker.get_slot('this_action')
        this_action="action_business_manufacture_cap"
        
        dispatcher.utter_message('Total capacity and average utilization')
        ActionSave.run('action_save',dispatcher, tracker, domain)
        
        return [SlotSet('last_action', last_action), SlotSet('this_action', this_action)]
  
  

class ActionBusinessManufactureWorkers(Action):
      
      def name(self):
          return "action_business_manufacture_workers"
      
      def run(self, dispatcher, tracker, domain):
        
        last_action= tracker.get_slot('this_action')
        this_action="action_business_manufacture_workers"
        
        dispatcher.utter_message('Total number of workers')
        ActionSave.run('action_save',dispatcher, tracker, domain)
        
        return [SlotSet('last_action', last_action), SlotSet('this_action', this_action)]
      
  
class ActionBusinessTraderType(Action):
      
      def name(self):
          return "action_business_trader_type"
      
      def run(self, dispatcher, tracker, domain):
        
        last_action= tracker.get_slot('this_action')
        this_action="action_business_trader_type"
        
        dispatcher.utter_message('wholesale or retail')
        ActionSave.run('action_save',dispatcher, tracker, domain)
        
        return [SlotSet('last_action', last_action), SlotSet('this_action', this_action)]
  
  

class ActionBusinessTraderPurchase(Action):
      
      def name(self):
          return "action_business_trader_purchase"
      
      def run(self, dispatcher, tracker, domain):
        
        last_action= tracker.get_slot('this_action')
        this_action="action_business_trader_purchase"
        
        dispatcher.utter_message('purchase against order or stockist--? check for stock days in LOS(financial summary) for any follow up')
        ActionSave.run('action_save',dispatcher, tracker, domain)
        
        return [SlotSet('last_action', last_action), SlotSet('this_action', this_action)]
  
  

class ActionBusinessSPOrders(Action):
      
      def name(self):
          return "action_business_sp_orders"
      
      def run(self, dispatcher, tracker, domain):
        
        last_action= tracker.get_slot('this_action')
        this_action="action_business_sp_orders"
        
        dispatcher.utter_message('oredrs in hand')
        ActionSave.run('action_save',dispatcher, tracker, domain)
        
        return [SlotSet('last_action', last_action), SlotSet('this_action', this_action)]
  
  

class ActionBusinessSPOrdersRenew(Action):
      
      def name(self):
          return "action_business_sp_orders_renew"
      
      def run(self, dispatcher, tracker, domain):
        
        last_action= tracker.get_slot('this_action')
        this_action="action_business_sp_orders_renew"
        
        dispatcher.utter_message('are these orders renewded every year')
        ActionSave.run('action_save',dispatcher, tracker, domain)
        
        return [SlotSet('last_action', last_action), SlotSet('this_action', this_action)]
  
  

class ActionBusinessPartiesPurchase(Action):
      
      def name(self):
          return "action_business_parties_purchase"
      
      def run(self, dispatcher, tracker, domain):
        
        last_action= tracker.get_slot('this_action')
        this_action="action_business_parties_purchase"
        
        dispatcher.utter_message('how many parties do you purchase from can you name the major parties')
        ActionSave.run('action_save',dispatcher, tracker, domain)
        
        return [SlotSet('last_action', last_action), SlotSet('this_action', this_action)]
  
  

class ActionBusinessCreditPaymentTerms(Action):
      
      def name(self):
          return "action_business_credit_payment_terms"
      
      def run(self, dispatcher, tracker, domain):
        
        last_action= tracker.get_slot('this_action')
        this_action="action_business_credit_payment_terms"
        
        dispatcher.utter_message('what are the payment terms')
        ActionSave.run('action_save',dispatcher, tracker, domain)
        
        return [SlotSet('last_action', last_action), SlotSet('this_action', this_action)]
  
  

class ActionBusinessCreditPos(Action):
      
      def name(self):
          return "action_business_credit_pos"
      
      def run(self, dispatcher, tracker, domain):
        
        last_action= tracker.get_slot('this_action')
        this_action="action_business_credit_pos"
        
        dispatcher.utter_message('how much creditors outstanding/ trade payable as of date  OR what is the credit position as of date')
        ActionSave.run('action_save',dispatcher, tracker, domain)
        
        return [SlotSet('last_action', last_action), SlotSet('this_action', this_action)]
  
  

class ActionBusinessStockLevels(Action):
      
      def name(self):
          return "action_business_stock_levels"
      
      def run(self, dispatcher, tracker, domain):
        
        last_action= tracker.get_slot('this_action')
        this_action="action_business_stock_levels"
        
        dispatcher.utter_message('What are the stock level maintained?')
        ActionSave.run('action_save',dispatcher, tracker, domain)
        
        return [SlotSet('last_action', last_action), SlotSet('this_action', this_action)]
  
  

class ActionBusinessStockLevelsFollowup(Action):
      
      def name(self):
          return "action_business_stock_levels_followup"
      
      def run(self, dispatcher, tracker, domain):
        
        last_action= tracker.get_slot('this_action')
        this_action="action_business_stock_levels_followup"
        
        #if manufaturing:
        dispatcher.utter_message('Is it inclusive of raw material, wip, finished goods')
        #dispatcher.utter_message('if service : what kind of stock as no stock in service')
        ActionSave.run('action_save',dispatcher, tracker, domain)
        
        return [SlotSet('last_action', last_action), SlotSet('this_action', this_action)]
  
  
"""
class ActionBusinessStockLevelsFollowup(Action):
      
      def name(self):
          return "action_business_stock_levels_followup"
      
      def run(self, dispatcher, tracker, domain):
        
        this_action="action_business_stock_levels_followup"
        dispatcher.utter_message('if service : what kind of stock as no stock in service')
        ActionSave.run('action_save',dispatcher, tracker, domain)
        
        return [SlotSet('last_action', this_action)]
  
"""  
class ActionBusinessGodown(Action):
      
      def name(self):
          return "action_business_godown"
      
      def run(self, dispatcher, tracker, domain):
        
        last_action= tracker.get_slot('this_action')
        this_action="action_business_godown"
        
        dispatcher.utter_message('where are the goods stocked, do you own the place. Can ask the rent as well')
        ActionSave.run('action_save',dispatcher, tracker, domain)
        
        return [SlotSet('last_action', last_action), SlotSet('this_action', this_action)]
  
  

class ActionBusinessParties(Action):
      
      def name(self):
          return "action_business_parties"
      
      def run(self, dispatcher, tracker, domain):
        
        last_action= tracker.get_slot('this_action')
        this_action="action_business_parties"
        
        dispatcher.utter_message('how many parties do you sell to and can u name the major parties')
        ActionSave.run('action_save',dispatcher, tracker, domain)
        
        return [SlotSet('last_action', last_action), SlotSet('this_action', this_action)]
  
  

class ActionBusinessPartiesPaymentTerms(Action):
      
      def name(self):
          return "action_business_parties_payment_terms"
      
      def run(self, dispatcher, tracker, domain):
        
        last_action= tracker.get_slot('this_action')
        this_action="action_business_parties_payment_terms"
        
        dispatcher.utter_message('what r the payment terms / what is the credit period offered')
        ActionSave.run('action_save',dispatcher, tracker, domain)
        
        return [SlotSet('last_action', last_action), SlotSet('this_action', this_action)]
  
  

class ActionBusinessPartiesPosition(Action):
      
      def name(self):
          return "action_business_parties_position"
      
      def run(self, dispatcher, tracker, domain):
        
        last_action= tracker.get_slot('this_action')
        this_action="action_business_parties_position"
        
        dispatcher.utter_message('how much debtor outstanding/ whats the trade receivables / debtor position')
        ActionSave.run('action_save',dispatcher, tracker, domain)
        
        return [SlotSet('last_action', last_action), SlotSet('this_action', this_action)]
  
  

class ActionBusinessSales(Action):
      
      def name(self):
          return "action_business_sales"
      
      def run(self, dispatcher, tracker, domain):
        
        last_action= tracker.get_slot('this_action')
        this_action="action_business_sales"
        
        dispatcher.utter_message('monthly sales')
        ActionSave.run('action_save',dispatcher, tracker, domain)
        
        return [SlotSet('last_action', last_action), SlotSet('this_action', this_action)]
  
  

class ActionBusinessTO(Action):
      
      def name(self):
          return "action_business_to"
      
      def run(self, dispatcher, tracker, domain):
        
        last_action= tracker.get_slot('this_action')
        this_action="action_business_to"
        
        dispatcher.utter_message('what is the turnover till date from april what is the expectation for the full year, can pull turnover for last year')
        ActionSave.run('action_save',dispatcher, tracker, domain)
        
        return [SlotSet('last_action', last_action), SlotSet('this_action', this_action)]
  
  

class ActionBusinessCC(Action):
      
      def name(self):
          return "action_business_cc"
      
      def run(self, dispatcher, tracker, domain):
        
        last_action= tracker.get_slot('this_action')
        this_action="action_business_cc"
        
        dispatcher.utter_message('what is cash component of the overall sales')
        ActionSave.run('action_save',dispatcher, tracker, domain)
        
        return [SlotSet('last_action', last_action), SlotSet('this_action', this_action)]
  
  

class ActionBusinessGM(Action):
      
      def name(self):
          return "action_business_gm"
      
      def run(self, dispatcher, tracker, domain):
        
        last_action= tracker.get_slot('this_action')
        this_action="action_business_gm"
        
        dispatcher.utter_message('what are the gross margins in the business')
        ActionSave.run('action_save',dispatcher, tracker, domain)
        
        return [SlotSet('last_action', last_action), SlotSet('this_action', this_action)]
  
  

class ActionBusinessEmployees(Action):
      
      def name(self):
          return "action_business_employees"
      
      def run(self, dispatcher, tracker, domain):
        
        last_action= tracker.get_slot('this_action')
        this_action="action_business_employees"
        
        dispatcher.utter_message('How many employees do you have?')
        ActionSave.run('action_save',dispatcher, tracker, domain)
        
        return [SlotSet('last_action', last_action), SlotSet('this_action', this_action)]
  
  

class ActionBusinessGST(Action):
      
      def name(self):
          return "action_business_gst"
      
      def run(self, dispatcher, tracker, domain):
        
        last_action= tracker.get_slot('this_action')
        this_action="action_business_gst"
        
        dispatcher.utter_message('GST margins')
        ActionSave.run('action_save',dispatcher, tracker, domain)
        
        return [SlotSet('last_action', last_action), SlotSet('this_action', this_action)]
  
  

class ActionBusinessGSTBills(Action):
      
      def name(self):
          return "action_business_gst_bills"
      
      def run(self, dispatcher, tracker, domain):
        
        last_action= tracker.get_slot('this_action')
        this_action="action_business_gst_bills"
        
        dispatcher.utter_message('have you paid the latest gst bills')
        ActionSave.run('action_save',dispatcher, tracker, domain)
        
        return [SlotSet('last_action', last_action), SlotSet('this_action', this_action)]
  
  

class ActionBusinessLA(Action):
      
      def name(self):
          return "action_business_la"
      
      def run(self, dispatcher, tracker, domain):
        
        last_action= tracker.get_slot('this_action')
        this_action="action_business_la"
        
        dispatcher.utter_message('what kind of loan amount are you looking at')
        ActionSave.run('action_save',dispatcher, tracker, domain)
        
        return [SlotSet('last_action', last_action), SlotSet('this_action', this_action)]
  
  

class ActionBusinessEndUse(Action):
      
      def name(self):
          return "action_business_end_use"
      
      def run(self, dispatcher, tracker, domain):
        
        last_action= tracker.get_slot('this_action')
        this_action="action_business_end_use"
        
        dispatcher.utter_message('End Use ?')
        ActionSave.run('action_save',dispatcher, tracker, domain)
        
        return [SlotSet('last_action', last_action), SlotSet('this_action', this_action)]
  
