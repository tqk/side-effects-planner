import sys
import tarski
from tarski.io import PDDLReader
from tarski.io import fstrips as iofs
from tarski.syntax import land

from tarski.search import GroundForwardSearchModel
from tarski.grounding.lp_grounding import (
    ground_problem_schemas_into_plain_operators,
    LPGroundingStrategy,
)

USAGE = "python3 goalimpact.py <in-domain.pddl> <in-problem.pddl> <out-domain.pddl> <out-problem.pddl>"




def normalize_fluent(fluent):
    return str(fluent).replace('()', '').replace(')', '').replace('  ',' ').strip().replace(' ', '_').replace('(', '_').replace(',', '_')

def normalize_action(act):
    return str(act).replace(' ', '').replace('(', '__').replace(')', '').replace(',', '_')

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


def modify_domain(atomic_domain, stratified=False):

    # Add done predicate
    donePre = atomic_domain.language.predicate('done')

    # # add done action
    atomic_domain.action('done', [],
                         precondition = atomic_domain.goal,
                         effects = [
                             iofs.AddEffect(donePre())
                         ])

    # Don't allow regular actions after done
    for action in atomic_domain.actions.values():
        if action.name != 'done':
            action.precondition = land(action.precondition, ~donePre())

    achieved_fluents = []

    for f in [f() for f in atomic_domain.language.predicates if f.arity == 0]:
        if f != donePre() and f not in atomic_domain.goal.subformulas:

            achieved = atomic_domain.language.predicate('achieved_'+normalize_fluent(f))
            achieved_fluents.append(achieved)

            # If stratified, then the achievements must happen in order.
            if stratified and len(achieved_fluents) > 1:
                pospre = land(f, donePre(), achieved_fluents[-2](), flat=True)
                negpre = land(~f, donePre(), achieved_fluents[-2](), flat=True)
            else:
                pospre = f & donePre()
                negpre = ~f & donePre()

            if f in atomic_domain.init.as_atoms():

                atomic_domain.action('ignore_'+normalize_fluent(f), [],
                                     precondition = negpre,
                                     effects = [
                                         iofs.AddEffect(achieved()),
                                     ],
                                     cost = iofs.AdditiveActionCost(atomic_domain.language.constant(1, atomic_domain.language.get_sort('Integer'))))

                atomic_domain.action('achieve_'+normalize_fluent(f), [],
                                     precondition = pospre,
                                     effects = [
                                         iofs.AddEffect(achieved()),
                                     ])
            else:
                atomic_domain.action('ignore_'+normalize_fluent(f), [],
                                     precondition = pospre,
                                     effects = [
                                         iofs.AddEffect(achieved()),
                                     ],
                                     cost = iofs.AdditiveActionCost(atomic_domain.language.constant(1, atomic_domain.language.get_sort('Integer'))))

                atomic_domain.action('achieve_'+normalize_fluent(f), [],
                                     precondition = negpre,
                                     effects = [
                                         iofs.AddEffect(achieved()),
                                     ])

    atomic_domain.goal = land(*[f() for f in achieved_fluents], flat=True)

    return atomic_domain



if __name__ == '__main__':
    if len(sys.argv) != 5:
        print(USAGE)
        exit(1)

    domain_file = sys.argv[1]
    problem_file = sys.argv[2]
    out_domain_file = sys.argv[3]
    out_problem_file = sys.argv[4]

    domain = parse_pddl(domain_file, problem_file)
    (grounded_fluents, init, goal, operators) = ground_problem(domain)

    atomic_domain = atomicize(grounded_fluents, init, goal, operators)

    modified_domain = modify_domain(atomic_domain, stratified=True)

    write_pddl(modified_domain, out_domain_file, out_problem_file)

    print('Huzzah!')
