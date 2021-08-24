
import tarski
from tarski.io import PDDLReader
from tarski.io import fstrips as iofs
from tarski.syntax import land

from tarski.search import GroundForwardSearchModel
from tarski.grounding.lp_grounding import (
    ground_problem_schemas_into_plain_operators,
    LPGroundingStrategy,
)

def cost1(domain):
    return iofs.AdditiveActionCost(domain.language.constant(1, domain.language.get_sort('Integer')))

def normalize_fluent(fluent):
    return str(fluent).replace('()', '').replace(')', '').replace('  ',' ').strip().replace(' ', '_').replace('(', '_').replace(',', '_')

def normalize_action(act):
    return str(act).replace(' ', '').replace('(', '__').replace(')', '').replace(',', '_')

def str_to_atom(fluent, domain):
    return domain.language.get(fluent)()

def str_to_action(act, domain):
    return domain.get_action(act)

def regress(state, act):
    adds = {f for f in act.effects if isinstance(f, iofs.AddEffect)}
    dels = {f for f in act.effects if isinstance(f, iofs.DelEffect)}



    # TODO: figure out how to get at the negative preconditions
    pospres = {f for f in act.precondition.subformulas}
    negpres = {f for f in act.precondition.subformulas}


    
    pos = state[0]
    neg = state[1]

    assert adds & dels == set() and pos & dels == set(), f"Cannot regress with conflicting goal / action effects: {state} {act}"
    
    return ((pos - adds) | pospres), ((neg - dels) | negpres)



def write_pddl(problem, dname, pname):
    writer = iofs.FstripsWriter(problem)
    writer.write(dname, pname)

    # Fix the function name
    with open(dname, 'r') as f:
        domtext = f.read()
    domtext = domtext.replace('- int', '- number')
    with open(dname, 'w') as f:
        f.write(domtext)

    # Add the metric to minimize cost
    with open(pname, 'r') as f:
        probtext = f.read()
    assert probtext[-3:] == ')\n\n', probtext[-3:]
    probtext = probtext[:-3] + '\n(:metric minimize (total-cost))\n\n)\n'
    with open(pname, 'w') as f:
        f.write(probtext)


def parse_pddl(dname, pname):
    reader = PDDLReader(raise_on_error=True)
    reader.parse_domain(dname)
    problem = reader.parse_instance(pname)
    return problem

def ground_problem(problem):
    operators = ground_problem_schemas_into_plain_operators(problem)
    instance = GroundForwardSearchModel(problem, operators)
    grounder = LPGroundingStrategy(problem, include_variable_inequalities=True)
    grounded_fluents = set([grounded_fluent.to_atom() for grounded_fluent in grounder.ground_state_variables().objects])
    init = [f for f in problem.init.as_atoms() if f in grounded_fluents]
    if isinstance(problem.goal, tarski.syntax.Atom):
        goal = [problem.goal]
    else:
        goal = [f for f in problem.goal.subformulas if f in grounded_fluents]

    return (grounded_fluents, init, goal, operators)

def atomicize(fluents, init, goal, operators, dname = "atomic", pname = "atomicP"):

    lang = iofs.language(dname, theories=['arithmetic'])
    cost = lang.function('total-cost', lang.Integer)

    # Fluents
    fmap = {}

    for f in fluents:
        fmap[f] = lang.predicate(normalize_fluent(f))

    problem = iofs.create_fstrips_problem(domain_name=dname, problem_name=pname, language=lang)

    # Initial state
    new_init = tarski.model.create(lang)
    for atom in init:
        new_init.add(fmap[atom])
    problem.init = new_init

    # Goal
    problem.goal = land(*[fmap[f]() for f in goal], flat=True)

    # Operators
    for op in operators:
        pre = [fmap[f]() for f in op.precondition.subformulas if f in fluents]
        effs = []
        for eff in op.effects:
            if isinstance(eff, iofs.AddEffect):
                effs.append(iofs.AddEffect(fmap[eff.atom]()))
            elif isinstance(eff, iofs.DelEffect):
                effs.append(iofs.DelEffect(fmap[eff.atom]()))
            else:
                raise ValueError("Unknown effect type: {}".format(eff))

        problem.action(normalize_action(op.name), [], precondition=land(*pre, flat=True), effects=effs)

    return problem
