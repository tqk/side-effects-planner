
import json, sys

import tarski_wrapper as tw

USAGE = "\n\tpython3 planimpact.py <in-domain.pddl> <in-problem.pddl> <in-plans.py> <out-domain.pddl> <out-problem.pddl>\n"




def modify_domain(atomic_domain, in_plans, stratified=False):

    # Read the plans json from in_plans
    with open(in_plans, 'r') as f:
        plandata = json.load(f)

    # Compute the goal from the text description
    plans = {}
    goals = {}
    for agent in plandata:
        for i, plangoal in enumerate(plandata[agent]):
            agname = agent + str(i)
            goals[agname] = set([tw.str_to_atom(f, atomic_domain) for f in plangoal['goal']])
            plans[agname] = plangoal['plan']

    subgoals = {agent: [goals[agent]] for agent in plans}
    for agent in plans:
        state = goals[agent]
        for act in reversed(plans[agent]):
            state = tw.regress(state, tw.str_to_action(act, atomic_domain))
            subgoals[agent].append(state)


    # Add done predicate
    donePre = atomic_domain.language.predicate('done')

    # add done action
    #  for this, we allow ever agent to act, since it's required in their regressed goal
    active_fluents = [tw.str_to_atom(f'acting_{ag.lower()}', atomic_domain) for ag in plandata]
    atomic_domain.action('done', [],
                         precondition = atomic_domain.goal,
                         effects = [tw.iofs.AddEffect(donePre())] +\
                                   [tw.iofs.AddEffect(a) for a in active_fluents])

    # Don't allow regular actions after done
    for action in atomic_domain.actions.values():
        if action.name != 'done':
            action.precondition = tw.land(action.precondition, ~donePre(), flat=True)

    achieved_fluents = []
    for agent in subgoals:

        achieved = atomic_domain.language.predicate(f'achieved_{agent}')
        achieved_fluents.append(achieved)

        # If stratified, then the achievements must happen in order.
        if stratified and len(achieved_fluents) > 1:
            pre = tw.land(~achieved(), achieved_fluents[-2](), donePre(), flat=True)
        else:
            pre = tw.land(~achieved(), donePre(), flat=True)

        atomic_domain.action(f'ignore_{agent}', [],
                             precondition = pre,
                             effects = [
                                 tw.iofs.AddEffect(achieved()),
                             ],
                             cost = tw.cost1(atomic_domain))

        for i, state in enumerate(subgoals[agent]):

            statef = list(state)

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
