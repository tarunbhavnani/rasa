from rasa_core.agent import Agent
from rasa_core.featurizers import MaxHistoryTrackerFeaturizer, BinarySingleStateFeaturizer,LabelTokenizerSingleStateFeaturizer
from rasa_core.policies.keras_policy import KerasPolicy
from rasa_core.policies.memoization import MemoizationPolicy
from rasa_core.policies.fallback import FallbackPolicy


fallback = FallbackPolicy(fallback_action_name="action_default_fallback",
                          core_threshold=0.6,
                          nlu_threshold=0.3)

#we have taken LabelTokenizerSingleStateFeaturizer instead of the normally used binary
def train_dialogue(domain_file, model_path, training_folder):
    

    agent = Agent(domain_file,
                  policies=[MemoizationPolicy(max_history=5),
                            KerasPolicy(MaxHistoryTrackerFeaturizer(BinarySingleStateFeaturizer(),max_history=5),
                                        epochs=300), fallback])


    training_data = agent.load_data(training_folder)

    agent.train(training_data)
    agent.persist(model_path)


if __name__ == "__main__":

    train_dialogue('domain.yml', 'models/dialogue', 'data/stories.md')



