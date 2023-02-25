import unittest

from collections import OrderedDict

from ..clean_data import clean_address, clean_date
from ..constants import MLK, UNKNOWN_DATE, THURGOOD


class TestCleanData(unittest.TestCase):
    def test_clean_address(self):
        self.assertEqual("1530 Newton St NE", clean_address("1530 Newton St NE, Washington, DC 20017"))
        self.assertEqual("14th St and I St NW", clean_address("14th St NW & I St NW, Washington, DC 20005"))

    def test_clean_address_pre_clean_repl(self):
        self.assertEqual("430 E St NW", clean_address("Glass entry, 430 E St., NW"))
        self.assertEqual("430 E St NW", clean_address("glass entry, 430 E St NW, WDC"))
        self.assertEqual(THURGOOD, clean_address("Thurgood Marshall Building"))

    def test_clean_address_other_repl(self):
        self.assertEqual(MLK, clean_address("MLK Library"))
        self.assertEqual("Some address Rd", clean_address("Some address Road"))
        self.assertEqual("111 Mass Ave NW ", "111 Massachusetts Ave NW")

    def test_clean_date_doubles(self):
        self.assertEqual("2018-09-30", clean_date(OrderedDict({"date": "9-30--2018"})))
        self.assertEqual("2020-10-28", clean_date(OrderedDict({"date": "10//28/20"})))

    def test_clean_date_short(self):
        self.assertEqual("2022-01-01", clean_date(OrderedDict({"date": "1/1/22"})))

    def test_clean_date_long(self):
        self.assertEqual("2021-12-12", clean_date(OrderedDict({"Date": "12-12-2021"})))

    def test_malformatted_date(self):
        self.assertEqual(UNKNOWN_DATE, clean_date(OrderedDict({"date": "12/12"})))
