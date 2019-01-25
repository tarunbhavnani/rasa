#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 25 11:05:40 2019

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

df = pd.read_excel('data_los.xlsx')
df_counter=pd.read_csv('df_counter.csv')
df_counter['ans']=""
df_slots=pd.read_csv("df_slots.csv")

logger = logging.getLogger(__name__)
"""
class ActionDefaultFallback(Action):
    "Executes the fallback action and goes back to the previous state of the dialogue"

    def name(self) :
        return 'action_default_fallback_tarun'

    def run(self, dispatcher, tracker, domain):
        
        #last_intent= tracker.latest_message['intent']
         
        dispatcher.utter_template("utter_default", tracker,
                                  silent_fail=True)
        
        return [ActionReverted()]
"""

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
                    return[FollowupAction('action_business_kind'),SlotSet('user_name', user_name), SlotSet('user_cell', user_cell)]
         else:
                    dispatcher.utter_message("Ref ID not registered. Please re-enter the registered id or contact SMEcorner helpdesk to reschedule your interview. Thanks!")
                    return[FollowupAction('action_interview_start')]
        except:
          dispatcher.utter_message("Ref ID not registered. Please re-enter the registered id or contact SMEcorner helpdesk to reschedule your interview. Thanks!")
          return[FollowupAction('action_interview_start')]


class Actioninterviewstart(Action):
    def name(self):
        return 'action_interview_start'
    def run(self, dispatcher, tracker, domain):
      counter='action_interview_start'
      current="action_interview_start"
      user_name = tracker.get_slot('user_name')
      user_cell=tracker.get_slot('user_cell')
        
      if (user_name=="Dear" and user_cell=="none"):
           dispatcher.utter_message("Kindly input your registration id- cell number to begin the interview.")
           return[FollowupAction("action_listen"),SlotSet('counter', counter),SlotSet('current', current) ]
      else:
           dispatcher.utter_message("Continue plz.")
           return[]
        


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
        last_intent= tracker.latest_message['intent'].get('name')
        last_message= tracker.latest_message['text']
        
        dispatcher.utter_message(last_intent)
        
        if current==counter=="action_interview_start":
          counter="action_fetch_details"
          
        if last_intent=="chitchat":
          dispatcher.utter_message("This is an interview, ill ask again!!")
          return[FollowupAction(current)]
        elif len(last_message)==0:
          dispatcher.utter_message("Please dont leave replies blank, ill ask again!!")
          return[FollowupAction(current)]
        else:
         
         #dispatcher.utter_message(last_intent)
         if counter=="action_business_kind":
           if last_intent=="pvt":
             #dispatcher.utter_message("Got it u meant private!")
             counter="action_private"
           elif last_intent== "public":
             #dispatcher.utter_message("Got it u meant public!")
             counter= "action_public"
           elif last_intent=="prop":
             #dispatcher.utter_message("Got it u meant proprietery!")
             counter="action_prop_business_years_explain"
           elif last_intent== "partnership":
             #dispatcher.utter_message("Got it u meant partnership!")
             counter="action_partner"
           else:
             dispatcher.utter_message("Not understood!")
             counter="action_business_kind"
        
         if counter == "action_nob_fallback":
           if last_intent=="manufacturing":
             dispatcher.utter_message("Got it u meant manufacturing!")
             counter= "action_manu_loc"
           elif last_intent=="SP":
             dispatcher.utter_message("Got it u meant service provider!")
             counter= "action_sp_order"
           elif last_intent== "trader":
             dispatcher.utter_message("Got it u meant Trader!")
             counter= "action_trader"
           else:
             dispatcher.utter_message("Not understood!")
             counter="action_nob"
         if counter=="end":
           dispatcher.utter_message("Thanks for your time!!")
           return[FollowupAction("action_restart")]
         return[FollowupAction(counter)]



class ActionBusinessKind(Action):
    
    def name(self):
        return "action_business_kind"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("What kind of business do you have?\n-Private ltd(pvt)\n-Public ltd(pub)\n-Proprietery(prop)\n-Partnership(partner)")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter=current="action_business_kind"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionPrivate(Action):
    
    def name(self):
        return "action_private"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("Can you please name the directors and their respective shareholding patterns?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      current="action_private"
      counter="action_business_years"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionPartner(Action):
    
    def name(self):
        return "action_partner"
    def run(self, dispatcher, tracker, domain):
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
      dispatcher.utter_message("Is it listed on any stock market?\n-Yes\n-No")
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
        counter="action_industry_type"
        current="action_business_years"
        return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionPropBusinessYearsExplain(Action):
    
    def name(self):
        return "action_prop_business_years_explain"
    def run(self, dispatcher, tracker, domain):
        user_name = tracker.get_slot('user_name')
        dispatcher.utter_message("{} what was it that you were working in, before this venture?".format(user_name))
        #ActionSave.run('action_save',dispatcher, tracker, domain)
        counter="action_industry_type"
        current="action_prop_business_years_explain"
        return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionIndustryType(Action):
    
    def name(self):
        return "action_industry_type"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("What is the industry type?\nTextile\n-Readymade\n-Clothes\n-Electronics\n-Fmcg\n-Groceries\n-Any other plz specify")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_nob"
      current="action_industry_type"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionNob(Action):
    
    def name(self):
        return "action_nob"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("What is the nature of business:\n-Manufacturing(Manu)\n-Trader(retail/wholesale)\n-Service-Provider(SP)")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_nob_fallback"
      current="action_nob"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]


class ActionManuLoc(Action):
    
    def name(self):
        return "action_manu_loc"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("Where is the manufacturing unit, please specify the address(all if more)")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_manu_unit_manage"
      current="action_manu_loc"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionManuUnitManage(Action):
    
    def name(self):
        return "action_manu_unit_manage"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("How do you manage the oversee of manufacture unit.")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_manu_machine"
      current="action_manu_unit_manage"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionManuMachine(Action):
    
    def name(self):
        return "action_manu_machine"
    def run(self, dispatcher, tracker, domain):
        user_name=tracker.get_slot("user_name")
        dispatcher.utter_message("How many machines do you have in the specified manufacturing locations {}?".format(user_name))
        #ActionSave.run('action_save',dispatcher, tracker, domain)
        counter="action_manu_workers"
        current="action_manu_machine"
        return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionManuWorkers(Action):
    
    def name(self):
        return "action_manu_workers"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("How many workers work in the manufacturing location(s)")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_manu_utl"
      current="action_manu_workers"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionManuUtl(Action):
    
    def name(self):
        return "action_manu_utl"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("What is the total capacity for productions and what is the average utilization?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_purchase_parties"
      current="action_manu_utl"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionTrader(Action):
    
    def name(self):
        return "action_trader"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("What kind of Trader are you into:\n-Retail\n-Wholesale\n-Both retail and wholesale")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_trader_galla"
      current="action_trader"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionTraderGalla(Action):
    
    def name(self):
        return "action_trader_galla"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("What is the Daily walkin sale or the daily galla")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_trader_godown"
      current="action_trader_galla"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionTraderGodown(Action):
    
    def name(self):
        return "action_trader_godown"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("Where do you stock your goods/inventory?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_trader_logistics"
      current="action_trader_godown"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionTraderLogistics(Action):
    
    def name(self):
        return "action_trader_logistics"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("How do you manage the logistics. Please explain")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_purchase_parties"
      current="action_trader_logistics"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionSpOrder(Action):
    
    def name(self):
        return "action_sp_order"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("What are the orders/contracts in hand")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_sp_order2"
      current="action_sp_order"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionSpOrder2(Action):
    
    def name(self):
        return "action_sp_order2"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("Are these orders renewed every year")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_purchase_parties"
      current="action_sp_order2"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionPurchaseParties(Action):
    
    def name(self):
        return "action_purchase_parties"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("Are there any specific parties you buy your goods/raw material from. Please name them?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_purchase_payment"
      current="action_purchase_parties"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionPurchasePayment(Action):
    
    def name(self):
        return "action_purchase_payment"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("What are the payment terms with your suppliers?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_credit_outstanding"
      current="action_purchase_payment"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionCreditOutstanding(Action):
    
    def name(self):
        return "action_credit_outstanding"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("How much creditors outstanding/trade payable as of date OR what is the credit position as of date")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_stock_level"
      current="action_credit_outstanding"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionStockLevel(Action):
    
    def name(self):
        return "action_stock_level"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("What stock levels are maintained?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_sell_parties"
      current="action_stock_level"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionStockLevel2(Action):
    
    def name(self):
        return "action_stock_level2"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("Is it inclusive of raw material, wip, finished goods")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_sell_parties"
      current="action_stock_level2"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionSellParties(Action):
    
    def name(self):
        return "action_sell_parties"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("Where all do you sell your products, please name the major buyers?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_sell_payment"
      current="action_sell_parties"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionSellPayment(Action):
    
    def name(self):
        return "action_sell_payment"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("Please explain the payment terms with your buyers/clients.")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_debt_outstanding"
      current="action_sell_payment"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionDebtOutstanding(Action):
    
    def name(self):
        return "action_debt_outstanding"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("How much is the outstanding debtor the trade receivables as of date.")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_monthly_sales"
      current="action_debt_outstanding"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



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
      counter="action_gst"
      current="action_employees"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionGst(Action):
    
    def name(self):
        return "action_gst"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("what are the GST margins")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_gst_status"
      current="action_gst"
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
      counter="action_ubl_follow"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionUBLFollow(Action):
    
    def name(self):
        return "action_ubl_follow"
    def run(self, dispatcher, tracker, domain):
      
      dispatcher.utter_message("ubl_follow_up under construction!!..Please hit enter for Now!")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_ubl_enquiry"
      current="action_ubl_follow"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionUBLEnquiry(Action):
    
    def name(self):
        return "action_ubl_enquiry"
    def run(self, dispatcher, tracker, domain):
      current="action_ubl_enquiry"
      user_cell=tracker.get_slot('user_cell')
      enquiry=int(df[df.applicant_1_phone==int(user_cell)].ubl_enquiry.item())  
      #put scop for 0 enquiry
      dispatcher.utter_message("""You have applied for a UBL at {} different loan providers. Why have you not taken
                               loan from any one of the other {}""".format(enquiry, enquiry-1))
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_gl"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionGL(Action):
    
    def name(self):
        return "action_gl"
    def run(self, dispatcher, tracker, domain):
      #gl=10
      current="action_gl"
      user_cell=tracker.get_slot('user_cell')
      gl=int(df[df.applicant_1_phone==int(user_cell)].gold_loan.item())  
      

      if gl>0:
       dispatcher.utter_message("You have {} gold loans running, is this true?".format(gl))
       #ActionSave.run('action_save',dispatcher, tracker, domain)
       counter="action_bto"
       return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]
      else:
       counter="action_bto"
       return [FollowupAction(counter),SlotSet('counter', counter),SlotSet('current', current) ]



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
      counter="action_cd"
      current="action_emi_bounce"
#      emi_bounce=3
      user_cell=tracker.get_slot('user_cell')
      emi_bounce=int(df[df.applicant_1_phone==int(user_cell)].emi_bounce_6.item())  
      

      if emi_bounce > 0:
       dispatcher.utter_message("You have bounced on your emis {} times in the past year. Can you please explain".format(emi_bounce))
       #ActionSave.run('action_save',dispatcher, tracker, domain)
       return[SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current)]
      else:
       return[FollowupAction(counter),SlotSet('counter', counter),SlotSet('current', current)]
       


class ActionCD(Action):
    
    def name(self):
        return "action_cd"
    def run(self, dispatcher, tracker, domain):
      current="action_cd"
      
      dispatcher.utter_message("Credit depleting doubts under-construction!!!..Please hit enter for Now!")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_mcd"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionMCD(Action):
    
    def name(self):
        return "action_mcd"
    def run(self, dispatcher, tracker, domain):
      current="action_mcd"
      dispatcher.utter_message("Doubts on monthy credits under-construction!!!..Please hit enter for Now!")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_hvc"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]



class ActionHVC(Action):
    
    def name(self):
        return "action_hvc"
    def run(self, dispatcher, tracker, domain):
      current="action_hvc"
      dispatcher.utter_message("Doubts on High Value Credits under-construction!!!..Please hit enter for Now!")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="end"
      return [SlotSet('counter', counter),FollowupAction("action_listen"),SlotSet('current', current) ]
