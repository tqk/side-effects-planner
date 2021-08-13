#Creating the language
import tarski
from tarski.io import PDDLReader
from tarski.io import fstrips as iofs
from tarski.syntax import land
reader = PDDLReader(raise_on_error=True)
reader.parse_domain('./domainA.pddl')
problem = reader.parse_instance('./problemA.pddl')
lang = problem.language
#domain
#types
animal = lang.get('animal')
others = lang.get('others')
grid = lang.get('grid')
constant = lang.get('constant')

#predicates
adjacent = lang.get('adjacent')
on = lang.get('on')
clean = lang.get('clean')
polluted = lang.get('polluted')
succ = lang.get('succ')
budget = lang.get('budget')
acting = lang.get('acting')
free = lang.get('free') 

#constants
N0, N1, N2, N3 = [lang.get(f'c{k}') for k in range(0,4)]
G11, G12, G13, G14 = [lang.get(f'g{k}') for k in range(11,15)]
G21, G22, G23, G24 = [lang.get(f'g{k}') for k in range(21,25)]
G31, G32, G33, G34 = [lang.get(f'g{k}') for k in range(31,35)]
Tree = lang.get('tree')
Wood = lang.get('wood')
Fountain = lang.get('fountain')
Factory = lang.get('factory')
Truck = lang.get('truck')
Beaver = lang.get('beaver')
Racoon = lang.get('racoon')

#actions
TruckMove = problem.get_action('TruckMove')
arrive = problem.get_action('arrive')
clean = problem.get_action('clean')
AnimalMove = problem.get_action('AnimalMove')

#problem
#init
init = problem.init

#goal
goal_a = problem.goal
goal_b = land(on(Racoon, G13), on(Fountain, G13))
goal_c = land(on(Beaver, G11), on(Tree, G11))
goal_d = land(on(Beaver, G33), on(Wood, G33))



print('sorts:')
print(lang.sorts)
print('\n')
print('predicates:')
print(lang.predicates)
print('\n')
print('functions:')
print(lang.functions)
print('\n')
print('constants:')
print(lang.constants())
print('\n')
print('init:')
print(type(problem.init))
print(problem.init.__module__)
print('\n')
print('actions:')
print(list(problem.actions))
print('\n')
print('goal:')
print(problem.goal)
print('\n')

#export
writer = iofs.FstripsWriter(problem)
writer.write("domain.pddl", "problem.pddl")
    
    
  
  

