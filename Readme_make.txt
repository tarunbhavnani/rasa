
all the questions as actions they throw the last action as a slot which will be indeispensable to help the machine learn about next question.
limited slots
if multiple followup questions, we extraxt the last utternace by user and use it to find which qs to dispatch.


pip install 'prompt_toolkit==1.0.14'
pip install 'ipykernel<5.0.0'



##train n run
source activate rasa_new
cd Desktop/rasa_final_start

python train_nlu.py
#python train_core.py

#token not found-----------pip install 'prompt_toolkit==1.0.14'


#get in interactive learning and train
python -m rasa_core.train interactive -o models/dialogue -d domain.yml -s data/stories.md --nlu models/nlu/default/latest_nlu --endpoints endpoints.yml

#run
python -m rasa_core.run --core models/dialogue --nlu models/nlu/default/latest_nlu --endpoints endpoints.yml





##hwo build!!

1) create an action for every slot to be filled.

#current
interview start throws first question 
-user reverts with answer
-next action saves the slot for previous question and asks another question

#future
**every question has a seperate action!!no forms needed now!!
interview start throws first question 
-user reverts with answer
-next action saves the slot for previous question and creates one more slot entry which helps rasa core decide which 
action to run for the next question

