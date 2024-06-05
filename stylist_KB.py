from experta import *

class Cloth(Fact):
    name = Field(str , True)
    color = Field(str , True)
    category = Field(str , True)
    size = Field(any , True)

class My_closet(Fact):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    cloth_id = Field(str , True)

class Occasion(Fact):
    pass

class MyStylist_Engine(KnowledgeEngine):
    def __init__(self):
        super().__init__()

    @DefFacts()
    def init_Data():
        yield Cloth(name= "xhoof shirt" , color="red" , category="men/shirts" ,size ="large");
        yield Cloth(name= "xhoof shirt" , color="gray" , category="men/shirts" ,size ="Medium");
        



    @Rule()
    def suggest_style():
        pass

    @Rule()
    def suggest_clothToBuy():
        pass

  