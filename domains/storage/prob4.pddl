; two non-goal fluents has been modified

; Map of the Depots:
; 00
; *0
;---
; 0: depot0 area
; *: Depot access point
; =: Transit area

(define (problem storage-5)
(:domain Storage-Propositional)
(:objects
	depot0-1-1 depot0-1-2 depot0-2-1 depot0-2-2 container-0-0 container-0-1 depot0-11-1 depot0-11-2 depot0-12-1 depot0-12-2 container-10-0 container-10-1 - storearea
	hoist0 hoist1 - hoist
	crate0 crate1 crate10 crate11 - crate
	container0 container10 - container
	depot0 depot10 - depot
	loadarea loadarea1 - transitarea

)

(:init
	(connected depot0-1-1 depot0-2-1)
	(connected depot0-1-1 depot0-1-2)
	(connected depot0-1-2 depot0-2-2)
	(connected depot0-1-2 depot0-1-1)
	(connected depot0-2-1 depot0-1-1)
	(connected depot0-2-1 depot0-2-2)
	(connected depot0-2-2 depot0-1-2)
	(connected depot0-2-2 depot0-2-1)
	(in depot0-1-1 depot0)
	(in depot0-1-2 depot0)
	(in depot0-2-1 depot0)
	(in depot0-2-2 depot0)
	(on crate0 container-0-0)
	(on crate1 container-0-1)
	(in crate0 container0)
	(in crate1 container0)
	(in container-0-0 container0)
	(in container-0-1 container0)
	(connected loadarea container-0-0)
	(connected container-0-0 loadarea)
	(connected loadarea container-0-1)
	(connected container-0-1 loadarea)
	(connected depot0-2-1 loadarea)
	(connected loadarea depot0-2-1)
	(clear depot0-1-1);
	(clear depot0-2-2);
	(clear depot0-2-1);
	;;
	(at hoist0 loadarea)
	(available hoist0)
	(at hoist1 depot0-1-2)
	(available hoist1)
	(acting hoist1))

(:goal (and
	(on crate0 depot0-1-1)
	(on crate1 depot0-2-2)
	))


)

