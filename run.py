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
    
    #print(f"Running {command}")
    
    start = time.time()
    subprocess.call(command, shell=True, executable='/bin/bash')
    end = time.time()
    
    print(f"Time of {command}:\n{end-start}\n")
    
    return end-start

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
        return (f"{outdir}/{compilation}-{domain}-domain{assess2}.pddl", f"{outdir}/{compilation}-{domain}-problem{problem}{assess2}.pddl")
    
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

def planner(domain, problem, compilation=None, assess=None, prog="downward --alias seq-opt-lmcut"):
    domain_file, problem_file = filenames(domain, problem, compilation, assess)
    
    if compilation is None: 
        compilation = ""
    command = f"{prog} --plan-file {outdir}/{planname(domain,problem,compilation,assess)} {domain_file} {problem_file} > {logdir}/{planname(domain,problem,compilation,assess)}.txt"
    
    return timed_run(command)



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

 def runtests(domain, problem):
     
    print(f"Running on problem {problem} of {domain} domain\n")
    
    # first, just solve the problem without trying to aviod SEs
    planner(domain, problem)
    
    
    # now evaluate how well that solution does at avoiding FSEs, PSEs, GSEs
    for x in ['fluent', 'plan', 'goal']:
    
        compilation(domain, problem, x, assess=planname(domain, problem))
        planner(domain, problem, x, assess=planname(domain, problem))
        
    break
    
    
    # find the fluent-preserving compilation
    
    compilation(domain, problem, 'fluent')
    # solve that
    planner(domain,problem,'fluent')
    
    # now evaluate how well the solution does at avoiding PSEs and GSEs
    # ...
    break
    
    
    # find the plan-preserving compilation
    compilation(domain, problem, 'plan')
    # solve that
    planner(domain,problem,'plan')
    
    
    # find the goal-preserving compilation
    compilation(domain, problem, 'goal')
    # solve that
    planner(domain,problem,'goal', prog='lama')


if __name__ == '__main__':
    
    for domain in problems:
        print(f"Running on {domain} domain\n")
        
        for problem in range(1, problems[domain]+1):
            runtests(domain, problem)
       
            
