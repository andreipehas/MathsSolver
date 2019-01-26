
from kivy.app import App
from kivy.uix.camera import Camera
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

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

################ split latex into latex equations
def split_into_equations(s):
	return s[25:-18].split("\\")

from process_latex import process_sympy
import sympy

def check_equations(latex_equations):
	#for i in latex_equations:
	#	print i
	equations = [process_sympy(i[2:-2]) for i in latex_equations]
	#for i in equations:
	#	print i
	solution_sets = [sympy.solveset(i, domain=sympy.S.Complexes) for i in equations]
	return [ i==solution_sets[0] for i in solution_sets]
################
 

class Output(GridLayout):
    def __init__(self, latex_equations):
        super(Output, self).__init__()
        self.cols = 2
        checked_equations = check_equations(latex_equations)
        print checked_equations
        for latex_equation, checked_equation in zip(latex_equations, checked_equations):
            self.add_widget(Label(text=latex_equation))
            if checked_equation == True:
                self.add_widget(Label(text="True"))
            else:
                self.add_widget(Label(text="False"))


class CameraExample(App):

    def build(self):
        self.layout = BoxLayout(orientation='vertical')
        # Create a camera object
        self.cameraObject            = Camera(play=False)
        self.cameraObject.play       = True
        self.cameraObject.resolution = (600, 600) # Specify the resolution
        # Create a button for taking photograph
        self.cameraClick = Button(text="Take Photo and Evaluate")
        self.cameraClick.size_hint=(.5, .2)
        self.cameraClick.pos_hint={'x': .25, 'y':.75}
        # bind the button's on_press to onCameraClick
        self.cameraClick.bind(on_press=self.onCameraClick)
        # add camera and button to the layout
        self.layout.add_widget(self.cameraObject)
        self.layout.add_widget(self.cameraClick)

        # MY CODE
        
        # return the root widget
        return self.layout

    # Take the current frame of the video as the photo graph       
    def onCameraClick(self, *args):
        # self.cameraObject.export_to_png('output.png')
        # latex_string = image_to_latex('output.png')
        latex_string = "\left. \begin{array} { l } { x ^ { 2 } + 5 x + 6 = 0 } \\ { 3 x + 2 x + x ^ { 2 } + 3 x = 3 } \\ { x ^ { 2 } = 3 x + 2 x + 3 } \end{array} \right."
        latex_equations = split_into_equations(latex_string)
        print latex_equations
        self.output = Output(latex_equations)
        self.layout.add_widget(self.output)

# Start the Camera App
if __name__ == '__main__':
     CameraExample().run()
