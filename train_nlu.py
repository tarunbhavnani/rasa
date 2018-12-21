#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 21 15:54:59 2018

@author: tarun.bhavnani@dev.smecorner.com
"""
from rasa_nlu.training_data import load_data
from rasa_nlu import config
from rasa_nlu.model import Trainer
from rasa_nlu.model import Metadata, Interpreter
def train_nlu(data="data/nlu_data.md", configs="nlu_config.yml", model_dir="models/nlu"):
	training_data = load_data(data)
	trainer = Trainer(config.load(configs))
	trainer.train(training_data)
	model_directory = trainer.persist(model_dir, fixed_model_name = 'latest_nlu')
    
    
if __name__ == "__main__":
  train_nlu()
