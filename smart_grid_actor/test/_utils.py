from smart_grid_actor.actor import NotSolvable


def assure_is_int(test_class_instance, value, expected_value):
    test_class_instance.failUnlessEqual(value, expected_value)
    test_class_instance.failUnlessEqual(type(value), int)


class AbstractInterface(object):
    #a1 = None
    #assertEqual = None
    #assertRaises = None

    def test_get_value(self):
        assure_is_int(self, self.a1.get_value(), 1)

    def test_get_value_range(self):
        self.assertEqual(
            self.a1.get_value_range(),
            set([1, 2, 3])
        )

    def test_set_value_int(self):
        ret_val = self.a1.set_value(2)

        assert ret_val == 2

        assure_is_int(self, self.a1.get_value(), 2)

    def test_set_value_int_out_of_range(self):
        with self.assertRaises(NotSolvable):
            self.a1.set_value(0)

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

        with self.assertRaises(NotSolvable):
            self.a1.set_value("Zwei")

        assure_is_int(self, self.a1.get_value(), 1)
