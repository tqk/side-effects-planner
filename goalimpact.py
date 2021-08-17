import sys
import tarski
from tarski.io import PDDLReader
from tarski.io import fstrips as iofs
from tarski.syntax import land

from tarski.search import GroundForwardSearchModel
from tarski.search.operations import progress
from tarski.grounding.lp_grounding import (
    ground_problem_schemas_into_plain_operators,
    LPGroundingStrategy,
)

# first argument: path to the domain file
# second argument: path to the problem file
a = str(sys.argv[1])
b = str(sys.argv[2])
#print(a)  #'./domainA.pddl'
#print(b)  #'./problemA.pddl'

# read the existing model and ground it
reader = PDDLReader(raise_on_error=True)
reader.parse_domain(format(a))
problem = reader.parse_instance(format(b))
lang = problem.language
operators = ground_problem_schemas_into_plain_operators(problem)
instance = GroundForwardSearchModel(problem, operators)
grounder = LPGroundingStrategy(problem, include_variable_inequalities=True)
grounded_fluents = [grounded_fluent.to_atom() for grounded_fluent in grounder.ground_state_variables().objects]
init = problem.init.as_atoms()

# add done predicate
donePre = lang.predicate('done')
achieved = lang.predicate('achieved')
# add done action
doneAct = problem.action('done', [], precondition = problem.goal,
effects = [
    iofs.AddEffect(donePre)
]) 



for x in grounded_fluents:
    if x not in problem.goal.subformulas:
        #   ; If (holding A) is not in the goal, but in the initial state
        #   (:action achieve_holding_A
        #       :precondition (and (done) (holding A))
        #       :effect (and (achieved_holding_A))
        #   )
        if x in init:
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
        ignore_A = problem.action('ignore_A',[],precondition = donePre,
            effects = [
                iofs.AddEffect(achieved)
            ])
        #   ; If (holding A) is not in the goal, and not in the initial state
        #   (:action achieve_holding_A
        #       :precondition (and (done) (not (holding A)))
        #       :effect (and (achieved_holding_A))
        #   )
        achieved_B = problem.action('achieved_B',[],precondition = donePre &~x,
            effects = [
                iofs.AddEffect(achieved)
            ])
#export
#writer = iofs.FstripsWriter(problem)
#writer.write("domain.pddl", "problem.pddl")
print(list(problem.actions))