
from experta import *
import pandas as pd 
from Boufybot import phrases as bot_phrs
from Boufybot import occasions
from Facts_classes import * 
import random


matched_colors = pd.read_csv("Data/matched_color.csv")
clothes = pd.read_csv("Data/clothes.csv")
mycloset_clothes = pd.read_csv("Data/mycloset.csv")


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
                        size =clothes.loc[i , "size"] )
    
        # * import Colors match each other
        for i in matched_colors.index:
            yield Color_Matched(matched_colors.loc[i , "color1"] , matched_colors.loc[i , "color2"] , matched = matched_colors.loc[i , "match"] )

    # ------------------------------------------------------------
    # ! - Gathering Data -

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
        print("Boufy will not share any information about you , it's our secret...😊")
        self.declare(Data_collected(True))
        print()
        print("one more thing 😊, do you want to allow Boufy to access your closet's clothes")
        print("this will help to have better experience with boufy , [yes/no]")
        In = True if input()=="yes" else False
        if(In):
            self.declare(IncludeMy_closet(True))

    @Rule(IncludeMy_closet(True))
    def includeCloset(self):
        # * import clothes
        for i in mycloset_clothes.index:
            self.declare(
                My_closet(
                    name= clothes.loc[i , "name"] ,
                    color=clothes.loc[i , "color"]  ,
                    category=clothes.loc[i , "category"],
                    size =clothes.loc[i , "size"] 
                )
            )
        print("your closet imported successfully")

    @Rule(AskQustion(True))
    def ask(self):
        print(random.choice(bot_phrs["greets"]))
        print("Boufy needs some information about you...😊 ")

    @Rule(Data_collected(True) , ~Occasion(W()))
    def ask_about_occasion(self ):
        print(random.choice(bot_phrs["ask_occasion"]))
        while(True):
            In = input()  
            if(In not in occasions):
                print("Boufy cannot recgonize the occasion  you have entered !")
                print("please enter it proberly :" ,end=" ")
                print(occasions.keys())
            else:
                break
        txt = occasions[In][0]
        for i in range(1,len(occasions[In])-1):
            txt+=" , "+ occasions[In][i]
        txt+=" or "+ occasions[In][len(occasions[In])-1]
        
        print("can you tell me whether it's " + txt)
        while(True):
            occ = input()
            flag = False 
            # To check if the input string contains one of the occasions
            for subocc in occasions[In]:
                if(subocc in occ):
                    self.declare(Occasion(subocc))
                    flag=True
                    break
            if(flag):
                break
            print("Boufy cannot recgonize what you have entered !")
            print("try again with one of those : "+txt)
    

    # ------------------------------------------------------------------------------
    # ! - suggestion Section -

    @Rule(  Cloth(name=MATCH.name1 ,color=MATCH.color1  , category=W(),size=W()),
            Cloth(name=MATCH.name2 ,color=MATCH.color2  , category=W(),size=W()),
            Color_Matched(MATCH.color1 , MATCH.color2 , matched =MATCH.percentage),
            TEST(lambda percentage : int(percentage)>30),
            Occasion(W())
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

myStylistEngine = MyStylist_Engine()
myStylistEngine.reset()
myStylistEngine.run()
