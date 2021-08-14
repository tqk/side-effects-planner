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
N0, N1, N2, N3 = [lang.get(f'n{k}') for k in range(0,4)]
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

#(clean G11) (clean G12) (clean G13) (clean G14)
#(clean G21) (clean G22) (clean G23) (clean G24)
#(clean G32) (clean G33) (clean G34)
#(polluted G31)
achieved_polluted = lang.predicate('achieved_polluted',grid)
#(free G11) (free G12) (free G13) (free G14)
#(free G22) (free G24)
#(free G32) (free G33) (free G34)
achieved_free = lang.predicate('achieved_free',grid)
#(on Truck G31)
achieved_on = lang.predicate('achieved_on',others, grid)

#define new actions
#first define the gerneral parameters: grid and Truck
gridx = lang.variable('gridx',grid)
Truckx = lang.variable('Truckx',others)
#   (holding A)   
#   (:action done
#       :precondition (and <whatever the original goal is>)
#       :effect (and (done))
#   )   
#   ; If (holding A) is in the goal, then just leave (holding A) in the goal
done = problem.action('done', [], precondition = on(Truck, G34) & on(Factory, G34),
effects = [
    iofs.AddEffect(on(Truck, G34)),
    iofs.AddEffect(on(Factory, G34))
])   
   
#   ; If (holding A) is not in the goal, but in the initial state
#   (:action achieve_holding_A
#       :precondition (and (done) (holding A))
#       :effect (and (achieved_holding_A))
#   )
achieved_polluted_gridA = problem.action('achieved_polluted_gridA',[gridx],precondition = on(Truck, G34) & on(Factory, G34) &polluted(gridx),
    effects = [
        iofs.AddEffect(achieved_polluted(gridx))
    ])
achieved_free_gridA = problem.action('achieved_free_gridA',[gridx],precondition = on(Truck, G34) & on(Factory, G34) &free(gridx),
    effects = [
        iofs.AddEffect(achieved_free(gridx))
    ]) 
achieved_on_gridA = problem.action('achieved_on_gridA',[gridx,Truckx],precondition = on(Truck, G34) & on(Factory, G34) &on(Truckx ,gridx),
    effects = [
        iofs.AddEffect(achieved_on(Truckx ,gridx))
    ]) 
#   (:action ignore_holding_A
#       :precondition (and (done))
#       :effect (and (achieved_holding_A) (increase total-cost 1))
#   )
#   ; Must add (achieved_holding_A) to the goal
ignore_polluted_gridA = problem.action('ignore_polluted_gridA',[gridx],precondition = on(Truck, G34) & on(Factory, G34),
    effects = [
        iofs.AddEffect(achieved_polluted(gridx))
    ])
ignore_free_gridA = problem.action('ignore_free_gridA',[gridx],precondition = on(Truck, G34) & on(Factory, G34),
    effects = [
        iofs.AddEffect(achieved_free(gridx))
    ]) 
ignore_on_gridA = problem.action('ignore_on_gridA',[gridx,Truckx],precondition = on(Truck, G34) & on(Factory, G34),
    effects = [
        iofs.AddEffect(achieved_on(Truckx ,gridx))
    ])    
   
   
#   ; If (holding A) is not in the goal, and not in the initial state
#   (:action achieve_holding_A
#       :precondition (and (done) (not (holding A)))
#       :effect (and (achieved_holding_A))
#   )
achieved_polluted_gridB = problem.action('achieved_polluted_gridB',[gridx],precondition = on(Truck, G34) & on(Factory, G34) &~polluted(gridx),
    effects = [
        iofs.AddEffect(achieved_polluted(gridx))
    ])
achieved_free_gridB = problem.action('achieved_free_gridB',[gridx],precondition = on(Truck, G34) & on(Factory, G34) &~free(gridx),
    effects = [
        iofs.AddEffect(achieved_free(gridx))
    ]) 
achieved_on_gridB = problem.action('achieved_on_gridB',[gridx,Truckx],precondition = on(Truck, G34) & on(Factory, G34) &~on(Truckx ,gridx),
    effects = [
        iofs.AddEffect(achieved_on(Truckx ,gridx))
    ]) 

   
#   (:action ignore_holding_A
#       :precondition (and (done))
#       :effect (and (achieved_holding_A) (increase total-cost 1))
#   )
#   ; Must add (achieved_holding_A) to the goal


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
print(problem.init)
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
    
    
  
  

