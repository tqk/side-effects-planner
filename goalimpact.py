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




# add done predicate
# donePre = lang.predicate('done')
# achieved = lang.predicate('achieved')
# # add done action
# doneAct = problem.action('done', [], precondition = problem.goal,
# effects = [
#     iofs.AddEffect(donePre)
# ])


def normalize_fluent(fluent):
    return str(fluent).replace('  ',' ').replace(' ', '_').replace('(', '_').replace(')', '').replace(',', '_')

def write_pddl(problem, dname, pname):
    writer = iofs.FstripsWriter(problem)
    writer.write(dname, pname)

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
    return (grounded_fluents, init, goal, instance.operators)

def atomicize(fluents, init, goal, operators, dname = "atomic", pname = "atomicP"):
    lang = iofs.language(dname)

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
    problem.goal = land(*[fmap[f]() for f in goal])

    # TODO: Operators

    return problem

"""
for x in grounded_fluents:
    if x not in problem.goal.subformulas:
        #   ; If (holding A) is not in the goal, but in the initial state
        #   (:action achieve_holding_A
        #       :precondition (and (done) (holding A))
        #       :effect (and (achieved_holding_A))
        #   )
        if x in init:
            print(normalize_fluent(x))
            achievedAct = problem.action('achieved_'+str(x),
                            [],




                            precondition = donePre & x,

                            # TODO: Predicate and atom can't be combined. Need to do everything on the lifted level.
                            #        This means that the cost of ignoring a goal atom should be 0 and not 1.
                            #        This also means that all objects should move to constants, so that we can have
                            #          the "done" action actually work.




                            effects = [iofs.AddEffect((achieved))])
        #   (:action ignore_holding_A
        #       :precondition (and (done))
        #       :effect (and (achieved_holding_A) (increase total-cost 1))
        #   )
        #   ; Must add (achieved_holding_A) to the goal
        # ignore_A = problem.action('ignore_A',[],precondition = donePre,
        #     effects = [
        #         iofs.AddEffect(achieved)
        #     ])
        #   ; If (holding A) is not in the goal, and not in the initial state
        #   (:action achieve_holding_A
        #       :precondition (and (done) (not (holding A)))
        #       :effect (and (achieved_holding_A))
        #   )
        # achieved_B = problem.action('achieved_B',[],precondition = donePre &~x,
        #     effects = [
        #         iofs.AddEffect(achieved)
        #     ])
#export
#writer = iofs.FstripsWriter(problem)
#writer.write("domain.pddl", "problem.pddl")
# print(list(problem.actions))
"""

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

    write_pddl(atomic_domain, out_domain_file, out_problem_file)
