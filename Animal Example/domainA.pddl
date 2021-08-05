(define (domain AnimalExample-d)
    (:requirements :strips :typing )
    (:types
        animal others - object
        grid
        constant
    )
    (:constants
        G11 G12 G13 G14 - grid
        G21 G22 G23 G24 - grid
        G31 G32 G33 G34 - grid
        Tree Wood Fountain Factory Truck - others
        Beaver Racoon - animal
        N0 N1 N2 N3 - constant
        
    )
    (:predicates
        (adjacent ?x - grid ?y - grid)
        (on ?x - object ?y - grid)  ; the object x is on the grid y
        (clean ?x - grid)
        (polluted ?x - grid)
        (succ ?x - constant ?y - constant)
        (budget ?x - constant)
        (acting ?x - object)
        (free ?x - grid)
    )

    (:action TruckMove
        :parameters (
            ?x - grid
            ?y - grid
        )
        :precondition (
            and 

                (adjacent ?x ?y)
                (on Truck ?x)
                (free ?y)
                (acting Truck)
                
        )
        :effect (
            and
                (not(on Truck ?x))
                (on Truck ?y)
                (not(clean ?y))
                (polluted ?y)
                (not(free ?y))
                (free ?x) 
        )
    )
    (:action arrive
        :parameters (
            ?x - grid
        )
        :precondition (
            and
                (on Truck G34)
                (on Factory G34) 
                (acting Truck)
        )
        :effect (
            and 
                (not(acting Truck))
                (acting Beaver)
        )

    )
    
    (:action clean
        :parameters (
            ?x - grid
            ?y - constant 
            ?z - constant
        )
        :precondition (
            and 
                (polluted ?x)
                (on Truck ?x)
                (budget ?y)
                (succ ?z ?y)
                (acting Truck)
        )
        :effect (
            and 
                (not(polluted ?x))
                (clean ?x)
                (not(budget ?y))
                (budget ?z)
        )
    )
    (:action AnimalMove
        :parameters (
            ?x - grid
            ?y - grid
            ?z - animal
        )
        :precondition (
            and 
                (adjacent ?x ?y)
                (on ?z ?x)
                (clean ?y)
                (acting Beaver)
        )
        :effect (
            and
                (not(on ?z ?x))
                (on ?z ?y)
        )
    )  
)