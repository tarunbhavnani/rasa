this repository is for the final codes of rasa work 
-every question has a current, counter and followup
- current is the name of current action, counter is the name of next action, followup is the next action
- followup is mostly listen unless listining has to be skipped
- no stories are provided, hence it goes to action default fallback for each next action
- in default fallback it checks the current, counter and the intent of the reply.
- theses three combine and define the next action, which is pushed by action followup
