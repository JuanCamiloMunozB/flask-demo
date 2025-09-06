from abc import ABC, abstractmethod
from experta import KnowledgeEngine, Fact
from pgmpy.inference import VariableElimination

class BaseExpert(KnowledgeEngine, ABC):
    """
    Base class for sport-specific knowledge bases.
    All sport implementations should inherit from this.
    """

    # def __init__(self):
    #     self.counter = 0

    @abstractmethod
    def get_sport_name(self):
        """Return the name of the sport this knowledge base handles."""
        pass
    
    def get_next_question(self, facts, fact_cls=Fact):
        """
        Get the next question to ask the user based on the current state of the knowledge base.
        This method should be overridden in sport-specific implementations.
        """
        self.reset()
        for fact_dict in facts:
            if isinstance(fact_dict, dict):
                self.declare(fact_cls(**fact_dict))
        self.run()

        for fact in self.facts.values():
                if "question" in fact:
                    return {"question": fact["question"], "next_fact": fact["next_fact"]}
                if "result" in fact:
                    return {"result": fact["result"]}

        # self.counter += 1

        # if self.counter <= 1 :
        #     return {"question": "¿Cuál es el deporte?", "next_fact": "sport"}
        # else:
        #     return {"result": "No hay recomendaciones disponibles."}
            
            


class BaseBayesianNetwork(ABC):
    """
    Base class for sport-specific Bayesian networks.
    All sport implementations should inherit from this.
    """
    def __init__(self):
        """Initialize the Bayesian network."""
        self.model = self.create_network()
        self.inference = VariableElimination(self.model)

    @abstractmethod
    def create_network(self):
        """Create and return the Bayesian network for this sport."""
        pass