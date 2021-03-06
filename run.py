import os
import subprocess
import time
from utils import convert_plan

#problems = {
#    'wildlife': 1,
#    'floor-tile': 3,
#    'storage': 3,
#    'zeno': 3
#}
#compilations = ['fluent', 'plan', 'goal']

outdir = "outputs"
logdir = "logs"



def timed_run(command):

    #print(f"Running {command}")

    start = time.time()
    subprocess.call(command, shell=True, executable='/bin/bash')
    end = time.time()

    print(f"Time of {command}:\n{end-start}\n")


def filenames(domain, problem, compilation=None, assess=None):
    d = f"domains/{domain}/domain.pddl"
    p = f"domains/{domain}/prob{problem}.pddl"
    if compilation is None:
        return (d, p)
    else:
        if assess is None:
            assess2 = ""
        else:
            assess2 = "-assess-" + assess
        return (f"{outdir}/{domain}{problem}-{compilation}-domain{assess2}.pddl", f"{outdir}/{domain}-{compilation}-problem{problem}{assess2}.pddl")

def plansfilename(domain, problem):
    # gets name of file with lists of plans for domain and problem
    return f"domains/{domain}/plans{problem}.json"

def planname(domain, problem, compilation=None, assess=None):
    # gets name to use for output plan
    if compilation is None:
        compilation = ""
    if assess is None:
        assess2 = ""
    else:
        assess2 = "-assess-" + assess
    return f"{domain}{problem}{compilation}{assess2}.ipc"

def planner(domain, problem, compilation=None, assess=None, prog=None):
    if prog is None:
        prog = "downward --alias seq-opt-lmcut"

    domain_file, problem_file = filenames(domain, problem, compilation, assess)


    outputfile = f"{outdir}/{planname(domain,problem,compilation,assess)}"

    if compilation is None:
        compilation = ""
    command = f"{prog} --plan-file {outputfile} {domain_file} {problem_file} > {logdir}/{planname(domain,problem,compilation,assess)}.txt"

    timed_run(command)

    if prog=='lama': # find name of the last file that was output
        number = 1
        while os.path.isfile(f"{outputfile}.{number+1}"):
            number = number+1
        outputfile = f"{outputfile}.{number}"
        assert os.path.isfile(outputfile)

    print(outputfile)
    subprocess.call(f"tail -n1 {outputfile}", shell=True, executable='/bin/bash')
    print()



def compilation(domain, problem, x, assess=None):
    # x is "fluent", "plan", or "goal"
    domain_file, problem_file = filenames(domain, problem)
    compiled_domain_file, compiled_problem_file = filenames(domain, problem, x, assess)

    if x=="fluent":
        plan_file = ""
    else:
        plan_file = plansfilename(domain, problem)

    if assess is None:
        assess2 = ""
    else:
        assess2 = f"--assess {outdir}/{assess}"

    command = f"python3 {x}impact.py {assess2} {domain_file} {problem_file} {plan_file} {compiled_domain_file} {compiled_problem_file}"

    return timed_run(command)


def sanitytest(domain, problem):
    print(f"Running on problem {problem} of {domain} domain")

    print("Sanity check: how many side effects are avoided by an empty plan?\n")
    for x in [#'fluent',
        'plan', 'goal']:

        print(f"Assessing the empty plan at {x}-preservation\n")

        compilation(domain, problem, x, assess="empty.ipc")
        if x=='goal':
            program = 'lama'
        else:
            program = None
        planner(domain, problem, x, assess="empty.ipc", prog=program)

def runtests(domain, problem):

    print(f"Running on problem {problem} of {domain} domain\n")


    # first, just solve the problem without trying to aviod SEs

    print("Finding a plan with standard planning\n")

    planner(domain, problem)


    # now evaluate how well that solution does at avoiding FSEs, PSEs, GSEs
    for x in ['fluent', 'plan', 'goal']:

        print(f"Assessing the standard plan at {x}-preservation\n")

        compilation(domain, problem, x, assess=planname(domain, problem))
        if x=='goal':
            program = 'lama'
        else:
            program = None
        planner(domain, problem, x, assess=planname(domain, problem), prog=program)




    # find the fluent-preserving compilation

    print("Finding a fluent-preserving plan\n")

    compilation(domain, problem, 'fluent')
    # solve that
    planner(domain,problem,'fluent')

    # now evaluate how well the solution does at avoiding PSEs and GSEs
    # we need to convert the plan found for the fluent-preserving compilation to work for the original problem
    converted_plan = f"converted-{planname(domain, problem, 'fluent')}"
    convert_plan(f"{outdir}/{planname(domain, problem, 'fluent')}", f"{outdir}/{converted_plan}", 'done')


    for x in ['plan', 'goal']:

        print(f"Assessing the fluent-preserving plan at {x}-preservation\n")

        compilation(domain, problem, x, assess=converted_plan)
        if x=='goal':
            program = 'lama'
        else:
            program = None
        planner(domain, problem, x, assess=converted_plan, prog=program)


    # find the plan-preserving compilation
    print("Finding a policy-preserving plan\n")

    compilation(domain, problem, 'plan')
    # solve that
    planner(domain,problem,'plan')


    # find the goal-preserving compilation
    print("Finding a goal-preserving plan\n")

    compilation(domain, problem, 'goal')
    # solve that
    planner(domain,problem,'goal', prog='lama')


if __name__ == '__main__':
    #sanitytest('storage',1)
    #sanitytest('storage',2)
    #sanitytest('storage',3)
    #sanitytest('zeno',1)
    #sanitytest('zeno',2)
    #sanitytest('zeno',3)
    #sanitytest('floor-tile',1)
    #sanitytest('floor-tile',2)
    #sanitytest('floor-tile',3)

    #sanitytest('wildlife',1)

    runtests('wildlife',1)
    runtests('storage',1)
    runtests('storage',2)
    runtests('storage',3)
    runtests('storage',4)
    runtests('storage',5)
    runtests('zeno',1)
    runtests('zeno',2)
    runtests('zeno',3)
    runtests('floor-tile',1)
    runtests('floor-tile',2)
    runtests('floor-tile',3)


