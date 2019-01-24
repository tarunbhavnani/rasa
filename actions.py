
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
      user_name = tracker.get_slot('user_name')
      user_cell=tracker.get_slot('user_cell')
        
      if (user_name=="Dear" and user_cell=="none"):
           dispatcher.utter_message("Kindly input your registration id- cell number to begin the interview.")
           return[FollowupAction("action_listen"),SlotSet('counter', counter)]
      else:
           dispatcher.utter_message("Continue plz.")
           return[]
        

# the actions which have bifurcations are bifurcated in fallback as well see below:
class ActionDefaultFallback(Action):
    def name(self):
        #return "action_question_counter"
        return 'action_default_fallback'
    def run(self, dispatcher, tracker, domain):
        #text= tracker.latest_message['text']
        #interpreter = RasaNLUInterpreter('./models/nlu/default/latest_nlu')
        #last_intent=interpreter.parse(text)['intent_ranking'][0]
        counter= tracker.get_slot('counter')
        last_intent= tracker.latest_message['intent'].get('name')
        dispatcher.utter_message("placeholder")
        #dispatcher.utter_message(last_intent)
        if counter=="action_business_kind":
          if last_intent=="pvt":
            dispatcher.utter_message("Got it u meant private!")
            counter="action_private"
          elif last_intent== "public":
            dispatcher.utter_message("Got it u meant public!")
            counter= "action_public"
          elif last_intent=="prop":
            dispatcher.utter_message("Got it u meant proprietery!")
            counter="action_prop_business_years_explain"
          elif last_intent== "partnership":
            dispatcher.utter_message("Got it u meant partnership!")
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
            counter="action_business_kind"
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
      counter="action_business_kind"
      return [SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionPrivate(Action):
    
    def name(self):
        return "action_private"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("Can you please name the directors and their respective shareholding patterns?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_business_years"
      return [SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionPartner(Action):
    
    def name(self):
        return "action_partner"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("Can you please name the partners and their respective ownership in the venture?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter= "action_partner_explain"
      return [SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionPartnerExplain(Action):
    
    def name(self):
        return "action_partner_explain"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("Which all partners are actively involved in business.Please explain")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_business_years"
      return [SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionPublic(Action):
    
    def name(self):
        return "action_public"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("What is your shareholding in the company?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_public2"
      return [SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionPublic2(Action):
    
    def name(self):
        return "action_public2"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("Is it listed on any stock market?\n-Yes\n-No")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_business_years"
      return [SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionBusinessYears(Action):
    
    def name(self):
        return "action_business_years"
    def run(self, dispatcher, tracker, domain):
        user_name = tracker.get_slot('user_name')
        dispatcher.utter_message("How many years have you been in the business {}".format(user_name))
        #ActionSave.run('action_save',dispatcher, tracker, domain)
        counter="action_industry_type"
        return [SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionPropBusinessYearsExplain(Action):
    
    def name(self):
        return "action_prop_business_years_explain"
    def run(self, dispatcher, tracker, domain):
        user_name = tracker.get_slot('user_name')
        dispatcher.utter_message("{} what was it that you were working in, before this venture?".format(user_name))
        #ActionSave.run('action_save',dispatcher, tracker, domain)
        counter="action_industry_type"
        return [SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionIndustryType(Action):
    
    def name(self):
        return "action_industry_type"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("What is the industry type?\nTextile\n-Readymade\n-Clothes\n-Electronics\n-Fmcg\n-Groceries\n-Any other plz specify")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_nob"
      
      return [SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionNob(Action):
    
    def name(self):
        return "action_nob"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("What is the nature of business:\n-Manufacturing(Manu)\n-Trader(retail/wholesale)\n-Service-Provider(SP)")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_nob_fallback"
      
      return [SlotSet('counter', counter),FollowupAction("action_listen")]


class ActionManuLoc(Action):
    
    def name(self):
        return "action_manu_loc"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("Where is the manufacturing unit, please specify the address(all if more)")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_manu_unit_manage"
      return [SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionManuUnitManage(Action):
    
    def name(self):
        return "action_manu_unit_manage"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("How do you manage the oversee of manufacture unit.")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_manu_machine"
      return [SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionManuMachine(Action):
    
    def name(self):
        return "action_manu_machine"
    def run(self, dispatcher, tracker, domain):
        user_name=tracker.get_slot("user_name")
        dispatcher.utter_message("How many machines do you have in the specified manufacturing locations {}?".format(user_name))
        #ActionSave.run('action_save',dispatcher, tracker, domain)
        counter="action_manu_workers"
        return [SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionManuWorkers(Action):
    
    def name(self):
        return "action_manu_workers"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("How many workers work in the manufacturing location(s)")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_manu_utl"
      return [SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionManuUtl(Action):
    
    def name(self):
        return "action_manu_utl"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("What is the total capacity for productions and what is the average utilization?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_purchase_parties"
      return [SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionTrader(Action):
    
    def name(self):
        return "action_trader"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("What kind of Trader are you into:\n-Retail\n-Wholesale\n-Both retail and wholesale")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_trader_galla"
      return [SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionTraderGalla(Action):
    
    def name(self):
        return "action_trader_galla"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("What is the Daily walkin sale or the daily galla")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_trader_godown"
      return [SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionTraderGodown(Action):
    
    def name(self):
        return "action_trader_godown"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("Where do you stock your goods/inventory?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_trader_logistics"
      return [SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionTraderLogistics(Action):
    
    def name(self):
        return "action_trader_logistics"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("How do you manage the logistics. Please explain")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_purchase_parties"
      return [SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionSpOrder(Action):
    
    def name(self):
        return "action_sp_order"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("What are the orders/contracts in hand")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_sp_order2"
      return [SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionSpOrder2(Action):
    
    def name(self):
        return "action_sp_order2"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("Are these orders renewed every year")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_purchase_parties"
      return [SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionPurchaseParties(Action):
    
    def name(self):
        return "action_purchase_parties"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("Are there any specific parties you buy your goods/raw material from. Please name them?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_purchase_payment"
      return [SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionPurchasePayment(Action):
    
    def name(self):
        return "action_purchase_payment"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("What are the payment terms with your suppliers?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_credit_outstanding"
      return [SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionCreditOutstanding(Action):
    
    def name(self):
        return "action_credit_outstanding"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("How much creditors outstanding/trade payable as of date OR what is the credit position as of date")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_stock_level"
      return [SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionStockLevel(Action):
    
    def name(self):
        return "action_stock_level"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("What stock levels are maintained?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_sell_parties"
      return [SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionStockLevel2(Action):
    
    def name(self):
        return "action_stock_level2"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("Is it inclusive of raw material, wip, finished goods")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_sell_parties"
      return [SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionSellParties(Action):
    
    def name(self):
        return "action_sell_parties"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("Where all do you sell your products, please name the major buyers?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_sell_payment"
      return [SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionSellPayment(Action):
    
    def name(self):
        return "action_sell_payment"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("Please explain the payment terms with your buyers/clients.")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_debt_outstanding"
      return [SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionDebtOutstanding(Action):
    
    def name(self):
        return "action_debt_outstanding"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("How much is the outstanding debtor the trade receivables as of date.")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_monthly_sales"
      return [SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionMonthlySales(Action):
    
    def name(self):
        return "action_monthly_sales"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("Please specify the monthly sales.")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_turnover"
      return [SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionTurnover(Action):
    
    def name(self):
        return "action_turnover"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("What is the turnover till date from april this year and what is the expectation for the full year?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_cash"
      return [SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionCash(Action):
    
    def name(self):
        return "action_cash"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("What is cash component of the overall sales?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_gross_margins"
      return [SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionGrossMargins(Action):
    
    def name(self):
        return "action_gross_margins"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("What are the gross margins in the business")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_employees"
      return [SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionEmployees(Action):
    
    def name(self):
        return "action_employees"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("How many employees do you have?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_gst"
      return [SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionGst(Action):
    
    def name(self):
        return "action_gst"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("what are the GST margins")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_gst_status"
      return [SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionGstStatus(Action):
    
    def name(self):
        return "action_gst_status"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("Have you paid the latest gst bills?\n-Yes\n-No")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_loan_amount"
      return [SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionLoanAmount(Action):
    
    def name(self):
        return "action_loan_amount"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("What kind of loan amount are you looking at?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_end_use"
      return [SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionEndUse(Action):
    
    def name(self):
        return "action_end_use"
    def run(self, dispatcher, tracker, domain):
      dispatcher.utter_message("What do you plan to do with the loan money?")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_ubl"
      return [SlotSet('counter', counter),FollowupAction("action_listen")]


class ActionUBL(Action):
    
    def name(self):
        return "action_ubl"
    def run(self, dispatcher, tracker, domain):
      
      
      loan_amt=200000
      loan_num=6
      dispatcher.utter_message("According to my knowledge, you have a current outstanding ubl of {} in {} different loans. Please explain if anything has changed.".format(loan_amt, loan_num))
            
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_ubl_follow"
      return [SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionUBLFollow(Action):
    
    def name(self):
        return "action_ubl_follow"
    def run(self, dispatcher, tracker, domain):
      
      dispatcher.utter_message("action_ubl_follow")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_ubl_enquiry"
      return [SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionUBLEnquiry(Action):
    
    def name(self):
        return "action_ubl_enquiry"
    def run(self, dispatcher, tracker, domain):
      enquiry= 6
      dispatcher.utter_message("""You have applied for a UBL at {} different loan providers. Why have you not taken
                               loan from any one of the other {}""".format(enquiry, enquiry-1))
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_gl"
      return [SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionGL(Action):
    
    def name(self):
        return "action_gl"
    def run(self, dispatcher, tracker, domain):
      gl=10
      if gl>0:
       dispatcher.utter_message("You have {} gold loans running, is this true?".format(gl))
       #ActionSave.run('action_save',dispatcher, tracker, domain)
       counter="action_bto"
       return [SlotSet('counter', counter),FollowupAction("action_listen")]
      else:
       counter="action_bto"
       return [FollowupAction(counter),SlotSet('counter', counter)]



class ActionBTO(Action):
    
    def name(self):
        return "action_bto"
    def run(self, dispatcher, tracker, domain):
      counter="action_ccod"
      BTO=1.5
      if BTO>1:
       dispatcher.utter_message("Your BTO is {} Please explain why it is so high?".format(BTO))
       #ActionSave.run('action_save',dispatcher, tracker, domain)
       return [SlotSet('counter', counter),FollowupAction("action_listen")]
      elif BTO<0.2:
       dispatcher.utter_message("ask why low?")
       #ActionSave.run('action_save',dispatcher, tracker, domain
       return [SlotSet('counter', counter),FollowupAction("action_listen")]
      else:
        #dispatcher.utter_message("bto is {}".format(BTO))
        return[FollowupAction(counter),SlotSet('counter', counter)]

       



class ActionCCOD(Action):
    
    def name(self):
        return "action_ccod"
    def run(self, dispatcher, tracker, domain):
      counter="action_emi_bounce"
      ccod = 1
      if ccod==1:
        dispatcher.utter_message("Why CC/OD is depleating in the last 6 months?")
       # ActionSave.run('action_save',dispatcher, tracker, domain)
        return[SlotSet('counter', counter),FollowupAction("action_listen")] 
      else:
       return [FollowupAction(counter),SlotSet('counter', counter)]



class ActionEMIBounce(Action):
    
    def name(self):
        return "action_emi_bounce"
    def run(self, dispatcher, tracker, domain):
      counter="action_cd"
      emi_bounce=3
      if emi_bounce > 0:
       dispatcher.utter_message("You have bounced on your emis {} times in the past year. Can you please explain".format(emi_bounce))
       #ActionSave.run('action_save',dispatcher, tracker, domain)
       return[SlotSet('counter', counter),FollowupAction("action_listen")]
      else:
       return[FollowupAction(counter),SlotSet('counter', counter)]
       



class ActionCD(Action):
    
    def name(self):
        return "action_cd"
    def run(self, dispatcher, tracker, domain):
      
      dispatcher.utter_message("Credit depleting doubts!")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_mcd"
      return [SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionMCD(Action):
    
    def name(self):
        return "action_mcd"
    def run(self, dispatcher, tracker, domain):
      
      dispatcher.utter_message("Doubts on monthy credits!")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="action_hvc"
      return [SlotSet('counter', counter),FollowupAction("action_listen")]



class ActionHVC(Action):
    
    def name(self):
        return "action_hvc"
    def run(self, dispatcher, tracker, domain):
      
      dispatcher.utter_message("Doubts on High Value Credits!")
      #ActionSave.run('action_save',dispatcher, tracker, domain)
      counter="end"
      return [SlotSet('counter', counter),FollowupAction("action_listen")]
