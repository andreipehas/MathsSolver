
from kivy.app import App
from kivy.uix.camera import Camera
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image

from kivy.core.window import Window

from kivy.cache import Cache


Window.clearcolor = (1, 1, 1, 1)
Window.size = (1023, 1267)

################ equation.py
import sys
import base64
import requests
import json

def image_to_latex(file_path):
    image_uri = "data:image/jpg;base64," + base64.b64encode(open(file_path, "rb").read())
    r = requests.post("https://api.mathpix.com/v3/latex",
        data=json.dumps({'src': image_uri}),
        headers={"app_id": "robhoenig_gmail_com", "app_key": "9c9288a9292d9235c24d",
                "Content-type": "application/json"})
    result = json.loads(r.text)
    latex = result["latex"]
    return latex
################

################
from sympy import *                                                                   

def sympy_equation_to_png(equation, filename):
    preview(equation, viewer='file', filename=filename)
################

################ split latex into latex equations
def split_into_equations(s):
    if(len(s.split("\\\\"))>1):
        return s[27:-20].split("\\\\")
    else:
        return s.split("=")

from latex2sympy.process_latex import process_sympy
import sympy

# def check_equations_and_generate_pngs(latex_equations):
#     equations = [process_sympy(i[2:-2]) for i in latex_equations]
#     for i, equation in enumerate(equations):
#         sympy_equation_to_png(equation, "output"+str(i)+".png")
#     solution_sets = [sympy.solveset(i, domain=sympy.S.Complexes) for i in equations]
#     return [ i==solution_sets[0] for i in solution_sets]

def check_equations_and_generate_pngs(latex_equations):
    for i in latex_equations:
        print i
    is_multiple = len(latex_equations[0].split("="))>1
    if(is_multiple):
        equations_raw = [process_sympy(i[2:-2]) for i in latex_equations]
    else:
        equations_raw = [process_sympy(i) for i in latex_equations]
    for i, equation in enumerate(latex_equations):
        sympy_equation_to_png(equation, "output"+str(i)+".png")
    if(is_multiple):
        equations = [sympy.simplify((i.args[0]-i.args[1]).doit()) for i in equations_raw]
        for i in equations:
            print i, sympy.solveset(i, domain=sympy.S.Complexes)
        solution_sets = [sympy.solveset(i, domain=sympy.S.Complexes) for i in equations]
        return [True]+[solution_sets[i-1].is_subset(solution_sets[i]) for i in range(1, len(solution_sets))]
    else:
        equations = [sympy.simplify(i.doit()) for i in equations_raw]
        differences = [0]+[sympy.simplify(equations[i-1]-equations[i]) for i in range(1, len(equations))]
        for i, equation in enumerate(differences):
            sympy_equation_to_png(equation, "diff"+str(i)+".png")
        return [True]+[sympy.solveset(differences[i])==sympy.solveset(0) for i in range(1, len(differences))]
################
 

class Output(GridLayout):
    def __init__(self, latex_equations, **kwargs):
        super(Output, self).__init__(**kwargs)
        is_multiple = len(latex_equations[0].split("="))>1
        if(is_multiple):
            self.cols = 3
        else:
            self.cols = 4
        # TODO: ENABLE
        try:
            checked_equations = check_equations_and_generate_pngs(latex_equations)
        except:
            self.add_widget(Label(text="Ooops! I didn't understand that input.", color=[1,0,0, 1], font_size='60dp'))
            return
        print checked_equations
        for i, (latex_equation, checked_equation) in enumerate(zip(latex_equations, checked_equations)):
            if i == 0:
                self.add_widget(Label(text="Original equation:", color=[0,0,0, 1], font_size='30dp'))
            else:
                # self.add_widget(Label(text="Step "+str(i)+":",  color=[0,0,0, 1], font_size='30dp'))
                if checked_equation == True:
                    self.add_widget(Image(source="arrow_green.jpg"))
                else: 
                    self.add_widget(Image(source="arrow_red.jpg"))

            self.add_widget(Image(source="output"+str(i)+".png", size_hint_x=0.8, size_hint_y=0.8, allow_stretch=True))

            if checked_equation == True:
                text = "[b]This step is correct![/b]"
                if i == 0:
                    text = ""                    
                self.add_widget(Label(text=text, color=[0,1,0, 1], font_size='30dp', markup=True))
            else:
                self.add_widget(Label(text="[b]This step went wrong![/b]", color=[1,0,0, 1], font_size='30dp', markup=True))
                
            self.add_widget(Image(source="diff"+str(i)+".png", size_hint_x=0.8, size_hint_y=0.8, allow_stretch=True))


class CameraExample(App):

    def build(self):
        self.clicked = False
        self.layout = FloatLayout(orientation='vertical')
        # Create a camera object
        self.cameraObject            = Camera(play=False, pos=(0,346))
        self.cameraObject.play       = True
        self.cameraObject.resolution = (1000, 600) # Specify the resolution
        # Create a button for taking photograph
        self.cameraClick = Button(text="Take Photo and Evaluate", pos=(0, 440), font_size='60dp')
        self.cameraClick.size_hint=(1, .2)
        # bind the button's on_press to onCameraClick
        self.cameraClick.bind(on_press=self.onCameraClick)
        # add camera and button to the layout
        self.layout.add_widget(self.cameraObject)
        self.layout.add_widget(self.cameraClick)
        return self.layout 

    def delete_output_pngs(self):
        import glob, os, multiprocessing
        p = multiprocessing.Pool(4)
        print os.listdir('.') 
        print "after"
        p.map(os.remove, glob.glob("output*.png"))
        print os.listdir('.') 

    # Take the current frame of the video as the photo graph       
    def onCameraClick(self, *args):
        Cache.remove('kv.image')
        Cache.remove('kv.texture')
        self.delete_output_pngs()
        if self.clicked == True:
            self.layout.remove_widget(self.output)
        self.clicked = True
        self.cameraObject.export_to_png('output.png')
        latex_string = image_to_latex('output.png')
        print latex_string.__repr__()
        # latex_string = "\left. \begin{array} { l } { x ^ { 2 } + 5 x + 6 = 0 } \\ { 3 x + 2 x + x ^ { 2 } + 3 x = 3 } \\ { x ^ { 2 } = -8 x + 3 } \end{array} \right."
        # latex_string = "\left. \begin{array} { l } { x ^ { 2 } + 5 x + 6 = 0 } \\ { 3 x + 2 x + x ^ { 2 } + 3 x = 3 } \\ { x ^ { 2 } = 3 x + 2 x + 3 } \\ { 6 = x ^ { 2 } + 4 + 5 } \end{array} \right."
        latex_equations = split_into_equations(latex_string)
        print latex_equations
        self.output = Output(latex_equations, size_hint=(1, .35))
        self.layout.add_widget(self.output)

# Start the Camera App
if __name__ == '__main__': 
     CameraExample().run()
