
import json, sys

import tarski_wrapper as tw

USAGE = "\n\tpython3 planimpact.py [--assess plan.ipc] <in-domain.pddl> <in-problem.pddl> <in-plans.py> <out-domain.pddl> <out-problem.pddl>\n"




def modify_domain(atomic_domain, in_plans, stratified=False, assess=None):
    if assess is not None:
        if len(assess) == 0: # if we're trying to evalute the empty plan, we don't need the goal
            atomic_domain.goal = atomic_domain.init.as_atoms()[0]
    

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
            state = tw.regress(state, tw.str_to_action(tw.normalize_action(act), atomic_domain))
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
            action.precondition = tw.land(*(action.precondition.subformulas), ~donePre(), flat=True)

    # Add the forced plan as a prefix.
    if assess is not None:
        tw.force_plan(atomic_domain, assess, avoid = ['done'])

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

    if stratified:
        atomic_domain.goal = achieved_fluents[-1]()
    else:
        atomic_domain.goal = tw.land(*[f() for f in achieved_fluents], flat=True)

    return atomic_domain



if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == '--assess':
        with open(sys.argv[2], 'r') as f:
            plan = [l.strip() for l in f.readlines() if ';' not in l]
        argv = sys.argv[3:]
    else:
        plan = None
        argv = sys.argv[1:]

    if len(argv) != 5:
        print(USAGE)
        exit(1)

    #print('\n\tCompiling problem...', end='')

    domain_file = argv[0]
    problem_file = argv[1]
    in_plans = argv[2]
    out_domain_file = argv[3]
    out_problem_file = argv[4]

    domain = tw.parse_pddl(domain_file, problem_file)
    (grounded_fluents, init, goal, operators) = tw.ground_problem(domain)

    atomic_domain = tw.atomicize(grounded_fluents, init, goal, operators)

    modified_domain = modify_domain(atomic_domain, in_plans, stratified=True, assess=plan)

    tw.write_pddl(modified_domain, out_domain_file, out_problem_file)

    #print('done!\n')
