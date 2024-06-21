
from experta import *
import pandas as pd 
from Boufybot import phrases as bot_phrs
from Facts_classes import * 
import random


matched_colors = pd.read_csv("matched_color.csv")
clothes = pd.read_csv("clothes.csv")


class MyStylist_Engine(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.suggestions = []
        self.suggestions_num = 0

    @DefFacts()
    def init_Data(self):
        for info in INFO:
            yield Ask(info)

        yield AskQustion(True)

        # creating Facts from data stored as a CSV files
        # * import clothes
        for i in clothes.index:
            yield Cloth(name= clothes.loc[i , "name"] ,
                        color=clothes.loc[i , "color"]  ,
                        category=clothes.loc[i , "category"],
                        size =clothes.loc[i , "size"] );
    
        # * import Colors match each other
        for i in matched_colors.index:
            yield Color_Matched(matched_colors.loc[i , "color1"] , matched_colors.loc[i , "color2"] , matched = matched_colors.loc[i , "match"] )
             

    @Rule(  Cloth(name=MATCH.name1 ,color=MATCH.color1  , category=W(),size=W()),
            Cloth(name=MATCH.name2 ,color=MATCH.color2  , category=W(),size=W()),
            Color_Matched(MATCH.color1 , MATCH.color2 , matched =MATCH.percentage),
            TEST(lambda percentage : int(percentage)>50),
            Data_collected(True)
          )
    def check_matched_clothes(self , name1  ,color1, name2 , color2):
        self.suggestions.append(f"you can wear :{color1} {name1} with {color2} {name2}")
        self.suggestions_num+=1
        if(self.suggestions_num>10):
            self.declare(Fact(suggestions_num=True))
        # print(f"you can wear :{color1} {name1} with {color2} {name2} ")

    @Rule(Fact(suggestions_num=True))
    def suggest_style(self):
        for i,x in enumerate(self.suggestions):
            print(x)

    @Rule()
    def suggest_clothToBuy(self):
        pass


    @Rule(AS.f << Ask(MATCH.needed_data),
          ~Info(needed_data=W()))
    def collect_Data(self ,needed_data ,f):
        print(random.choice(bot_phrs["collect_data"][needed_data]))
        In = input()
        self.declare(Info(**{needed_data:In}))
        self.retract(f)

    @Rule(~ Ask(W()))
    def end_collecting_data(self):
        print("thanks for the information you provided , I can now be more specific about you ")
        print("Boufy will not share any information about you , its our secret...😊")
        self.declare(Data_collected(True))
        print("gotcha , here you are ............")


    @Rule(AskQustion(True))
    def ask(self):
        print(random.choice(bot_phrs["greets"]))
        print("Boufy needs some information about you...😊 ")

myStylistEngine = MyStylist_Engine()
myStylistEngine.reset()
myStylistEngine.run()
