# rasa
Rasa Open Source Interview Bot

- This is an AI bot built on Rasa Stack.
- Purpose is to take on interviews.
- Rasa uses two sets of deep learning frameworks.
  -1) For intent classification, also called Rasa NLU.
  -2) For flow of converstaions. It gets trained on the stories(as rasa calls it). 
      Every utterance is classified as some intent by the NLU and it also extracts the slots, which might be
      names/ time locations etc. We train a model also called rasa_core on this data and thus predict the next action 
      after each utterance from the user.
- Here we have skipped the 2nd deep learning model. Why? The interview is a set of some 50-60 questions which obviously
  change according to the flow of the interview. Now to predict this long conversations the lstms don't work very accurately, moreover 
  I need a big big database on the sample stories to train the model. With not enough resources to develop this database I tried 
  another approach.
- I have hardcoded the decision tree for the questions flow.
- so why is it different from a basic form filling?
  - Yepp, its quite better then that. I am analyzing all the utterances by user through the NLU model or some other custom
    codes I have written in the actions file. Basically all the user utterances are getting understood by the bot, but it is taking
    actions on them only when its needed. E.g. when bot asks you the time you have been with the business, it reacts differently 
    to the different timelines you give. But when he asks for your address, it just moves on by digesting your answer.
    
- This just makes the bot more robust on starting and finishing the interview.

