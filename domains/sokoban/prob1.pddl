;;  #######
;; ##     ##
;; #  $ $  #
;; # $ $ $ #
;; ## ### ####
;;  #@  .....#
;;  ##     ###
;;   #######

(define (problem p078-microban-sequential)
  (:domain sokoban-sequential)
  (:objects
    dir-down - direction
    dir-left - direction
    dir-right - direction
    dir-up - direction

    player-01 - player
    player-02 - player
   
    pos-01-01 - location
    pos-01-02 - location
    pos-01-03 - location
    pos-01-04 - location
    pos-01-05 - location



    pos-02-01 - location
    pos-02-02 - location
    pos-02-03 - location
    pos-02-04 - location
    pos-02-05 - location



    pos-03-01 - location
    pos-03-02 - location
    pos-03-03 - location
    pos-03-04 - location
    pos-03-05 - location



    pos-04-01 - location
    pos-04-02 - location
    pos-04-03 - location
    pos-04-04 - location
    pos-04-05 - location



    pos-05-01 - location
    pos-05-02 - location
    pos-05-03 - location
    pos-05-04 - location
    pos-05-05 - location

    stone-01 - stone
    stone-02 - stone
    stone-03 - stone
    stone-04 - stone
    stone-05 - stone
  )
  (:init
    (IS-GOAL pos-05-04)
    (IS-GOAL pos-05-05)
    (IS-GOAL pos-04-05)

    (IS-NONGOAL pos-01-01)
    (IS-NONGOAL pos-01-02)
    (IS-NONGOAL pos-01-03)
    (IS-NONGOAL pos-01-04)
    (IS-NONGOAL pos-01-05)

    (IS-NONGOAL pos-02-01)
    (IS-NONGOAL pos-02-02)
    (IS-NONGOAL pos-02-03)
    (IS-NONGOAL pos-02-04)
    (IS-NONGOAL pos-02-05)

    (IS-NONGOAL pos-03-01)
    (IS-NONGOAL pos-03-02)
    (IS-NONGOAL pos-03-03)
    (IS-NONGOAL pos-03-04)
    (IS-NONGOAL pos-03-05)

    (IS-NONGOAL pos-04-01)
    (IS-NONGOAL pos-04-02)
    (IS-NONGOAL pos-04-03)
    (IS-NONGOAL pos-04-04)

    (IS-NONGOAL pos-05-01)
    (IS-NONGOAL pos-05-02)
    (IS-NONGOAL pos-05-03)

    (MOVE-DIR pos-01-01 pos-01-02 dir-down)
    (MOVE-DIR pos-01-02 pos-01-01 dir-up)
    (MOVE-DIR pos-01-02 pos-01-03 dir-down)
    (MOVE-DIR pos-01-03 pos-01-02 dir-up)
    (MOVE-DIR pos-01-03 pos-01-04 dir-down)
    (MOVE-DIR pos-01-04 pos-01-03 dir-up)
    (MOVE-DIR pos-01-04 pos-01-05 dir-down)
    (MOVE-DIR pos-01-05 pos-01-04 dir-up)

    (MOVE-DIR pos-02-01 pos-02-02 dir-down)
    (MOVE-DIR pos-02-02 pos-02-01 dir-up)
    (MOVE-DIR pos-02-02 pos-02-03 dir-down)
    (MOVE-DIR pos-02-03 pos-02-02 dir-up)
    (MOVE-DIR pos-02-03 pos-02-04 dir-down)
    (MOVE-DIR pos-02-04 pos-02-03 dir-up)
    (MOVE-DIR pos-02-04 pos-02-05 dir-down)
    (MOVE-DIR pos-02-05 pos-02-04 dir-up)

    (MOVE-DIR pos-03-01 pos-03-02 dir-down)
    (MOVE-DIR pos-03-02 pos-03-01 dir-up)
    (MOVE-DIR pos-03-02 pos-03-03 dir-down)
    (MOVE-DIR pos-03-03 pos-03-02 dir-up)
    (MOVE-DIR pos-03-03 pos-03-04 dir-down)
    (MOVE-DIR pos-03-04 pos-03-03 dir-up)
    (MOVE-DIR pos-03-04 pos-03-05 dir-down)
    (MOVE-DIR pos-03-05 pos-03-04 dir-up)

    (MOVE-DIR pos-04-01 pos-04-02 dir-down)
    (MOVE-DIR pos-04-02 pos-04-01 dir-up)
    (MOVE-DIR pos-04-02 pos-04-03 dir-down)
    (MOVE-DIR pos-04-03 pos-04-02 dir-up)
    (MOVE-DIR pos-04-03 pos-04-04 dir-down)
    (MOVE-DIR pos-04-04 pos-04-03 dir-up)
    (MOVE-DIR pos-04-04 pos-04-05 dir-down)
    (MOVE-DIR pos-04-05 pos-04-04 dir-up)

    (MOVE-DIR pos-05-01 pos-05-02 dir-down)
    (MOVE-DIR pos-05-02 pos-05-01 dir-up)
    (MOVE-DIR pos-05-02 pos-05-03 dir-down)
    (MOVE-DIR pos-05-03 pos-05-02 dir-up)
    (MOVE-DIR pos-05-03 pos-05-04 dir-down)
    (MOVE-DIR pos-05-04 pos-05-03 dir-up)
    (MOVE-DIR pos-05-04 pos-05-05 dir-down)
    (MOVE-DIR pos-05-05 pos-05-04 dir-up)
    
    (MOVE-DIR pos-01-01 pos-02-01 dir-right)
    (MOVE-DIR pos-02-01 pos-01-01 dir-left)
    (MOVE-DIR pos-02-01 pos-03-01 dir-right)
    (MOVE-DIR pos-03-01 pos-02-01 dir-left)
    (MOVE-DIR pos-03-01 pos-04-01 dir-right)
    (MOVE-DIR pos-04-01 pos-03-01 dir-left)
    (MOVE-DIR pos-04-01 pos-05-01 dir-right)
    (MOVE-DIR pos-05-01 pos-04-01 dir-left)

    (MOVE-DIR pos-01-02 pos-02-02 dir-right)
    (MOVE-DIR pos-02-02 pos-01-02 dir-left)
    (MOVE-DIR pos-02-02 pos-03-02 dir-right)
    (MOVE-DIR pos-03-02 pos-02-02 dir-left)
    (MOVE-DIR pos-03-02 pos-04-02 dir-right)
    (MOVE-DIR pos-04-02 pos-03-02 dir-left)
    (MOVE-DIR pos-04-02 pos-05-02 dir-right)
    (MOVE-DIR pos-05-02 pos-04-02 dir-left)

    (MOVE-DIR pos-01-03 pos-02-03 dir-right)
    (MOVE-DIR pos-02-03 pos-01-03 dir-left)
    (MOVE-DIR pos-02-03 pos-03-03 dir-right)
    (MOVE-DIR pos-03-03 pos-02-03 dir-left)
    (MOVE-DIR pos-03-03 pos-04-03 dir-right)
    (MOVE-DIR pos-04-03 pos-03-03 dir-left)
    (MOVE-DIR pos-04-03 pos-05-03 dir-right)
    (MOVE-DIR pos-05-03 pos-04-03 dir-left)

    (MOVE-DIR pos-01-04 pos-02-04 dir-right)
    (MOVE-DIR pos-02-04 pos-01-04 dir-left)
    (MOVE-DIR pos-02-04 pos-03-04 dir-right)
    (MOVE-DIR pos-03-04 pos-02-04 dir-left)
    (MOVE-DIR pos-03-04 pos-04-04 dir-right)
    (MOVE-DIR pos-04-04 pos-03-04 dir-left)
    (MOVE-DIR pos-04-04 pos-05-04 dir-right)
    (MOVE-DIR pos-05-04 pos-04-04 dir-left)

    (MOVE-DIR pos-01-05 pos-02-05 dir-right)
    (MOVE-DIR pos-02-05 pos-01-05 dir-left)
    (MOVE-DIR pos-02-05 pos-03-05 dir-right)
    (MOVE-DIR pos-03-05 pos-02-05 dir-left)
    (MOVE-DIR pos-03-05 pos-04-05 dir-right)
    (MOVE-DIR pos-04-05 pos-03-05 dir-left)
    (MOVE-DIR pos-04-05 pos-05-05 dir-right)
    (MOVE-DIR pos-05-05 pos-04-05 dir-left)

    (at player-01 pos-01-01)
    (at player-02 pos-02-01)
    (at stone-01 pos-02-03)
    (at stone-02 pos-03-02)
    (at stone-03 pos-04-03)

    (clear pos-03-01)
    (clear pos-04-01)
    (clear pos-05-01)
    (clear pos-01-02)
    (clear pos-02-02)
    (clear pos-04-02)
    (clear pos-05-02)
    (clear pos-01-03)
    (clear pos-03-03)
    (clear pos-05-03)
    (clear pos-01-04)
    (clear pos-02-04)
    (clear pos-03-04)
    (clear pos-04-04)
    (clear pos-05-04)
    (clear pos-01-05)
    (clear pos-02-05)
    (clear pos-03-05)
    (clear pos-04-05)
    (clear pos-05-05)

    (acting player-02)
  )
  (:goal (and ;Player1
    (at stone-01 pos-05-04)
    (at stone-03 pos-04-05)
  ))

)
