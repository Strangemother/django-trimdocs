from django.test import TestCase

class ExampleTestCase(TestCase):
    def setUp(self):
        pass 

    def test_example(self):
        self.assertEqual(1 + 1, 2)
        