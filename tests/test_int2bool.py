import unittest
import cpmpy as cp 
from cpmpy.expressions import *
from cpmpy.model import Model
from cpmpy.solvers.pysat import CPM_pysat
from cpmpy.transformations.to_bool import extract_boolvar, intvar_to_boolvar

class TestInt2Bool(unittest.TestCase):
    def setUp(self):
        self.iv = intvar(lb=2, ub=7,name="iv")
        self.bvs = boolvar(shape=5, name="bv")
        self.iv_vector = intvar(lb=2, ub=7, shape=5, name="iv_vec")
        self.iv_2dmatrix = intvar(lb=2, ub=4, shape=(5, 7), name="iv_2d")
        self.iv_3dmatrix = intvar(lb=2, ub=4, shape=(5, 6, 7), name="iv_3d")

    def test_boolmodel(self):
        boolmodel = Model(
            sum(self.bvs) > 4,
        )
        boolmodel2 = Model(
            sum(self.bvs) > 4,
        )

        ivarmap, new_model = boolmodel.int2bool_onehot()

        self.assertEqual(len(ivarmap), 0)
        # returns same model
        self.assertEqual(new_model, boolmodel)

        # ensuring model with same constraints are not equal
        # different refence to object
        self.assertNotEqual(boolmodel, boolmodel2)

    ## VARIABLES: intvar -> boolvar
    def test_intvar_to_boolvar(self):
        iv = intvar(0, 5, shape=1, name="x")
        ivarmap, constraints = intvar_to_boolvar(iv)
        self.assertEqual(len(ivarmap[iv]), iv.ub - iv.lb + 1)
        self.assertEqual(len(extract_boolvar(ivarmap)), iv.ub - iv.lb + 1)

    def test_boolvar_to_boolvar(self):
        bv = boolvar()
        ivarmap, constraints = intvar_to_boolvar(bv)
        self.assertEqual(ivarmap[bv], bv)
        self.assertEqual(len(constraints), 0)

    def test_intvar_arr_to_boolvar_array(self):
        iv = intvar(0, 5, shape=10, name="x")
        ivarmap, constraints = intvar_to_boolvar(iv)
        self.assertEqual(len(ivarmap), iv.shape[0])

        # handle more complex matrix data structures
        iv_matrix = intvar(0, 5, shape=(10, 10), name="x")
        ivarmap, constraints = intvar_to_boolvar(iv_matrix)

        self.assertEqual(len(ivarmap), iv_matrix.shape[0] * iv_matrix.shape[1])

        for varmap in ivarmap.values():
            self.assertEqual(len(varmap), iv_matrix[0, 0].ub - iv_matrix[0, 0].lb + 1)

    ## CONSTRAINTS:
    def test_equals_var(self):

        iv_model = Model(
            self.iv == 6
        )

        ivarmap, bool_model = iv_model.int2bool_onehot()

        # solve both models and checking for result
        bool_model.solve()
        iv_model.solve()

        # return same value
        self.assertEqual(extract_solution(ivarmap), set([(self.iv, self.iv.value())]))

    def test_equals_vector(self):

        iv_model = Model(
            self.iv_vector[0] == 2,
            self.iv_vector[1] == 3,
            self.iv_vector[2] == 4,
            self.iv_vector[3] == 3,
            self.iv_vector[4] == 2,
        )

        ivarmap, bool_model = iv_model.int2bool_onehot()
        iv_model.solve()
        bool_model.solve()

        for iv in self.iv_vector:
            self.assertTrue(ivarmap[iv][iv.value()])

        self.assertEqual(
            extract_solution(ivarmap),
            set((iv, iv.value()) for iv in self.iv_vector)
        )

    def test_equals_vector_assignment(self):

        iv_model = Model(
            self.iv_vector == [2, 3, 4, 3, 2]
        )
        ivarmap, bool_model = iv_model.int2bool_onehot()
        bool_model.solve()

        iv_model_sol = extract_solution(ivarmap)

        iv_model2 = Model(
            self.iv_vector[0] == 2,
            self.iv_vector[1] == 3,
            self.iv_vector[2] == 4,
            self.iv_vector[3] == 3,
            self.iv_vector[4] == 2,
        )

        ivarmap2, bool_model2 = iv_model2.int2bool_onehot()
        bool_model2.solve()
        iv_model2_sol = extract_solution(ivarmap)

        # both assignment should be valid
        self.assertEqual(iv_model_sol, iv_model2_sol)

    def test_different(self):
        iv_model = Model(
            self.iv != 2,
            self.iv != 3,
            self.iv != 4,
            self.iv != 5,
            self.iv != 6,
        )
        iv_model.solve()
        ivarmap, bool_model = iv_model.int2bool_onehot()
        bool_model.solve()
        self.assertEqual(extract_solution(ivarmap), set([(self.iv, self.iv.value())]))

    def test_comparison(self):
        iv_model = Model(
            self.iv > 5,
            self.iv < 7
        )
        iv_model.solve()
        ivarmap, bool_model = iv_model.int2bool_onehot()
        bool_model.solve()
        self.assertEqual(extract_solution(ivarmap), set([(self.iv, self.iv.value())]))

        iv_model2 = Model(
            self.iv >= 6,
            self.iv <= 6
        )
        iv_model2.solve()
        ivarmap2, bool_model2 = iv_model2.int2bool_onehot()
        bool_model2.solve()
        self.assertEqual(extract_solution(ivarmap2), set([(self.iv, self.iv.value())]))

    def test_comparison_edge_cases(self):
        iv_model = Model(
            self.iv < 10,
            self.iv > -1,
            self.iv >= 7
        )

        iv_model.solve()
        ivarmap, bool_model = iv_model.int2bool_onehot()
        bool_model.solve()
        self.assertEqual(extract_solution(ivarmap), set([(self.iv, self.iv.value())]))

def extract_solution(ivarmap):

    sol = set()
    for iv, value_dict in ivarmap.items():
        n_val_assigned = sum(1 if bv.value() else 0 for iv_val, bv in value_dict.items())
        assert n_val_assigned == 1, f"Expected: 1, Got: {n_val_assigned} value can be assigned!"
        for iv_val, bv in value_dict.items():
            if bv.value():
                sol.add((iv, iv_val))

    return sol

if __name__ == '__main__':
    unittest.main()

