
import sys
from tarski.io import fstrips as iofs
from tarski.syntax import land

from tarski_wrapper import *

USAGE = "python3 goalimpact.py <in-domain.pddl> <in-problem.pddl> <out-domain.pddl> <out-problem.pddl>"




def modify_domain(atomic_domain, stratified=False):

    # Add done predicate
    donePre = atomic_domain.language.predicate('done')

    # # add done action
    atomic_domain.action('done', [],
                         precondition = atomic_domain.goal,
                         effects = [
                             iofs.AddEffect(donePre())
                         ])

    # Don't allow regular actions after done
    for action in atomic_domain.actions.values():
        if action.name != 'done':
            action.precondition = land(action.precondition, ~donePre())

    achieved_fluents = []

    if isinstance(atomic_domain.goal, tarski.syntax.Atom):
        goal = [atomic_domain.goal]
    else:
        goal = atomic_domain.goal

    for f in [f() for f in atomic_domain.language.predicates if f.arity == 0]:
        if f != donePre() and f not in goal:

            achieved = atomic_domain.language.predicate('achieved_'+normalize_fluent(f))
            achieved_fluents.append(achieved)

            # If stratified, then the achievements must happen in order.
            if stratified and len(achieved_fluents) > 1:
                pospre = land(f, donePre(), achieved_fluents[-2](), flat=True)
                negpre = land(~f, donePre(), achieved_fluents[-2](), flat=True)
            else:
                pospre = f & donePre()
                negpre = ~f & donePre()

            if f in atomic_domain.init.as_atoms():

                atomic_domain.action('ignore_'+normalize_fluent(f), [],
                                     precondition = negpre,
                                     effects = [
                                         iofs.AddEffect(achieved()),
                                     ],
                                     cost = iofs.AdditiveActionCost(atomic_domain.language.constant(1, atomic_domain.language.get_sort('Integer'))))

                atomic_domain.action('achieve_'+normalize_fluent(f), [],
                                     precondition = pospre,
                                     effects = [
                                         iofs.AddEffect(achieved()),
                                     ])
            else:
                atomic_domain.action('ignore_'+normalize_fluent(f), [],
                                     precondition = pospre,
                                     effects = [
                                         iofs.AddEffect(achieved()),
                                     ],
                                     cost = iofs.AdditiveActionCost(atomic_domain.language.constant(1, atomic_domain.language.get_sort('Integer'))))

                atomic_domain.action('achieve_'+normalize_fluent(f), [],
                                     precondition = negpre,
                                     effects = [
                                         iofs.AddEffect(achieved()),
                                     ])

    atomic_domain.goal = land(*[f() for f in achieved_fluents], flat=True)

    return atomic_domain



if __name__ == '__main__':
    if len(sys.argv) != 5:
        print(USAGE)
        exit(1)

    domain_file = sys.argv[1]
    problem_file = sys.argv[2]
    out_domain_file = sys.argv[3]
    out_problem_file = sys.argv[4]

    domain = parse_pddl(domain_file, problem_file)
    (grounded_fluents, init, goal, operators) = ground_problem(domain)

    atomic_domain = atomicize(grounded_fluents, init, goal, operators)

    modified_domain = modify_domain(atomic_domain, stratified=True)

    write_pddl(modified_domain, out_domain_file, out_problem_file)

    print('Huzzah!')
