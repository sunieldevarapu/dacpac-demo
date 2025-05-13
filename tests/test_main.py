import unittest
from test_app.main import get_example

class TestMain(unittest.TestCase):
    def test_get_example(self):
        status_code = get_example()
        self.assertEqual(status_code, 200)

if __name__ == '__main__':
    unittest.main()
