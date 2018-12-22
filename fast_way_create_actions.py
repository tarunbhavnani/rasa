#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 22 13:53:00 2018

@author: tarun.bhavnani@dev.smecorner.com
"""

print("""
class {}(Action):
    
    def name(self):
        return "{}"

    def run(self, dispatcher, tracker, domain):
    
      this_action="{}"
      dispatcher.utter_message({})
      ActionSave.run('action_save',dispatcher, tracker, domain)
      
      return [SlotSet('last_action', this_action)]

""".format("ActionFamilyStay","action_family_stay","action_family_stay","'Where do you stay?'"))
  

class ActionFamilyStay(Action):
    
    def name(self):
        return "action_family_stay"
    
    def run(self, dispatcher, tracker, domain):
      
      this_action="action_family_stay"
      dispatcher.utter_message('Where do you stay?')
      ActionSave.run('action_save',dispatcher, tracker, domain)
      
      return [SlotSet('last_action', this_action)]
    
    
    
    