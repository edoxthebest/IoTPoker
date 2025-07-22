import cvc5.pythonic as cvc5

s = cvc5.Solver()
STAR = cvc5.Star(cvc5.Union(cvc5.Range('a', 'z'),
                            cvc5.Range('A', 'Z'),
                            cvc5.Range('0', '9'),
                            cvc5.Re('/'),
                            ))
topic = cvc5.String('topic')


s.add(cvc5.InRe(topic, cvc5.Concat(cvc5.Re('AB'), STAR)))
s.add(cvc5.InRe(topic, cvc5.Concat(cvc5.Re('ABCDEF'), STAR)))
s.add(cvc5.InRe(topic, cvc5.Concat(cvc5.Re(''), STAR)))


print(s.check())
print(s.model())