# SAT-Solvers-in-Python
The purpose of this project is to provide implementations for different kinds of SAT-Solvers in Python. The function brute_force implements a SAT-Solver after the DPLL scheme and as such it is a complete solver guaranteed to find a satisfying assignment to a given SAT-formula if one exists. 

## Representation
A SAT-formula is a list [f,a], where f is a list of clauses and a is a dictionary containing the current assignment. A clause is a list of literals, where a literal is a string "x1" or "nx1", referring to the variable x1 or it's negation. 

## Features
- The function brute_force implements a SAT-Solver after the DPLL scheme and as such it is a complete solver, guaranteed to find a satisfying assignment to a given SAT-formula if one exists.

- The function craft_SAT is a randomised generator for SAT-formulas. The parameter k denotes the number of literals in each clause, num_vars denotes the number of variables and the parameter clauses denotes the number of clauses in the to be returned formula.

- The function display_SAT takes a SAT-formula and displays it nicely by replacing list brackets by round parentheses and by adding the correct symbols for the operators of propositional logic. Example: ( ¬x₃ ∨ x₄ ∨ x₂ ) ∧ ( x₂ ∨ x₀ ∨ x₃ ) ∧ ( ¬x₂ ∨ ¬x₄ ∨ ¬x₃ ) ∧ ( ¬x₂ ∨ ¬x₃ ∨ ¬x₄ )