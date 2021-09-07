
import tarski
from tarski.io import PDDLReader
from tarski.io import fstrips as iofs
from tarski.syntax import land, Atom

from tarski.search import GroundForwardSearchModel
from tarski.grounding.lp_grounding import (
    ground_problem_schemas_into_plain_operators,
    LPGroundingStrategy,
)

from tarski.grounding.naive_grounding import ground_symbols_exhaustively
from tarski.syntax.util import get_symbols

from tarski.grounding import NaiveGroundingStrategy
from tarski.syntax.transform.action_grounding import ground_schema_into_plain_operator_from_grounding

def cost1(domain):
    return iofs.AdditiveActionCost(domain.language.constant(1, domain.language.get_sort('Integer')))

def normalize_fluent(fluent):
    return str(fluent).lower().replace('()', '').replace(')', '').replace('  ',' ').strip().replace(' ', '_').replace('(', '_').replace(',', '_')

def normalize_action(act):
    return str(act).lower().replace(' ', '').replace('(', '__').replace(')', '').replace(',', '_')

def str_to_atom(fluent, domain):
    return domain.language.get(fluent)()

def str_to_action(act, domain):
    return domain.get_action(act)

def regress(state, act):

    debug = False
        
    adds = {f.atom for f in act.effects if isinstance(f, iofs.AddEffect)}
    dels = {f.atom for f in act.effects if isinstance(f, iofs.DelEffect)}
    pre = {f for f in act.precondition.subformulas}

    if debug:
        print("\nRegression State:")
        print(state)
        print("...through action %s" % act.name)
        print("PRE:" + str(pre))
        print("ADD:" + str(adds))
        print("DEL:" + str(dels))
        print("Resulting state:")
        print((state - adds) | pre)

    assert adds & dels == set() and state & dels == set(), f"Cannot regress with conflicting goal / action effects: {state} {act}"

    return ((state - adds) | pre)



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
    grounder = NaiveGroundingStrategy(problem)

    grounded_fluents = set(ground_symbols_exhaustively(get_symbols(problem.language, include_builtin=False)))

    init = [f for f in problem.init.as_atoms()]# if f in grounded_fluents]

    if isinstance(problem.goal, Atom):
        goal = [problem.goal]
    else:
        goal = [f for f in problem.goal.subformulas]# if f in grounded_fluents]

    operators = []
    actions = grounder.ground_actions()
    for name, bindings in actions.items():
        for binding in bindings:
            action = problem.get_action(name)
            operators.append(ground_schema_into_plain_operator_from_grounding(action, binding))

    return (grounded_fluents, init, goal, operators)

def smart_ground_problem(problem):
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
    fluent_strings = set(map(str, fluents))

    for f in fluent_strings:
        fmap[f] = lang.predicate(normalize_fluent(f))

    problem = iofs.create_fstrips_problem(domain_name=dname, problem_name=pname, language=lang)

    # Initial state
    new_init = tarski.model.create(lang)
    for atom in init:
        new_init.add(fmap[str(atom)])
    problem.init = new_init

    # Goal
    problem.goal = land(*[fmap[str(f)]() for f in goal], flat=True)

    # Operators
    for op in operators:
        pre = [fmap[str(f)]() for f in op.precondition.subformulas if str(f) in fluent_strings]
        effs = []
        for eff in op.effects:
            if isinstance(eff, iofs.AddEffect):
                effs.append(iofs.AddEffect(fmap[str(eff.atom)]()))
            elif isinstance(eff, iofs.DelEffect):
                effs.append(iofs.DelEffect(fmap[str(eff.atom)]()))
            else:
                raise ValueError("Unknown effect type: {}".format(eff))

        problem.action(normalize_action(op.name), [], precondition=land(*pre, flat=True), effects=effs)

    return problem

def force_plan(domain, plan, avoid = []):
    
    enabled = domain.language.predicate('enabled')

    
    for action in domain.actions.values():
        # Disable all the regular actions
        if all([nm not in action.name for nm in avoid]):
            if isinstance(action.precondition, Atom):
                action.precondition = land(action.precondition, enabled(), flat=True)
            else:
                action.precondition = land(*(action.precondition.subformulas), enabled(), flat=True)

        # If there is a clone action (only in the goal-preserving compilation), have it re-enable all actions
        if action.name == 'clone':
            action.effects += [iofs.AddEffect(enabled())]

    # Create a new fluent for every action in the plan
    step_fluents = [domain.language.predicate(f'forced-step-{i}') for i in range(len(plan))]

    # Create a new action for every step in the plan
    for i, act in enumerate(plan):
        act_name = act[1:-1].split(' ')[0]
        act_params = act[1:-1].split(' ')[1:]
        new_name = act_name + '__' + '_'.join(act_params)
        orig = str_to_action(new_name, domain)
        pres = [f for f in orig.precondition.subformulas if 'enabled' not in str(f)] + [~step_fluents[i]()]
        if i > 0:
            pres.append(step_fluents[i-1]())
        
        domain.action(f'assess-step-{i}', [],
                        precondition = land(*pres, flat=True),
                        effects = orig.effects + [iofs.AddEffect(step_fluents[i]())])
