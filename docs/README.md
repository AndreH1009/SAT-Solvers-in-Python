# SAT-Solvers-in-Python
The purpose of this project is to provide implementations for a selection of SAT-Solvers in Python. It contains a complete solver 'solve_complete' and an incomplete solver 'walk_sat'. All solvers and functions operate on SAT-formulas in conjunctive normalform.

## Representation
A SAT-formula is a list [f,a], where f is a list of clauses and a is a dictionary containing the current assignment. A clause is a list of literals, where a literal is a string "x1" or "nx1", referring to the variable x1 or it's negation. 

## Features
- The function solve_complete implements a SAT-Solver after the DPLL scheme and as such it is a complete solver, guaranteed to find a satisfying assignment to a given SAT-formula if one exists, using recursive tree-search to search the domain of all possible assignments.

- The function walk_sat implements a probabilistic SAT-solver by performing a random walk on the domain of possible assignments. It delivers a 'best-guess', and as such is not guaranteed to find a satisfying assignment even if it exists. Being incomplete, it is much faster than the solve_complete algorithm. 

- The function craft_SAT is a randomised generator for SAT-formulas in conjunctive normalform. The parameter k denotes the number of literals in each clause, num_vars denotes the number of variables and the parameter clauses denotes the number of clauses in the to be returned formula.

- The function display_SAT takes a SAT-formula and displays it nicely by replacing list brackets by round parentheses and by adding the correct symbols for the operators of propositional logic.\
Example: ( ¬x₃ ∨ x₄ ∨ x₂ ) ∧ ( x₂ ∨ x₀ ∨ x₃ ) ∧ ( ¬x₂ ∨ ¬x₄ ∨ ¬x₃ ) ∧ ( ¬x₂ ∨ ¬x₃ ∨ ¬x₄ )

## How To
- access the project:\
clone the project and find file "sat_solvers.py" in src.
- generate a SAT-formula with 3-clauses, 4 variables and 5 clauses:\
```my_sat = craft_SAT(k=3, num_vars=4, clauses=5)```
- display a given formula "my_sat":\
```display_SAT(my_sat)```
- solve formula my_sat using complete solver solve_complete:\
```print(solve_SAT(my_sat, method='complete))```
- solve formula my_sat using incomplete solver walk_sat:\
```print(solve_SAT(my_sat, method='complete))```
- print the solving process:\
```solve_SAT(my_sat, verbose=True)```

## Example: solve_complete
```
input formula: 
( x₂ ∨ x₁ ∨ x₀ ) ∧ ( x₂ ∨ ¬x₁ ∨ x₀ ) ∧ ( ¬x₂ ∨ ¬x₁ ∨ ¬x₃ ) ∧ ( ¬x₀ ∨ x₂ ∨ x₃ )
-----SIMPLIFY--------------------------------
-----starting round 1------------------------
after reduction: 
( x₂ ∨ x₁ ∨ x₀ ) ∧ ( x₂ ∨ ¬x₁ ∨ x₀ ) ∧ ( ¬x₂ ∨ ¬x₁ ∨ ¬x₃ ) ∧ ( ¬x₀ ∨ x₂ ∨ x₃ )
current assignment:  {'x0': None, 'x1': None, 'x2': None, 'x3': None}
-----END-------------------------------------
I will assign  x0 with  True
-----SIMPLIFY--------------------------------
-----starting round 1------------------------
after reduction: 
( ¬x₂ ∨ ¬x₁ ∨ ¬x₃ ) ∧ ( x₂ ∨ x₃ )
current assignment:  {'x0': True, 'x1': None, 'x2': None, 'x3': None}
-----starting round 2------------------------
after reduction: 
( x₂ ∨ x₃ )
current assignment:  {'x0': True, 'x1': False, 'x2': None, 'x3': None}
-----starting round 3------------------------
after reduction: 
[]
current assignment:  {'x0': True, 'x1': False, 'x2': True, 'x3': True}
-----END-------------------------------------
found satisfying assignment!
{'x0': True, 'x1': False, 'x2': True, 'x3': True}
```

## Example: walk_sat
```
input formula: 
( ¬x₃ ∨ ¬x₀ ∨ ¬x₁ ) ∧ ( ¬x₁ ∨ ¬x₂ ∨ ¬x₀ ) ∧ ( x₂ ∨ ¬x₃ ∨ ¬x₁ ) ∧ ( ¬x₂ ∨ x₃ ∨ x₁ ) ∧ ( ¬x₀ ∨ ¬x₁ ∨ ¬x₃ )
restarting counter:  1
randomly generated assignment:  {'x0': True, 'x1': True, 'x2': True, 'x3': True}
clause  ['nx3', 'nx0', 'nx1'] is not satisfied.
flipped literal  nx3
new assignment:  {'x0': True, 'x1': True, 'x2': True, 'x3': False}
clause  ['nx1', 'nx2', 'nx0'] is not satisfied.
flipped literal  nx2
new assignment:  {'x0': True, 'x1': True, 'x2': False, 'x3': False}
assignment  {'x0': True, 'x1': True, 'x2': False, 'x3': False} is satisfying.

```