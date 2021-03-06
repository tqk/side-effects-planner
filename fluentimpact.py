
import sys

import tarski_wrapper as tw

USAGE = "\n\tpython3 fluentimpact.py [--assess plan.ipc] <in-domain.pddl> <in-problem.pddl> <out-domain.pddl> <out-problem.pddl>\n"




def modify_domain(atomic_domain, stratified=False, assess=None):
    
    if assess is not None:
        if len(assess) == 0: # if we're trying to evalute the empty plan, we don't need the goal
            atomic_domain.goal = atomic_domain.init.as_atoms()[0]

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
            action.precondition = tw.land(*(action.precondition.subformulas), ~donePre(), flat=True)

    # Add the forced plan as a prefix.
    if assess is not None:
        tw.force_plan(atomic_domain, assess, avoid = ['done'])

    achieved_fluents = []

    if isinstance(atomic_domain.goal, tw.tarski.syntax.Atom):
        goal = [atomic_domain.goal]
    else:
        goal = atomic_domain.goal.subformulas

    for f in [f() for f in atomic_domain.language.predicates if f.arity == 0]:
        if f != donePre() and f not in goal and 'forced' not in str(f) and 'enabled' not in str(f):

            achieved = atomic_domain.language.predicate('achieved_'+tw.normalize_fluent(f))
            achieved_fluents.append(achieved)

            # If stratified, then the achievements must happen in order.
            if stratified and len(achieved_fluents) > 1:
                pospre = tw.land(f, donePre(), achieved_fluents[-2](), ~achieved(), flat=True)
                negpre = tw.land(~f, donePre(), achieved_fluents[-2](), ~achieved(), flat=True)
            else:
                pospre = f & donePre()
                negpre = ~f & donePre()

            if f in atomic_domain.init.as_atoms():

                atomic_domain.action('ignore_'+tw.normalize_fluent(f), [],
                                     precondition = negpre,
                                     effects = [
                                         tw.iofs.AddEffect(achieved()),
                                     ],
                                     cost = tw.cost1(atomic_domain))

                atomic_domain.action('achieve_'+tw.normalize_fluent(f), [],
                                     precondition = pospre,
                                     effects = [
                                         tw.iofs.AddEffect(achieved()),
                                     ])
            else:
                atomic_domain.action('ignore_'+tw.normalize_fluent(f), [],
                                     precondition = pospre,
                                     effects = [
                                         tw.iofs.AddEffect(achieved()),
                                     ],
                                     cost = tw.cost1(atomic_domain))

                atomic_domain.action('achieve_'+tw.normalize_fluent(f), [],
                                     precondition = negpre,
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

    if len(argv) != 4:
        print(USAGE)
        exit(1)

    #print("\n\tCompiling...", end='')
    domain_file = argv[0]
    problem_file = argv[1]
    out_domain_file = argv[2]
    out_problem_file = argv[3]

    domain = tw.parse_pddl(domain_file, problem_file)
    (grounded_fluents, init, goal, operators) = tw.ground_problem(domain)

    atomic_domain = tw.atomicize(grounded_fluents, init, goal, operators)

    modified_domain = modify_domain(atomic_domain, stratified=True, assess=plan)

    tw.write_pddl(modified_domain, out_domain_file, out_problem_file)

    #print('done!\n')
