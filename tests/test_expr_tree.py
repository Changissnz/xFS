from .expr_tree_samples import *
from graph_models.expr_tree import * 
import unittest 


"""
python -m tests.test_expr_tree
"""
class ExprTreeClass(unittest.TestCase):

    """
    tests method on lone sample q
    """
    def test__ExprTree__find_inner_chunk(self):

        q = "((A & (B | C)) & (F | E)"
        et = ExprTree(q)

        index = et.find_inner_chunk()
        assert q[index[0]:index[1] + 1] == "(B | C)"

    def test__ExprTree__find_outer_chunk(self):

        start,end = ExprTree.find_outer_chunk(sample1)
        assert sample1[start:end+1] == "(A & B)"

        start,end = ExprTree.find_outer_chunk(sample2)
        assert sample2[start:end+1] == "(A & (B | C))"

        start,end = ExprTree.find_outer_chunk(sample4)
        assert sample4[start:end+1] == "(((A & B) & (C & D)) | 5)"

        start,end = ExprTree.find_outer_chunk(sample5)
        assert sample5[start:end+1] == "(A & (B | C))"

    def test__ExprTree_parse(self):

        et = ExprTree(sample4)
        x = et.parse()
        y = ExprTree.inorder_traversal_display(x)
        assert y == " A  &  B  &  C  &  D  |  5 "

        et = ExprTree(sample5)
        x = et.parse()
        y = ExprTree.inorder_traversal_display(x)
        assert y == " A  &  B  |  C  &  F  |  E "


    """
    performs further testing of NOT operand
    """
    def test__ExprTree_parse__notop(self):

        et = ExprTree(sample6)
        x = et.parse()
        y = ExprTree.inorder_traversal_display(x)
        assert y == " A  &  B  !  |  C  |  D  &  E "

        et = ExprTree(sample7)
        x = et.parse()
        y = ExprTree.inorder_traversal_display(x)
        assert y == " A  !  &  B "

        et = ExprTree(sample8)
        x = et.parse()
        y = ExprTree.inorder_traversal_display(x)
        assert y == " A  &  B  ! "

        et = ExprTree(sample9)
        x = et.parse()
        y = ExprTree.inorder_traversal_display(x)
        assert y == " A  &  B  !  &  C  ! "

    ####---------------------------------------------------------------------------------

    # TODO: add assertions to this method
    def test__ExprTree__random_decision_printtest(self):

        et = ExprTree(sample5)
        x = et.parse()

        print("** target tree:\t", ExprTree.inorder_traversal_display(x))
        rd = et.random_decision()
        print("** random decision:\t", rd)

    def test__ExprTree__inorder_traversal_finder(self):

        et = ExprTree(sample12)
        et.process()
        assert len(et.possibleDecisions) == 2, "invalid {}, want {}".format(len(et.possibleDecisions), 4)

        et = ExprTree(sample6)
        et.process()
        assert len(et.possibleDecisions) == 3, "invalid {}, want {}".format(len(et.possibleDecisions), 3)

        answers = {"!(A & B)", "C", "D & E"}

        q = [ExprTree.traversal_display(x, "partial") for x in et.possibleDecisions.values()]

        for q_ in q: assert q_ in answers


    def test__ExprTree__evaluate_decision_absolute_truth(self):

        # parse sample
        et = ExprTree(sample6)
        x = et.parse()

        # get possible decisions
        et.inorder_decision_finder()

        # iterate through decisions and
        for k, x in et.possibleDecisions.items():
            y = ExprTree.inorder_traversal_display(x)
            result = et.evaluate_decision_absolute_truth(x, sample6__truthtable1)
            assert result == sample6__truthtable1_output[y], "truth table {}: wrong for {}".format("1", y)

    def test__ExprTree__evaluate_decision_absolute_truth_test2(self):

        def evaluate_etree(e, truthTable):
            results = []
            for k, x in e.possibleDecisions.items():
                y = ExprTree.inorder_traversal_display(x)
                result = et.evaluate_decision_absolute_truth(x, truthtable1)
                results.append(result)
            return results

        et = ExprTree("A & !B & C")
        et.process()
        q = evaluate_etree(et, truthtable1)
        assert q == [True]
        ###
        et = ExprTree("!A & B & C")
        et.process()
        q = evaluate_etree(et, truthtable1)
        assert q == [False]

        et = ExprTree("!(A & B) & C")
        et.process()
        q = evaluate_etree(et, truthtable1)
        assert q == [True]

    def test__ExprTree__traversal_display_test(self):
        # test sample 6,7,8,9
        et = ExprTree(sample6)
        et.process()
        q = ExprTree.traversal_display(et.parsedEas, "partial")
        assert q == sample6, "want {}, got {}".format(sample6, q)

        et = ExprTree(sample7)
        et.process()
        q = ExprTree.traversal_display(et.parsedEas, "partial")
        assert q == sample7, "want {}, got {}".format(sample7, q)

        et = ExprTree(sample8)
        et.process()
        q = ExprTree.traversal_display(et.parsedEas, "partial")
        assert q == sample8, "want {}, got {}".format(sample8, q)

        et = ExprTree(sample9)
        et.process()
        q = ExprTree.traversal_display(et.parsedEas, "partial")
        assert q == sample9, "want {}, got {}".format(sample9, q)

    def test__ExprTree__get_binary_permutations_test(self):
        sequenceSize = 5
        sequenceElements = ["l", "r"]

        allSequences = ExprTree.get_binary_permutations(sequenceSize, sequenceElements)

        q = list(allSequences)
        assert len(q) == 2 ** 5, "number of sequences {} does not match {}".format(len(q), 2**5)

    """
    this method does not have assertions. Requires human manual check.
    """
    def test__ExprTree__decision_to_choice_printtest(self,verbose = False):

        e = ExprTree(sample_sat1)
        e.process()
        x = e.parsedEas
        q = ExprTree.decision_to_choice(x)
        if verbose:
            print("SAMPLE1")
            print(ExprTree.traversal_display(q))

        e = ExprTree(sample_sat2)
        e.process()
        x = e.parsedEas
        q = ExprTree.decision_to_choice(x)
        if verbose:
            print("SAMPLE2")
            print(ExprTree.traversal_display(q))

        return

    def test__ExprTree__choice_tree_to_options(self):

        # create the choice tree
        e = ExprTree(sample_sat2)
        e.process()
        x = e.parsedEas

        q = ExprTree.decision_to_choice(x)
        q2 = ExprTree.choice_tree_to_options(q)
        assert len(q2) == 6, "invalid number of options, want {}, got {}".format(6, len(q2))

    def test__ExprTree__make_copy_at_or_test(self):

        e = ExprTree(sample6)
        e.process()
        q1, q2 = ExprTree.make_copy_at_or(e.parsedEas)
        q1_ = ExprTree.traversal_display(q1, "partial")
        q2_ = ExprTree.traversal_display(q2, "partial")
        assert q1_ == "!(A & B)"
        assert q2_ == "C | (D & E)"

        e = ExprTree(sample1)
        e.process()
        q = e.find_all_matching_nodes("|", 1)
        n = e.locate_node_by_index(q[0])
        q1, q2 = ExprTree.make_copy_at_or(n)
        q1 = ExprTree.rewind_to_root_(q1)
        q2 = ExprTree.rewind_to_root_(q2)
        q1_ = ExprTree.traversal_display(q1, "partial")
        q2_ = ExprTree.traversal_display(q2, "partial")
        assert q1_ == "(A & B) & F"
        assert q2_ == "(A & B) & E"

    def test__ExprTree___is_syntactical_test(self):
        e = ExprTree(syntact1)
        e.process()
        assert e.parsedEas != False

        e = ExprTree(nonsyntact2)
        e.process()
        assert e.parsedEas == False

        e = ExprTree("&")
        e.process()
        assert e.parsedEas == False

if __name__ == "__main__":
    unittest.main()