from experta import Fact,Field

INFO = ["prefered_color", "shirt_size" ,
"pants_size" ,"shoe_size" ,
"age" , "hieght"]

class Color_Matched(Fact):
    pass

class Cloth(Fact):
    name = Field(str , True)
    color = Field(str , True)
    category = Field(str , True)
    size = Field(any , True)

# * A class express the clothes the user has 
class My_closet(Fact):
    cloth_id = Field(str , True)

class Info(Fact):
   pass

# a class express the occasion the user wants to attend if any 
class Occasion(Fact):
    pass

class Ask(Fact):
    pass
class AskQustion(Fact):
    pass

class Data_collected(Fact):
    pass