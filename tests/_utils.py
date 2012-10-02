import os

import csp_solver

sugarjar_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 'sugar-v1-15-0.jar'))
csp_solver_config = csp_solver.get_valid_csp_solver_config(
    sugarjar_path=sugarjar_path
)

from smart_grid_simulation.simulation import NotSolvable


def assure_is_int(test_class_instance, value, expected_value):
    test_class_instance.failUnlessEqual(value, expected_value)
    test_class_instance.failUnlessEqual(type(value), int)


class AbstractInterface(object):
    def test_get_value(self):
        assure_is_int(self, self.a1.get_value(), 1)

    def test_get_value_range(self):
        self.failUnlessEqual(
            self.a1.get_value_range(),
            set([1,2,3])
        )

    def test_set_value_int(self):
        ret_val = self.a1.set_value(2)

        assert ret_val == 2

        assure_is_int(self, self.a1.get_value(), 2)

    def test_set_value_int_out_of_range(self):
        self.failUnlessRaises(
            NotSolvable,
            self.a1.set_value,
            0
        )

    def test_set_value_float(self):
        assert self.a1.get_value() == 1

        self.a1.set_value(2.1)

        assure_is_int(self, self.a1.get_value(), 2)

    def test_set_value_string(self):
        assert self.a1.get_value() == 1

        self.a1.set_value("2")

        assure_is_int(self, self.a1.get_value(), 2)

    def test_set_value_string_invalid(self):
        assert self.a1.get_value() == 1

        self.failUnlessRaises(
            NotSolvable,
            self.a1.set_value,
            "Zwei"
        )

        assure_is_int(self, self.a1.get_value(), 1)
