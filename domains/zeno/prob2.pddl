; one non-goal fluents has been modified 
(define (problem ZTRAVEL-1-3)
(:domain zeno-travel)
(:objects
	plane1 - aircraft
	plane2 - aircraft
	person1 - people
	person2 - people
	person3 - people
	city0 - city
	city1 - city
	city2 - city
	fl0 - flevel
	fl1 - flevel
	fl2 - flevel
	fl3 - flevel
	fl4 - flevel
	fl5 - flevel
	fl6 - flevel
	)
(:init
	(at plane1 city0)
	(at plane2 city1)

	(fuel-level plane1 fl2)
	(fuel-level plane2 fl2)
	(fuel-inventory city0 fl2)
	(fuel-inventory city1 fl2)
	(fuel-inventory city2 fl2)

	(at person1 city2)
	(at person2 city1)
	(at person3 city2)
	(next fl0 fl1)
	(next fl1 fl2)
	(next fl2 fl3)
	(next fl3 fl4)
	(next fl4 fl5)
	(next fl5 fl6)
	(acting plane1)
)
(:goal (and 
	(at person1 city0)
	(at person3 city0)
))
;(:goal (and 
;	(at person3 city0)
;	))
)