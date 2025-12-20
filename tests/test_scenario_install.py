import unittest
import sys

class TestScenarioInstall(unittest.TestCase):
    def test_colorama_installed(self):
        try:
            import colorama
            self.assertTrue(True, "colorama should be importable")
        except ImportError:
            self.fail("colorama is missing. Expecting Nova to install it.")

if __name__ == '__main__':
    unittest.main()
