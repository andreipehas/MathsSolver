
from latex2sympy.process_latex import process_sympy
import sympy

def check_equations(latex_equations):
	equations = [process_sympy(i) for i in latex_equations]
	solution_sets = [sympy.solveset(i, domain=sympy.S.Complexes) for i in equations]
	for i in range(len(solution_sets)):
		if(solution_sets[i]!=solution_sets[0]):
			print "You have a mistake in line ", i+1, "!"
			print "The line is "
			print latex_equations[i]
			return
	print "No mistakes!"




#testing
#check_equations(["x^2+5x+6=0", "x^2+5x=	-6", "(x+2)(x+3)=0"])
#check_equations(["x=\sqrt{2}", "x^2-\sqrt{8}x+2"])
