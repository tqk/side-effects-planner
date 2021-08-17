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
donePre = lang.predicate('done',agent)
#achieved_free = lang.predicate('achieved_free',grid)
print(type(donePre))
achieved = lang.predicate('achievedA',achieved_pre)

actingAgent = lang.variable('actingAgent',agent)

# add done action
doneAct = problem.action('done', [actingAgent], precondition = problem.goal,
effects = [
    iofs.AddEffect(donePre(actingAgent))
]) 

for x in problem.init.as_atoms():
    if x not in (problem.goal.__dict__)['subformulas']:
        #   ; If (holding A) is not in the goal, but in the initial state
        ##   (:action achieve_holding_A
        #       :precondition (and (done) (holding A))
        #       :effect (and (achieved_holding_A))
        #   )
        const = lang.variable(str(x),achieved_pre) 
        achieved_A = problem.action('achieved_A_'+str(x),[actingAgent, const],precondition = (donePre(actingAgent)) & x,
            effects = [
                iofs.AddEffect(achieved(const))
            ])
        #   (:action ignore_holding_A
        #       :precondition (and (done))
        #       :effect (and (achieved_holding_A) (increase total-cost 1))
        #   )
        #   ; Must add (achieved_holding_A) to the goal
        ignore_A = problem.action('ignore_'+str(x),[],precondition = (donePre(actingAgent)),
            effects = [
                iofs.AddEffect(achieved(const))
            ])
        #   ; If (holding A) is not in the goal, and not in the initial state
        #   (:action achieve_holding_A
        #       :precondition (and (done) (not (holding A)))
        #       :effect (and (achieved_holding_A))
        #   )
        achieved_B = problem.action('achieved_B_'+str(x),[],precondition = (donePre(actingAgent)) & ~x,
            effects = [
                iofs.AddEffect(achieved(const))
            ])
#export
#writer = iofs.FstripsWriter(problem)
#writer.write("domain.pddl", "problem.pddl")
print(list(problem.actions))