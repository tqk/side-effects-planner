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

# add actingAgent sort
agent = lang.sort('agent')
achieved_pre = lang.sort('achieved_pre')
# add done predicate
donePre = lang.predicate('done')
achieved = lang.predicate('achievedA')
#add the acting agent object
actingAgent = lang.variable('actingAgent',agent)

# add done action
doneAct = problem.action('done', [], precondition = problem.goal,
effects = [
    iofs.AddEffect(donePre())
]) 




print(type(problem.init))
for x in problem.init.as_atoms():
    if x not in (problem.goal.__dict__)['subformulas']:
        #   ; If (holding A) is not in the goal, but in the initial state
        ##   (:action achieve_holding_A
        #       :precondition (and (done) (holding A))
        #       :effect (and (achieved_holding_A))
        #   )
        const = lang.variable(str(x),achieved_pre) 
        achieved_A = problem.action('achieved_A_'+str(x),[],precondition = (donePre()) & x,
            effects = [
                iofs.AddEffect(achieved())
            ])
        #   (:action ignore_holding_A
        #       :precondition (and (done))
        #       :effect (and (achieved_holding_A) (increase total-cost 1))
        #   )
        #   ; Must add (achieved_holding_A) to the goal
        ignore_A = problem.action('ignore_'+str(x),[],precondition = (donePre()),
            effects = [
                iofs.AddEffect(achieved())
            ])
        #   ; If (holding A) is not in the goal, and not in the initial state
        #   (:action achieve_holding_A
        #       :precondition (and (done) (not (holding A)))
        #       :effect (and (achieved_holding_A))
        #   )
        achieved_B = problem.action('achieved_B_'+str(x),[],precondition = (donePre()) & ~x,
            effects = [
                iofs.AddEffect(achieved())
            ])

print(problem.actions)

#export
writer = iofs.FstripsWriter(problem)
writer.write("domain.pddl", "problem.pddl")

