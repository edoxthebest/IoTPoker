; topicexpression per id = (B/*)
; topicexpression per subscribe topic = (/A/?/topic${id})
; topicexpression per publish topic = (/?/C/topic${id})

(declare-const id1 String)
(declare-const id2 String)
(declare-const topic String)

(assert 
  (str.in.re
    id1
    (re.++
      (str.to.re "B/")
      re.allchar)))

(assert 
  (str.in.re
    id2
    (re.++
      (str.to.re "B/")
      re.allchar)))

(assert
  (str.in.re
    topic
    (re.++
      (str.to.re "/A/")
      re.allchar
      (str.to.re "/topic")
      (str.to.re id1))))

(assert
  (str.in.re
    topic
    (re.++
      (str.to.re "/")
      re.allchar
      (str.to.re "/C/topic")
      (str.to.re id2))))
(check-sat)
(get-model)

