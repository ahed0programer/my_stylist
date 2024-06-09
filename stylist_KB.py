
from experta import *
import pandas as pd 

matched_colors = pd.read_csv("matched_color.csv")
clothes = pd.read_csv("clothes.csv")

class Color_Matched(Fact):
    pass


class Cloth(Fact):
    name = Field(str , True)
    color = Field(str , True)
    category = Field(str , True)
    size = Field(any , True)

# * A class express the clothes the user has 
class My_closet(Fact):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    cloth_id = Field(str , True)

# a class express the occasion the user want to attend if any 
class Occasion(Fact):
    pass

class MyStylist_Engine(KnowledgeEngine):
    def __init__(self):
        super().__init__()

    @DefFacts()
    def init_Data(self):
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
            Color_Matched(MATCH.color1 , MATCH.color2 , matched =True )
          )
    def suggest_style(self , name1  ,color1, name2 , color2):
        print(f"you can wear :{color1} {name1} with {color2} {name2} ")


    @Rule()
    def suggest_clothToBuy(self):
        pass

myStylistEngine = MyStylist_Engine()
myStylistEngine.reset()
myStylistEngine.run()
# print(myStylistEngine.facts)