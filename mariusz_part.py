
from latex2sympy.process_latex import process_sympy
import sympy

eq = process_sympy("\cos s + 1 = 0")
print(eq)
res = sympy.solveset(eq)
print(res)
