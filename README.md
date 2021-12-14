# Code for "Planning to Avoid Side Effects"

The code was run on a Linux machine (with Python 3.6) and may not run on other operating systems. To set up the dependencies, you can use docker (https://www.docker.com/) with the provided Dockerfile. Note that the fluent-, policy-, and goal-preserving compilations heavily rely on the [Tarski](https://github.com/aig-upf/tarski) library. When running docker, you will need the `--privileged` option. 

To run the experiments reported in the paper, execute

> python3 run.py

This will write various files to the ./logs and ./outputs directories, but all the important information is in the output of the command. For each domain X and problem Y, the output will include

> Running on problem Y of X domain

and then lines describing the various types of plans it finds and how well they do at avoiding side effects. Note that in the code the names of the problems are just numbers (e.g., 1, 2, 3, ...), but in the table in the paper the problems are given alphanumeric names (e.g. the five storage problems are named a, b, c, c2, and c3). 


To illustrate the output format, consider how the output might start for the first (and only) problem in the wildlife domain:

> Running on problem 1 of wildlife domain                                                                                                                    
>                                                                                                                                         
> Finding a plan with standard planning                                                                                                                      
>
> Time of downward --alias seq-opt-lmcut --plan-file outputs/wildlife1.ipc domains/wildlife/domain.pddl domains/wildlife/prob1.pddl > logs/wildlife1.ipc.txt:
0.6302692890167236                                                                                                                                         
>                                                                                                                                                           
> outputs/wildlife1.ipc                                                                                                                                      
> ; cost = 7 (unit cost)                                                                                                                                     

What we see is that it reports the time it took to find the plan, and also the plan cost. (The cost for standard planning is just the number of actions, though, which is not one of the things that we're interested in).

The output then continues. The plan found with standard planning is assessed for how well it avoids different types of side effects, starting with FSEs.

> Assessing the standard plan at fluent-preservation
> 
> Time of python3 fluentimpact.py --assess outputs/wildlife1.ipc domains/wildlife/domain.pddl domains/wildlife/prob1.pddl  outputs/wildlife1-fluent-domain-assess-wildlife1.ipc.pddl outputs/wildlife-fluent-problem1-assess-wildlife1.ipc.pddl:
1.7298624515533447
>
> Time of downward --alias seq-opt-lmcut --plan-file outputs/wildlife1fluent-assess-wildlife1.ipc.ipc outputs/wildlife1-fluent-domain-assess-wildlife1.ipc.pddl outputs/wildlife-fluent-problem1-assess-wildlife1.ipc.pddl > logs/wildlife1fluent-assess-wildlife1.ipc.ipc.txt:
41.57134199142456
>
> outputs/wildlife1fluent-assess-wildlife1.ipc.ipc
> ; cost = 17 (general cost)

The times reported here are not very important (they're just the time used in assessing how good the plan is at avoiding FSEs), but the "cost" of 17 that is reported is the number of FSEs that the plan that was found using standard planning has.

The plan is next assessed on how well it avoids PSEs ("plan"-preservation in the output refers to policy-preservation).

> Assessing the standard plan at plan-preservation
>
> Time of python3 planimpact.py --assess outputs/wildlife1.ipc domains/wildlife/domain.pddl domains/wildlife/prob1.pddl domains/wildlife/plans1.json outputs/wildlife1-plan-domain-assess-wildlife1.ipc.pddl outputs/wildlife-plan-problem1-assess-wildlife1.ipc.pddl:
1.3944733142852783
>
> Time of downward --alias seq-opt-lmcut --plan-file outputs/wildlife1plan-assess-wildlife1.ipc.ipc outputs/wildlife1-plan-domain-assess-wildlife1.ipc.pddl outputs/wildlife-plan-problem1-assess-wildlife1.ipc.pddl > logs/wildlife1plan-assess-wildlife1.ipc.ipc.txt:
47.01744222640991
>
> outputs/wildlife1plan-assess-wildlife1.ipc.ipc
> ; cost = 3 (general cost)

This time the value of the "cost" is the number of policy side effects. The plan is next assessed at avoiding GSEs; the output for that (not shown) can be interpreted analagously.

After performing those assessments of the standard plan, a fluent-preserving plan is found:

> Finding a fluent-preserving plan
>
> Time of python3 fluentimpact.py  domains/wildlife/domain.pddl domains/wildlife/prob1.pddl  outputs/wildlife1-fluent-domain.pddl outputs/wildlife-fluent-problem1.pddl:
> 1.8526947498321533
>
> Time of downward --alias seq-opt-lmcut --plan-file outputs/wildlife1fluent.ipc outputs/wildlife1-fluent-domain.pddl outputs/wildlife-fluent-problem1.pddl > logs/wildlife1fluent.ipc.txt:
> 56.1292405128479
>
> outputs/wildlife1fluent.ipc
> ; cost = 13 (general cost)

The first time reported is compilation time, and the second is planning time on the compilation. The cost (13) of the plan on the compiled problem is the number of FSEs it has. The fluent-preserving plan is then also assessed for how well it avoids PSEs and GSEs (similarly to how the standard plan was). 

Finally, policy-preserving and goal-preserving plans are found as well. The outputs about them can be intepreted analogously to the outputs for the fluent-preserving plan.

Note: When using the fluent-, policy-, or goal-preserving compilations, the order in which some things are written in the output files (e.g., the order fluents are listed in the initial state) may vary from compilation run to compilation run (because of how python iterates through some data structures). This may affect the tie-breaking used by planning software in selecting actions. So multiple runs of the experiments are not guaranteed to give identical results.
