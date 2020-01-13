# author: Andre Hoffmann

import random
import copy as cpy


# return the negated literal
def negate(literal):
    if 'n' in literal:
        return ''.join(list(literal)[1:])  # cut off the negation marker
    else:
        return 'n' + str(literal)


# evaluate the boolean value of a literal
def eval_lit(literal, table):
    if 'n' in literal:
        if table[negate(literal)] is None:
            return None
        else:
            return not table[negate(literal)]
    else:
        if table[literal] is None:
            return None
        else:
            return table[literal]


# evaluate the boolean value of a clause
def eval_clause(clause, table):
    if len(clause) == 0:
        return False
    elif any([eval_lit(l, table) for l in clause]):
        return True
    elif not any(map(lambda i: i is None, table.items())):
        return False
    else:
        return None


# evaluate the boolean value of a formula in CNF
def eval_formula(formula):
    # return all(map(eval_clause, formula[0], formula[1]))
    return all(map(lambda c, d=formula[1]: eval_clause(c, d), formula[0]))


# return True if bottom is derived under current assignment,
# i.e. if there exists an empty clause or if there are no blank symbols left while the formula is not empty yet
def bottom(formula):
    return any(map(lambda c: len(c) == 0, formula[0]))


# delete any literal in a clause that evaluates to False
def reduce_clause(clause, table):
    marked = []
    for literal in clause:
        if eval_lit(literal, table) == False:
            marked.append(clause.index(literal))
    clause[:] = [literal for literal in clause if clause.index(literal) not in marked]


# delete clauses evaluating to True and literals evaluating to False
def reduce_formula(formula):
    marked = []
    for clause in formula[0]:
        if eval_clause(clause, formula[1]):  # check if clause equals to true, i.e. there exists a literal equaling True
            marked.append(formula[0].index(clause))
        else:
            reduce_clause(clause, formula[1])
    formula[0][:] = [clause for clause in formula[0] if formula[0].index(clause) not in marked]


# return list of all unassigned-to variables
def get_blank_symbols(formula):  # find symbols that haven't been assigned to yet
    blanks = []
    for symbol in formula[1].keys():
        if formula[1][symbol] is None:
            blanks.append(symbol)
    return blanks


# return list of literals that strictly appear in either negated or non-negated form
def monochromes(formula):
    checked = []
    monos = []
    for blank in get_blank_symbols(formula):
        if blank in checked:
            continue
        elif all(map(lambda c, l=blank: negate(l) not in c, formula[0])):  # check if symbol is a mono
            monos.append(blank)
            checked.append(blank)
        elif all(map(lambda c, l=negate(blank): negate(l) not in c, formula[0])):
            monos.append(negate(blank))
            checked.append(negate(blank))
        else:
            checked.extend([blank, negate(blank)])
    # print("monochrome literals: ", list(map(parse_literal, monos)))
    return monos


# return a list of all literals appearing in unit clauses
def unit_literals(formula):
    units = []
    for clause in formula[0]:
        if len(clause) == 1:
            units.append(clause[0])
    return units


# for a given literal assign value to the corresponding variable
def assign(formula, literal, value):
    if 'n' in literal:  # update dictionary
        formula[1][negate(literal)] = value
    else:
        formula[1][literal] = value


# perform trivial assignments and reduce the given formula
def simplify(formula, verbose=False):
    i = 0
    while True:
        i += 1
        if verbose:
            print('-----starting round %d------------------------' %i)
        token = cpy.deepcopy(formula)  # keep track of changes
        for literal in monochromes(formula):  # assign monochromatic literals such that they turn to True
            if 'n' in literal:
                assign(formula, literal, False)
            else:
                assign(formula, literal, True)
        # assign the literal in unit clauses such that the clause is satisfied
        for unit in unit_literals(formula):
            if 'n' in unit:
                assign(formula, unit, False)
            else:
                assign(formula, unit, True)
        # delete redundant clauses and literals
        reduce_formula(formula)
        if verbose:
            print("after reduction: ")
            display_SAT(formula)
            print('current assignment: ', formula[1])
        if token == formula or len(formula[0]) == 0:  # break when no change is achieved
            break


# search the whole domain of possible assignments by performing recursive tree-search
def solve_complete(formula, verbose=False):
    copy = cpy.deepcopy(formula)
    if verbose:
        print("-----SIMPLIFY--------------------------------")
    simplify(copy, verbose)
    if verbose:
        print("-----END-------------------------------------")
    # check if we can cut the current branch
    if len(copy[0]) == 0:
        if verbose:
            print("found satisfying assignment!")
        return copy[1]
    if bottom(copy):
        if verbose:
            print("derived bottom!")
        return None
    # assign randomly to an arbitrary symbol
    # each branch has two chances, if both derive bottom cut off that branch
    symbol = get_blank_symbols(copy)[0]
    if verbose:
        print("I will assign ", symbol, "with ", True)
    assign(copy, symbol, True)
    result = solve_complete(copy)
    # print("my first try resulted in ", first_try)
    if result is None:
        if verbose:
            print("Backtrack: I will assign ", symbol, "with ", False)
        assign(copy, symbol, False)
        result = solve_complete(copy)
        # print("my last try resulted in ", last_try)
    return result


# for a given literal negate the boolean value of the corresponding variable
def flip_literal(table, literal):
    if 'n' in literal:
        table[negate(literal)] = not table[negate(literal)]
    else:
        table[literal] = not table[literal]


# return the index of an arbitrary unsatisfied clause in formula
def get_unsat_clause_index(formula):
    for clause in formula[0]:
        if eval_clause(clause, formula[1]):
            continue
        else:
            return formula[0].index(clause)


# search for a literal that can be flipped without unsatisfying another clause
# if none was found return None
def get_best_lit(formula, clause_index):
    # print("clause index:", clause_index)
    # generate lookup-table for boolean values of each clause
    clause_vals = dict.fromkeys(range(len(formula[0])))
    for clause in clause_vals:
        clause_vals[clause] = eval_clause(formula[0][clause], formula[1])
    # print("satisfied clauses: ", clause_vals)
    # check each literal in given clause for it being flippable without unsatisfying other clauses
    for literal in formula[0][clause_index]:
        clause_vals_copy = cpy.deepcopy(clause_vals)  # copy of clause values
        assignments_copy = cpy.deepcopy(formula[1])  # copy of variable assignments
        flip_literal(assignments_copy, literal)  # flip the literal
        for clause in clause_vals_copy:  # evaluate all clauses after flipping the literal
            clause_vals_copy[clause] = eval_clause(formula[0][clause], assignments_copy)
        # check if literal has the desired property:
        if not any(map(lambda c: clause_vals[c] and not clause_vals_copy[c], clause_vals.keys())):
            # print("best-lit: ", literal)
            return literal
    return None


# count the number of clauses that get unsatisfied as a result of flipping the literal
def count_unsat_clauses(formula, literal):
    counter = 0
    # generate lookup-table for boolean values of each clause
    clause_vals = dict.fromkeys(range(len(formula[0])))
    for clause in clause_vals:
        clause_vals[clause] = eval_clause(formula[0][clause], formula[1])
    clause_vals_copy = cpy.deepcopy(clause_vals)  # copy of clause values
    assignments_copy = cpy.deepcopy(formula[1])  # copy of variable values
    flip_literal(assignments_copy, literal)  # flip the literal
    for clause in clause_vals_copy:  # evaluate all clauses after flipping the literal
        clause_vals_copy[clause] = eval_clause(formula[0][clause], assignments_copy)
    # count the number of dissatisfied clauses as a result of flipping literal
    for clause in clause_vals_copy:
        if not clause_vals_copy[clause] and clause_vals[clause]:  # check whether clause was True before and now False
            counter += 1
    return counter


# attempt to solve formula using a random walk
# number of coin tosses limited to tc, then restart on a random assignment
# algorithm starts at most tr times, then outputs None
def walk_sat(formula, tc=4, tr=4, bias=0.6, verbose=False):
    restarts = 0
    while not eval_formula(formula) and restarts < tr:
        restarts += 1
        if verbose:
            print("restarting counter: ", restarts)
        tosses = 0
        # generate random assignment:
        for key in formula[1]:
            formula[1][key] = bool(random.randint(0, 1))
        if verbose:
            print("randomly generated assignment: ", formula[1])
        while not eval_formula(formula) and tosses < tc:
            # pick arbitrary unsatisfied clause:
            clause = get_unsat_clause_index(formula)
            if verbose:
                print("clause ", formula[0][clause], "is not satisfied.")
            # if there exists a literal in clause that can be flipped without dissatisfying any other clause then flip
            best_lit = get_best_lit(formula, clause)
            if best_lit is not None:
                flip_literal(formula[1], best_lit)
                if verbose:
                    print("flipped literal ", best_lit)
                    print("new assignment: ", formula[1])
            else:
                # else toss a coin and perform action according to outcome
                coin = random.random() < bias
                tosses += 1
                if verbose:
                    print("tossed a coin with result ", coin, ", counter ", tosses)
                if coin:
                    # flip literal such that the least number of other clauses gets unsatisfied
                    if verbose:
                        print("flipped literal such that the least number of clauses get unsatisfied.")
                    counts = dict.fromkeys([l for l in formula[0][clause]])
                    for literal in counts.keys():
                        counts[literal] = count_unsat_clauses(formula, literal)
                    flip_literal(formula[1], min(counts, key=counts.get))
                else:
                    # flip random literal
                    if verbose:
                        print("flipped a random literal.")
                    flip_literal(formula[1], random.choice(formula[0][clause]))
    if verbose:
        if eval_formula(formula):
            print("assignment ", formula[1], "is satisfying.")
        else:
            print("no satisfying assignment found.")
    return formula[1] if eval_formula(formula) else None


def solve_SAT(formula, method='complete', tosses=4, restarts=4, coin_bias=0.6, verbose=False):
    if verbose:
        print("input formula: ")
        display_SAT(formula)
    if method == 'complete':
        return solve_complete(formula, verbose=verbose)
    if method == 'incomplete':
        return walk_sat(formula, tr=restarts, tc=tosses, bias=coin_bias, verbose=verbose)
    else:
        print("specify a valid method name!")
        return None


# randomly generate a SAT-formula in CNF
# 'k' literals per clause, 'num_vars' variables in total, and 'clauses' number of clauses
def craft_SAT(k, num_vars=4, clauses=12):
    formula = []
    variables = []
    for i in range(num_vars):  # generate symbols
        variables.append('x%d' %i)
    assignment = dict.fromkeys(variables)
    for i in range(clauses):
        clause = []
        indices = random.sample(range(0, len(variables)), k)  # pick k symbols from vars to inject in next clause
        for j in range(k):  # fill current clause
            neg = random.randint(0, 1)  # determine truth value of next symbol
            if neg:
                clause.append('n' + variables[indices[0]])
            else:
                clause.append(variables[indices[0]])
            indices = indices[1:]
        formula.append(clause)
    return [formula, assignment]


# rewrite the given literal using lowercase numbers and symbols of propositional logic
def parse_literal(literal):
    SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    if 'n' in literal:
        parsed = u'\u00AC' + literal[1] + literal[2].translate(SUB)
    else:
        parsed = literal[0] + literal[1].translate(SUB)
    return parsed


# rewrite the given clause using symbols of propositional logic and round parentheses
def parse_clause(clause):
    nice_strings = []
    for piece in map(lambda l: parse_literal(l), clause):
        nice_strings.append(piece)
    return '( ' + u' \u2228 '.join(nice_strings) + ' )'


# display the given formula using symbols of propositional logic and round parentheses
def display_SAT(formula):
    nice_strings = []
    for nice_clause in map(parse_clause, formula[0]):
        nice_strings.append(nice_clause)
    if len(nice_strings) == 0:
        print([])
    else:
        print(u' \u2227 '.join(nice_strings))

##################################

# my_sat = craft_SAT(k=3, num_vars=4, clauses=5)
# solve_SAT(my_sat, method='incomplete', verbose=True)

