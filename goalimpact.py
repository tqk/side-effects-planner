
import json, sys

from tarski.fstrips.fstrips import DelEffect, language

import tarski_wrapper as tw

USAGE = "\n\tpython3 goalimpact.py [--assess plan.ipc] <in-domain.pddl> <in-problem.pddl> <in-plans.py> <out-domain.pddl> <out-problem.pddl>\n"




def modify_domain(atomic_domain, in_plans, stratified=False, assess=None, skip_duplicate_goals=True):

    # Read the plans json from in_plans
    with open(in_plans, 'r') as f:
        goaldata = json.load(f)

    # Compute the goal from the text description
    goals = {}
    goal_hash = set()
    for agent in goaldata:
        for i, goal in enumerate(goaldata[agent]):
            agname = agent + str(i)
            ghash = '//'.join(sorted(map(str, set([tw.str_to_atom(f, atomic_domain) for f in goal['goal']]))))
            if not(skip_duplicate_goals and ghash in goal_hash):
                goals[agname] = set([tw.str_to_atom(f, atomic_domain) for f in goal['goal']])
            goal_hash.add(ghash)

    # Grab the agent acting fluents for use later on in the phases. Doesn't include initial
    acting_fluents = list(filter(lambda x: 'acting' in str(x.name), atomic_domain.language.predicates))
    # print(acting_fluents)

    # Clone all of the fluents for saving
    orig_fluents = [f for f in atomic_domain.language.predicates if f.arity == 0 and 'acting' not in str(f.name)]
    cloned_fluents = []
    orig_to_cloned = {}
    for f in orig_fluents:
        cloned_fluents.append(atomic_domain.language.predicate(f'cloned_{f.name}'))
        orig_to_cloned[f] = cloned_fluents[-1]

    # Special mode fluents
    mode_confirming = atomic_domain.language.predicate('mode_confirming') # everything after the main agent
    mode_resetting = atomic_domain.language.predicate('mode_resetting') # forcing a state reset

    # Add a phase to clone the final state
    atomic_domain.action('clone', [],
                         precondition = tw.land(atomic_domain.goal, ~mode_confirming(), flat=True),
                         effects = [tw.iofs.AddEffect(orig_to_cloned[f](), f()) for f in orig_fluents] + \
                                    [tw.iofs.DelEffect(f()) for f in acting_fluents] + \
                                    [tw.iofs.AddEffect(mode_confirming()), tw.iofs.AddEffect(mode_resetting())])

    def get_actor_fluent(ag):
        for f in acting_fluents:
            if ag.lower().startswith(str(f.name).split('acting_')[1]):
                return f

    # Action to reset the state for each acting agent
    for ag in goaldata:
        actor = get_actor_fluent(ag)
        atomic_domain.action('reset_'+ag, [],
                             precondition = mode_resetting(),
                             effects = [tw.iofs.AddEffect(f(), orig_to_cloned[f]()) for f in orig_fluents] + \
                                        [tw.iofs.DelEffect(f(), ~orig_to_cloned[f]()) for f in orig_fluents] + \
                                        [tw.iofs.DelEffect(f()) for f in acting_fluents if ag.lower() not in str(f.name)] + \
                                        [tw.iofs.DelEffect(mode_resetting()), tw.iofs.AddEffect(actor())])

    # Add the forced plan as a prefix.
    if assess:
        tw.force_plan(atomic_domain, assess, avoid = ['done', 'clone', 'reset'])

    achieved_fluents = []
    for agent in goals:

        achieved = atomic_domain.language.predicate(f'achieved_{agent}')
        achieved_fluents.append(achieved)

        actor = get_actor_fluent(agent)

        # If stratified, then the achievements must happen in order.
        if stratified and len(achieved_fluents) > 1:
            pre = tw.land(actor(), ~achieved(), achieved_fluents[-2](), mode_confirming(), ~mode_resetting(), flat=True)
        else:
            pre = tw.land(actor(), ~achieved(), mode_confirming(), ~mode_resetting(), flat=True)

        atomic_domain.action(f'ignore_{agent}', [],
                             precondition = pre,
                             effects = [
                                 tw.iofs.AddEffect(achieved()),
                                 tw.iofs.AddEffect(mode_resetting())
                             ],
                             cost = tw.cost1(atomic_domain))

        statef = list(goals[agent])

        # If stratified, then the achievements must happen in order.
        if stratified and len(achieved_fluents) > 1:
            pre = tw.land(*statef, actor(), ~achieved(), mode_confirming(), ~mode_resetting(), achieved_fluents[-2](), flat=True)
        else:
            pre = tw.land(*statef, actor(), ~achieved(), mode_confirming(), ~mode_resetting(), flat=True)

        atomic_domain.action(f'achieve_{agent}_{i}', [],
                                precondition = pre,
                                effects = [
                                    tw.iofs.AddEffect(achieved()),
                                    tw.iofs.AddEffect(mode_resetting())
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
