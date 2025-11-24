from collections import defaultdict

#### test expressions
sample1 = "(A & B) & (F | E)"
sample2 = "(A & (B | C)) & (F | E)"
sample3 = "FAKE"
sample4 = "(((A & B) & (C & D)) | 5)"
sample5 = "(A & (B | C)) & (F | E)"

sample6 = "!(A & B) | (C | (D & E))"

sample7 = "!A & B"
sample8 = "!(A & B)"
sample9 = "!(A & B) & !C"

sample10 = "!(A & B) | !(C & D)"

sample11 = "(A | B | C) & (!A | D | E) & (F | G | H)"

sample12 = "(D & !E) | (E & !F)"

#### below variables are used to test sample 6 truth output for ExprTree
sample6__truthtable1 = defaultdict(list)
sample6__truthtable1["B"] = False
sample6__truthtable1["C"] = False
sample6__truthtable1["D"] = True
sample6__truthtable1["E"] = True

sample6__truthtable1_output = {}
sample6__truthtable1_output[" A  &  B  ! "] = [] # undet
sample6__truthtable1_output[" C "] = False
sample6__truthtable1_output[" D  &  E "] = True

##### decisions: satisfiability
sample_sat1 = "!(A & !B) & C & !D & !(E & F & G) & !H"
sample_sat2 = "!(A & B & !C) & !(D & E) & (G & !H)"

##### syntactical test
syntact1 = "A & B & C & !A"
nonsyntact2 = "A & B & | C"

truthtable1 = defaultdict(list)
truthtable1["A"] = True
truthtable1["B"] = False
truthtable1["C"] = True
