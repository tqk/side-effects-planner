(define (problem AnimalExample-p)

    (:domain AnimalExample-d)
    (:objects)

    (:init 
        (adjacent G22 G12) (adjacent G24 G14)
        (adjacent G32 G22) (adjacent G34 G24)
        (adjacent G11 G12) (adjacent G12 G13) (adjacent G13 G14)
        (adjacent G21 G22) (adjacent G22 G23) (adjacent G23 G24)
        (adjacent G31 G32) (adjacent G32 G33) 
        
        (adjacent G12 G22) (adjacent G14 G24)
        (adjacent G22 G32) (adjacent G24 G34)
        (adjacent G12 G11) (adjacent G13 G12) (adjacent G14 G13)
        (adjacent G22 G21) (adjacent G23 G22) (adjacent G24 G23)
        (adjacent G32 G31) (adjacent G33 G32) 
        

        (on Tree G11)   (on Fountain G13)
        (on Beaver G21) (on Racoon G23)
        (on Truck G31)  (on Wood G33)   (on Factory G34)
        (clean G11) (clean G12) (clean G13) (clean G14)
        (clean G21) (clean G22) (clean G23) (clean G24)
        (clean G32) (clean G33) (clean G34)
        (polluted G31)
        (free G11) (free G12) (free G13) (free G14)
        (free G22) (free G24)
        (free G32) (free G33) (free G34)
        (succ N0 N1) (succ N1 N2) (succ N2 N3)
        (budget N3)
        (acting Truck)
    )
    (:goal 
        (and 
            (on Truck G34)
            (on Racoon G13)
            (on Beaver G11)
            (on Factory G34)
        )
    )
)