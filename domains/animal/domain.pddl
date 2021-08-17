(define (domain AnimalExample-d)
    (:requirements :strips :typing )
    (:types
        animal 
        others
        grid
        constant 
    )
    (:constants
        ; 3x4 grids
        G11 G12 G13 G14 - grid
        G21 G22 G23 G24 - grid
        G31 G32 G33 G34 - grid
        Tree Wood Fountain Factory Truck - others
        Beaver Racoon - animal
        N0 N1 N2 N3 - constant ; constant is used to count the number of times, that truck can clean the polluted grid
        
    )
    (:predicates
        (adjacent ?x - grid ?y - grid) ; the grid x is adjacent to the grid y
        (on ?x - object ?y - grid)  ; the object x is on the grid y
        (clean ?x - grid) ; the grid x is currently clean, animals can step on it
        (polluted ?x - grid) ; the grid x is currently pollusted, animals can not step on it
        (succ ?x - constant ?y - constant); y = x + 1
        (budget ?x - constant) ; budget is used to keep track of the remaining cleaning times
        (acting ?x - object); acting shows which agent is executing
        (free ?x - grid) ; there is no items stand on the grid x
    )
    ; Truck moves from one grid to another, two grids have to be adjacent to each other
    ; Set the previous grid to be free, and remove the free fluent from the current grid.
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
    ; Truck arrives at a grid where the factory locates. Truck achieves its goal, 
    ; Truck stop executing, other agents can start to execute.
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
    ; Truck cleans up the current grid, two grids have to be adjacent to each other
    ; The grid has to be clean.
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
    ; Animal moves from one grid to another, both grids must be ajacent to each other and clean,
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