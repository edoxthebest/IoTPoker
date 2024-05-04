; topicexpression per id = (B/*)
; topicexpression per subscribe topic = (/A/topic${id})

(declare-const id1 String)
(declare-const topic1 String)
(declare-const topic2 String)

(declare-const id1Re (RegEx String))

(declare-const id1Re (RegEx (RegEx String)))

(assert 
  (=
    id1Re
    (re.++
       (ite (= (str.at id1 0) "+")
         re.allchar
         (str.to.re (str.at id1 0))
       )
       (ite (= (str.at id1 1) "+")
         re.allchar
         (str.to.re (str.at id1 1))
       )
       (ite (= (str.at id1 2) "+")
         re.allchar
         (str.to.re (str.at id1 2))
       )
       (ite (= (str.at id1 3) "+")
         re.allchar
         (str.to.re (str.at id1 3))
       )
       (ite (= (str.at id1 4) "+")
         re.allchar
         (str.to.re (str.at id1 4))
       )
  )
))



(assert 
  (str.in.re
    id1
    (re.++
      (str.to.re "B/")
      re.allchar)))

(assert
  (str.in.re
    topic1
    (re.++
      (str.to.re "/A")
      (str.to.re "/topic")
      id1Re)))

(assert
  (str.in.re
    topic2
    (re.++
      (str.to.re "/A")
      (str.to.re "/topic")
      id1Re)))

(assert
  (not 
     (= topic1 topic2)))

(check-sat)
(get-model)

