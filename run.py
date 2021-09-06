import os
import subprocess
import time

problems = {
    'animal': 1,
    #'floor-tile': 3,
    #'storage': 3,
    #'zeno': 3
}
compilations = ['fluent', 'plan', 'goal']

outdir = "outputs"
logdir = "logs"



def timed_run(command):
    
    print(f"Running {command}")
    
    start = time.time()
    subprocess.call(command, shell=True, executable='/bin/bash')
    end = time.time()
    return f"Time of {command}: {end-start}"

def filenames(domain, problem, compilation=None):
    d = f"domains/{domain}/domain.pddl"
    p = f"domains/{domain}/prob{problem}.pddl"
    if compilation is None:
        return (d, p)
    else:
        return (f"{outdir}/{compilation}-{domain}-domain.pddl", f"{outdir}/{compilation}-{domain}-problem{problem}.pddl")
def planfilename(domain, problem):
    return f"domains/{domain}/plans{problem}.json"

def planner(domain, problem, compilation=None, prog="downward --alias seq-opt-lmcut"):
    domain_file, problem_file = filenames(domain, problem, compilation)
    
    if compilation is None: 
        compilation = ""
    command = f"{prog} --plan-file {outdir}/{domain}{problem}{compilation}.ipc {domain_file} {problem_file} > {logdir}/{domain}{problem}{compilation}.txt"
    
    return timed_run(command)



def compilation(domain, problem, x):
    # x is "fluent", "plan", or "goal"
    domain_file, problem_file = filenames(domain, problem)
    compiled_domain_file, compiled_problem_file = filenames(domain, problem, x)
    
    if x=="fluent":
        plan_file = ""
    else:
        plan_file = planfilename(domain, problem)
    
    command = f"python3 {x}impact.py {domain_file} {problem_file} {plan_file} {compiled_domain_file} {compiled_problem_file}"

    return timed_run(command)



if __name__ == '__main__':
    
    for domain in problems:
        print(f"Running on {domain} domain")
        
        for problem in range(1, problems[domain]+1):
            print(f"Running on problem {problem} of {domain} domain")
            
            # first, just solve the problem
            #print(planner(domain, problem))
            
            # find the fluent-preserving compilation
            
            #print(compilation(domain, problem, 'fluent'))
            # solve that
            #print(planner(domain,problem,'fluent'))
            
            # find the plan-preserving compilation
            #print(compilation(domain, problem, 'plan'))
            # solve that
            #print(planner(domain,problem,'plan'))
            
            
            # find the goal-preserving compilation
            print(compilation(domain, problem, 'goal'))
            # solve that
            print(planner(domain,problem,'goal','lama'))
            
