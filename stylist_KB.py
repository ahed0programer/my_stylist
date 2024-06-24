
from experta import *
from Facts_classes import * 
import pandas as pd 
from Boufybot import  occasions, phrases as bot_phrs
import random


matched_colors = pd.read_csv("Data/matched_color.csv")
clothes = pd.read_csv("Data/clothes.csv")
mycloset_clothes = pd.read_csv("Data/mycloset.csv")
occasions_formality = pd.read_csv("Data/occasion_class.csv")
occasions_wear = pd.read_csv("Data/occasion_wear.csv")
category=""

class MyStylist_Engine(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.suggestions = []
        self.suggestions_num = 0
        self.max_suggestions =10

    @DefFacts()
    def init_Data(self):
        for info in INFO:
            yield Ask(info)

        yield AskQustion(True)

        # creating Facts from data stored as a CSV files
        # * import clothes from the closet
        for i in mycloset_clothes.index:
            yield Cloth(name= mycloset_clothes.loc[i , "name"] ,
                        color=mycloset_clothes.loc[i , "color"]  ,
                        category=mycloset_clothes.loc[i , "category"],
                        size =mycloset_clothes.loc[i , "size"] ,
                        formality =mycloset_clothes.loc[i , "formality"] /100,
                        have_it=True
                    )

    
        # * import Colors match each other
        for i in matched_colors.index:
            yield Color_Matched(matched_colors.loc[i , "color1"] , matched_colors.loc[i , "color2"] , matched = matched_colors.loc[i , "match"]/100 )

        # * import occasions formality
        for i in occasions_formality.index:
            yield Occasion_Formality(occasion = occasions_formality.loc[i , "ocassion"] , formality=occasions_formality.loc[i , "formality"]/100)

        # * import what should be wore
        for i in occasions_wear.index:
            yield Occasion_Wear(occasion = occasions_wear.loc[i , "ocassion"] , should_wear=occasions_wear.loc[i , "should_wear"] , matched = float(occasions_wear.loc[i , "match"])/100)

    # ------------------------------------------------------------
    # ! - Gathering Data -

    @Rule(AskQustion(True))
    def ask(self):
        print(random.choice(bot_phrs["greets"]))
        print("Boufy needs some information about you...😊 ")

    @Rule(AS.f << Ask(MATCH.needed_data),
          ~Info(needed_data=W()))
    def collect_Data(self ,needed_data ,f):
        print(random.choice(bot_phrs["collect_data"][needed_data]))
        In = input()
        self.declare(Info(**{needed_data:In}))
        if(needed_data=="category"):
            global category
            category=In
        self.retract(f)

    @Rule(~ Ask(W()))
    def end_collecting_data(self):
        print("thanks for the information you provided , I can now be more specific about you ")
        print("Boufy will not share any information about you , it's our secret...😊")
        self.declare(Data_collected(True))
        print()
        print("one more thing 😊,By default Boufy will give you suggestions from your closet' clothes")
        print("do you want Boufy to give you suggestions in general Despite of yours ?? , [yes/no]")
        while(True):
            In = input()
            if(In=="yes"):
                self.declare(Include_GeneralClothes(True))
                break
            elif(In=="no"):break
            else:print("please answer with [yes/no] : ",end='')

    @Rule(Include_GeneralClothes(True))
    def includeclothesFromStore(self):
        # * import clothes
        for i in clothes.index:
            self.declare(
                Cloth(
                    name= clothes.loc[i , "name"] ,
                    color=clothes.loc[i , "color"]  ,
                    category=clothes.loc[i , "category"],
                    size =clothes.loc[i , "size"] ,
                    formality =clothes.loc[i , "formality"] /100,
                    have_it=False
                )
            )
        print("your closet imported successfully")

    @Rule(Data_collected(True) , ~Occasion(W()))
    def ask_about_occasion(self ):
        print(random.choice(bot_phrs["ask_occasion"]))
        while(True):
            In = input()  
            flag = False 
            # To check if the input string contains one of the occasions
            for subocc in occasions:
                if(subocc in In):
                    In=subocc
                    flag=True
                    break
            if(flag):
                break
            
            print("Boufy cannot recgonize the occasion  you have entered !")
            print("please enter it proberly :" ,end=" ")
            print(occasions.keys())
    
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

    @Rule( 
            Info(prefered_color=MATCH.prefered_color),
            Info(shirt_size=MATCH.shirt_size),
            Info(pants_size=MATCH.pants_size),
            Info(shoe_size=MATCH.shoe_size),
            Info(category=MATCH.category),
            Occasion(MATCH.occasion),
            Occasion_Formality(occasion=MATCH.occasion , formality = MATCH.occformality),
            AS.shirt << Cloth(name=MATCH.name1 ,color=MATCH.color1  , category="men/shirts",size=MATCH.shirt_size, formality=MATCH.formality1),
            AS.pants << Cloth(name=MATCH.name2 ,color=MATCH.color2  , category="men/pants",size=MATCH.pants_size , formality=MATCH.formality2),
            AS.shoes << Cloth(name=MATCH.name3 ,color=MATCH.color3  , category="men/shoes",size=MATCH.shoe_size , formality=MATCH.formality3),
            TEST(lambda formality1 , formality2 ,formality3 : formality1 - formality3<0.2 and formality1 - formality2<0.2),
            Color_Matched(MATCH.color1 , MATCH.color2 , matched =MATCH.color_consistancy1),
            Color_Matched(MATCH.color1 , MATCH.color3 , matched =MATCH.color_consistancy2),
            TEST(lambda color_consistancy1 , color_consistancy2 : color_consistancy1*color_consistancy2>0.2),
            salience=10
          )
    def check_matched_clothes(self ,color1 , prefered_color ,shirt , pants , shoes , occformality , formality1 , formality2 ,formality3 , color_consistancy1 ,color_consistancy2 ):
        formality = (formality1+formality2+formality3)/3
        formality = 1-(occformality-formality)
        order  = formality*color_consistancy1*color_consistancy2
        if(prefered_color==color1):
            order+=abs(order*1.4)
        outfit = {
            "color":color1,
            "shirt":shirt,
            "pants":pants,
            "shoes":shoes,
            "order":order,
            "watch":None,
            "watch_certainty":0,
            "hat":None,
            "hat_certainty":0
        }
        self.declare(Outfit(**outfit))

    @Rule(
        AS.outfit << Outfit(color=MATCH.color ,shirt=W(),pants=W(), shoes=W(),order=MATCH.order , watch=MATCH.watch_value, hat=W()),
        Occasion(MATCH.occasion),
        Occasion_Wear(occasion = MATCH.occasion , should_wear="watch" , matched = MATCH.watch_certainty),
        AS.watch << Cloth(name=MATCH.name ,color=MATCH.color1 , category="men/watches",size=W() , formality=W()),
        Color_Matched(MATCH.color,MATCH.color1 ,matched= MATCH.color_consistancy),
        TEST(lambda color_consistancy:color_consistancy>0.5),
        TEST(lambda watch_value: watch_value is None),
        salience=10
    )
    def scondary_style_watch(self,outfit ,watch , watch_certainty ):
        self.modify(outfit, watch= watch ,watch_certainty= watch_certainty)

    @Rule(
        AS.outfit << Outfit(color=MATCH.color ,shirt=W(),pants=W(), shoes=W(),order=MATCH.order ,watch=W() ,hat=MATCH.hat_value),
        Occasion(MATCH.occasion),
        Occasion_Wear(occasion = MATCH.occasion , should_wear="hat" , matched = MATCH.hat_certainty),
        AS.hat << Cloth(name=MATCH.name ,color=MATCH.color1 , category="men/hats",size=W() , formality=W()),
        Color_Matched(MATCH.color,MATCH.color1 ,matched= MATCH.color_consistancy),
        TEST(lambda color_consistancy:color_consistancy>0.5),
        TEST(lambda hat_value: hat_value is None),
        salience=10,
    )
    def scondary_style_hat(self,outfit ,hat , hat_certainty ):
        self.modify(outfit, hat= hat ,hat_certainty= hat_certainty)
    
    @Rule(AS.outfit<<Outfit(color=MATCH.color,shirt=MATCH.shirt,pants=MATCH.pants, shoes=MATCH.shoes,order=W(),watch=W(),watch_certainty=W() , hat=W() ,hat_certainty=W()) ,salience=5)
    def collect_outfit(self , outfit):
        self.suggestions.append(outfit)
        self.suggestions.sort(key=lambda x: x["order"] ,reverse=True)
        if(len(self.suggestions)>=self.suggestions_num):
            self.declare(End_Suggestion(True))


    @Rule(End_Suggestion(True) ,salience=1)
    def suggest_style(self):
        recommand_message = "I suggest you to wear"
        for suggestion in self.suggestions:
            if(suggestion['shirt']['have_it']):
                shirt_Text=f"your {suggestion['color']} {suggestion['shirt']['name']}👕"
            else:
                shirt_Text=f"a {suggestion['color']} {suggestion['shirt']['name']}👕 (you need to buy one !!)"
            if(suggestion['pants']['have_it']):
                pants_Text=f"your {suggestion['pants']['color']} {suggestion['pants']['name']} 👖"
            else:
                pants_Text=f"a {suggestion['pants']['color']} {suggestion['pants']['name']} 👖 (you need to buy one  !!)"
            if(suggestion['shoes']['have_it']):
                shoes_Text=f"your {suggestion['shoes']['color']} {suggestion['shoes']['name']} 👟"
            else:
                shoes_Text=f"a {suggestion['shoes']['color']} {suggestion['shoes']['name']} 👟 (you need to buy one !!)"
                
            print(recommand_message+f""" {shirt_Text} with {pants_Text} and {shoes_Text}""")

            if(suggestion["watch_certainty"]>0.2):
                prefix,suffix  = self.getMessagefromCertainty(suggestion["watch_certainty"])
                print(prefix+f"{suggestion['watch']['color']} {suggestion['watch']['name']} ⌚ , {suffix}")
            if(suggestion["hat_certainty"]>0.2):
                prefix,suffix  = self.getMessagefromCertainty(suggestion["hat_certainty"])
                print(prefix+f"{suggestion['hat']['color']} {suggestion['hat']['name']} 🧢👒 , {suffix}")
            print("tell me if you like it or not , so I can give you other options [yes/no]")
            In = input()
            if(In=="yes"):
                print("well done , hope you came back for best style advice from Boufy 😊")
                break
            print("----------------------------------------------")
            reactions = ["hmmm 😕 , watch this : " ,
                          "well 🤔 ! what about " ,
                          "🤔 what about ",
                          "😒 what about "
                          "let me think 😕 ! what about " ,
                          "your taste is hard 😒 , give me your opinion in this : "]
            react = random.choice(reactions)
            recommand_message=f"{react}"
        if(not In=="yes"):
            print("Damn you 😠!! , nothing is good for you now ,then go to carbbage and find some dirty bags and wear 😒😒 ")
                
    def getMessagefromCertainty(self , certainty):
        if(certainty>=0.9):
            return "for a perfect style 👌 you have to wear a " , "the style cannot be without it ✨✨ "
        elif(certainty>=0.6):
            return "it will be good if you wear a " , "a complete outfit makes perfect style 👌✨"
        elif(certainty>=0.3):
            return "if you love to, you can wear a " , "but I do not recommand it in this occasion 😕😕"
        else:
            return "it will be bad if you wear a " , "Do not wear if you think about it 🙅❌  "
