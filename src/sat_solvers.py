# author: Andre Hoffmann

import random
import copy as cpy


def negate(literal):
    if 'n' in literal:
        return ''.join(list(literal)[1:])  # cut off the negation marker
    else:
        return 'n' + str(literal)


def test_negate():
    lit1 = ['nx1', None]
    lit2 = ['x2', None]
    print(lit1, lit2)
    print(negate(lit1), negate(lit2))


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


def test_eval_lit():
    lit = ['nx1', False]
    lit2 = ['nx1', None]
    print('test_eval_lit: ', eval_lit(lit) == True)


def eval_clause(clause, table):  # clause is a list of tuples:(var, assignment)
    if len(clause) == 0:
        return False
    elif any([eval_lit(l, table) for l in clause]):
        return True
    else:
        return None


def test_eval_clause():
    c = [['nx0', True], ['x1', None], ['x3', True]]
    d = [['nx0', None], ['x1', None], ['x3', None]]
    print('test_eval_clause: ', eval_clause(c) == True and eval_clause(d) == False)


def eval_formula(formula):
    return all(map(eval_clause, formula[0], formula[1]))


def test_eval_formula():
    f = [[['nx0', None], ['x1', False], ['x3', True]]]
    print('test_eval_formula: ', eval_formula(f) == True)


# return True if bottom is derived under current assignment,
# i.e. if there exists an empty clause or if there are no blank symbols left while the formula is not empty yet
def bottom(formula):
    return any(map(lambda c: len(c) == 0, formula[0]))


def reduce_clause(clause, table):  # delete any literal in a clause that evaluates to False
    marked = []
    for literal in clause:
        if eval_lit(literal, table) == False:
            marked.append(clause.index(literal))
    clause[:] = [literal for literal in clause if clause.index(literal) not in marked]


def reduce_formula(formula):
    marked = []
    for clause in formula[0]:
        if eval_clause(clause, formula[1]):  # check if clause equals to true, i.e. there exists a literal equaling True
            marked.append(formula[0].index(clause))
        else:
            reduce_clause(clause, formula[1])
    formula[0][:] = [clause for clause in formula[0] if formula[0].index(clause) not in marked]


def get_blank_symbols(formula):  # find symbols that haven't been assigned to yet
    blanks = []
    for symbol in formula[1].keys():
        if formula[1][symbol] is None:
            blanks.append(symbol)
    return blanks


def monochromes(formula):  # find literals that strictly appear in either negated or non-negated form
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


def test_monos(iterations=1000):
    results = []
    for i in range(iterations):
        sat = craft_SAT(3)
        monos = monochromes(sat)
        if len(monos) != 0:
            literal = random.choice(monos)
            results.append(all(map(lambda c, l=literal: negate(l) not in c, sat)))
        else:
            continue
    return all(results)


def unit_literals(formula):  # return a list of all literals appearing in unit clauses
    units = []
    for clause in formula[0]:
        if len(clause) == 1:
            units.append(clause[0])
    return units


def assign(formula, literal, value):
    if 'n' in literal:  # update dictionary
        formula[1][negate(literal)] = value
    else:
        formula[1][literal] = value


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


def brute_force(formula, verbose=False):
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
    result = brute_force(copy)
    # print("my first try resulted in ", first_try)
    if result is None:
        if verbose:
            print("Backtrack: I will assign ", symbol, "with ", False)
        assign(copy, symbol, False)
        result = brute_force(copy)
        # print("my last try resulted in ", last_try)
    return result


def solve_SAT(formula, method='complete', verbose=False):
    if verbose:
        print("input formula: ")
        display_SAT(formula)
    if method == 'complete':
        return brute_force(formula, verbose)
    if method == 'incomplete':
        print("walk_sat not implemented yet!")
        return None
    else:
        print("specify a valid method name!")
        return None


def craft_SAT(k, num_vars=4, clauses=12):  # randomly generate a SAT-formula
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


def parse_literal(literal):
    SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    if 'n' in literal:
        parsed = u'\u00AC' + literal[1] + literal[2].translate(SUB)
    else:
        parsed = literal[0] + literal[1].translate(SUB)
    return parsed


def parse_clause(clause):
    nice_strings = []
    for piece in map(lambda l: parse_literal(l), clause):
        nice_strings.append(piece)
    return '( ' + u' \u2228 '.join(nice_strings) + ' )'


def display_SAT(formula):
    nice_strings = []
    for nice_clause in map(parse_clause, formula[0]):
        nice_strings.append(nice_clause)
    if len(nice_strings) == 0:
        print([])
    else:
        print(u' \u2227 '.join(nice_strings))

##################################

my_sat = craft_SAT(k=3, num_vars=4, clauses=5)
print(solve_SAT(my_sat, verbose=True))

