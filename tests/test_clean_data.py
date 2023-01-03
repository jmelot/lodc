import unittest

from ..clean_data import clean_address


class TestCleanData(unittest.TestCase):
    def test_clean_address(self):
        self.assertEqual("1530 Newton St NE", clean_address("1530 Newton St NE, Washington, DC 20017"))
        self.assertEqual("14th St NW & I St NW", clean_address("14th St NW & I St NW, Washington, DC 20005"))
