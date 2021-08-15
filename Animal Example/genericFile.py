import sys
import tarski
from tarski.io import PDDLReader
from tarski.io import fstrips as iofs
from tarski.syntax import land

# first argument: path to the domain file
# second argument: path to the problem file
a = str(sys.argv[1])
b = str(sys.argv[2])
#print(a)  #'./domainA.pddl'
#print(b)  #'./problemA.pddl'

# read the existing model 
reader = PDDLReader(raise_on_error=True)
reader.parse_domain(format(a))
problem = reader.parse_instance(format(b))
lang = problem.language


# add done predicate
donePre = lang.predicate('done')
print(type(donePre))
achieved = lang.predicate('achieved')
# add done action
doneAct = problem.action('done', [], precondition = problem.goal,
effects = [
    iofs.AddEffect(donePre)
]) 

for x in problem.init.as_atoms():
    print(type((problem.goal.__dict__)['subformulas'][0]))
    if x not in (problem.goal.__dict__)['subformulas']:
        #   ; If (holding A) is not in the goal, but in the initial state
        #   (:action achieve_holding_A
        #       :precondition (and (done) (holding A))
        #       :effect (and (achieved_holding_A))
        #   )
        achieved_polluted_gridA = problem.action('achieved_A',[],precondition = donePre & x,
            effects = [
                iofs.AddEffect((achieved))
        ])
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