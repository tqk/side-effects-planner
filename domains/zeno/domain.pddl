




    ; Domain: Moving people on/off airplains that fly around and refuel

    ; Relevance: Can potentially add a pilot persona for the agent, and
    ;  they can leave planes around the place





(define (domain zeno-travel)
(:requirements :typing)
(:types flevel
		people aircraft - object
		city)
(:predicates
	 (at ?x - object ?c - city) (in ?p - object ?a - aircraft) (fuel-level ?a - aircraft ?l - flevel) (next ?l1 - flevel ?l2 - flevel)  
	 (acting ?a - aircraft) (fuel-inventory ?c - city ?l - flevel))
(:action board
 :parameters ( ?p - people
 				?a - aircraft 
 				?c - city)
 :precondition
	(and    (at ?p ?c) (at ?a ?c) (acting ?a))
 :effect
	(and (in ?p ?a) (not (at ?p ?c))))

(:action debark
 :parameters ( ?p - people
 				?a - aircraft 
				?c - city)
 :precondition
	(and  (in ?p ?a) (at ?a ?c) (acting ?a))
 :effect
	(and (at ?p ?c) (not (in ?p ?a))))

(:action fly
 :parameters ( ?a - aircraft ?c1 - city ?c2 - city ?l1 - flevel ?l2 - flevel)
 :precondition
	(and    (at ?a ?c1) (fuel-level ?a ?l1) (next ?l2 ?l1) (acting ?a) )
 :effect
	(and (at ?a ?c2) (fuel-level ?a ?l2) (not (at ?a ?c1)) (not (fuel-level ?a ?l1))  ))

(:action zoom
 :parameters ( ?a - aircraft 
 				?c1 - city 
				?c2 - city 
				?l1 - flevel 
				?l2 - flevel 
				?l3 - flevel)
 :precondition
	(and (at ?a ?c1) (fuel-level ?a ?l1) (next ?l2 ?l1) (next ?l3 ?l2) (acting ?a) )
 :effect
	(and (at ?a ?c2) (fuel-level ?a ?l3) (not (at ?a ?c1)) (not (fuel-level ?a ?l1)) ))

(:action refuel
 :parameters ( ?a - aircraft 
 				?c - city 
				?l - flevel 
				?l1 - flevel
				?l2 - flevel
				?l3 - flevel)
 :precondition
	(and   (fuel-level ?a ?l) (next ?l ?l1) (at ?a ?c) (acting ?a) (fuel-inventory ?c ?l2) (next ?l3 ?l2))
 :effect
	(and (fuel-level ?a ?l1) (not (fuel-level ?a ?l)) (fuel-inventory ?c ?l3) (not(fuel-inventory ?c ?l2)) ))

)