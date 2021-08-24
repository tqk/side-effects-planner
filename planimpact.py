
import json, sys

import tarski_wrapper as tw

USAGE = "python3 planimpact.py <in-domain.pddl> <in-problem.pddl> <in-plans.py> <out-domain.pddl> <out-problem.pddl>"




def modify_domain(atomic_domain, in_plans, stratified=False):

    # Read the plans json from in_plans
    with open(in_plans, 'r') as f:
        plans = json.load(f)
    
    # Compute the goal from the text description
    goals = {}
    for agent in plans:
        goals[agent] = (set([tw.str_to_atom(f, atomic_domain) for f in plans[agent]['goal']]), set())
    
    subgoals = {agent: [goals[agent]] for agent in plans}
    for agent in plans:
        state = goals[agent]
        for act in reversed(plans[agent]['plan']):
            state = tw.regress(state, tw.str_to_action(act, atomic_domain))
            subgoals[agent].append(state)


    # Add done predicate
    donePre = atomic_domain.language.predicate('done')

    # # add done action
    atomic_domain.action('done', [],
                         precondition = atomic_domain.goal,
                         effects = [
                             tw.iofs.AddEffect(donePre())
                         ])

    # Don't allow regular actions after done
    for action in atomic_domain.actions.values():
        if action.name != 'done':
            action.precondition = tw.land(action.precondition, ~donePre(), flat=True)

    achieved_fluents = []
    for agent in subgoals:

        achieved = atomic_domain.language.predicate(f'achieved_{agent}')
        achieved_fluents.append(achieved)

        atomic_domain.action(f'ignore_{agent}', [],
                             precondition = ~achieved() & donePre(),
                             effects = [
                                 tw.iofs.AddEffect(achieved()),
                             ],
                             cost = tw.cost1(atomic_domain))

        for i, state in enumerate(subgoals[agent]):

            statef = list(state[0]) + [~f for f in state[1]]
        
            # If stratified, then the achievements must happen in order.
            if stratified and len(achieved_fluents) > 1:
                pre = tw.land(*statef, ~achieved(), donePre(), achieved_fluents[-2](), flat=True)
            else:
                pre = tw.land(*statef, ~achieved(), donePre(), flat=True)

            atomic_domain.action(f'achieve_{agent}_{i}', [],
                                 precondition = pre,
                                 effects = [
                                     tw.iofs.AddEffect(achieved()),
                                 ])

    atomic_domain.goal = tw.land(*[f() for f in achieved_fluents], flat=True)

    return atomic_domain



if __name__ == '__main__':
    if len(sys.argv) != 6:
        print(USAGE)
        exit(1)
    
    print('\n\tCompiling problem...', end='')

    domain_file = sys.argv[1]
    problem_file = sys.argv[2]
    in_plans = sys.argv[3]
    out_domain_file = sys.argv[4]
    out_problem_file = sys.argv[5]

    domain = tw.parse_pddl(domain_file, problem_file)
    (grounded_fluents, init, goal, operators) = tw.ground_problem(domain)

    atomic_domain = tw.atomicize(grounded_fluents, init, goal, operators)

    modified_domain = modify_domain(atomic_domain, in_plans, stratified=True)

    tw.write_pddl(modified_domain, out_domain_file, out_problem_file)

    print('done!\n')
