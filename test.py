from experta import *

class Age(Fact):
    pass

class KBss(KnowledgeEngine):
    @Rule()
    def sd(self):
        self.declare(Age(age="3"))

    @Rule(Age(age=MATCH.age))
    def sss(self ,age):
        print(age)
    
kb = KBss()
kb.reset()
kb.run()
print(kb.facts)