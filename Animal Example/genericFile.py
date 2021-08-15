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
# add done action
doneAct = problem.action('done', [], precondition = problem.goal,
effects = [
    iofs.AddEffect(donePre)
]) 

for x in problem.init.as_atoms():
    if x not in (problem.goal.__dict__)['subformulas']:
        pass
#export
#writer = iofs.FstripsWriter(problem)
#writer.write("domain.pddl", "problem.pddl")
print(list(problem.actions))