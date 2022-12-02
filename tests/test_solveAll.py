import unittest

import cpmpy as cp

class TestSolveAll(unittest.TestCase):


    def test_solveall_no_obj(self):

        a,b = cp.boolvar(shape=2)
        m = cp.Model(a | b)

        for name, solver in cp.SolverLookup.base_solvers():
            if not solver.supported():
                continue

            solver = cp.SolverLookup.get(name,model=m)
            self.assertEqual(3, solver.solveAll(solution_limit=1000))


    def test_solveall_with_obj(self):

        x = cp.intvar(0, 3, shape=3)
        m = cp.Model(minimize=cp.sum(x))

        for name, solver in cp.SolverLookup.base_solvers():
            if not solver.supported():
                continue

            try:
                solver = cp.SolverLookup.get(name, model=m)
                self.assertEqual(1, solver.solveAll(solution_limit=1000))
            except (Exception, NotImplementedError):
                pass # solver does not support finding all optimal solutions
