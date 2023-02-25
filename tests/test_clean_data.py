import unittest

from collections import OrderedDict

from ..clean_data import clean_address, clean_date, clean_bird
from ..constants import CONVENTION_CTR, MLK, UNKNOWN_DATE, THURGOOD, DOE, GU


class TestCleanData(unittest.TestCase):
    def test_clean_address(self):
        self.assertEqual("1530 Newton St NE", clean_address("1530 Newton St NE, Washington, DC 20017"))
        self.assertEqual("14th St and I St NW", clean_address("14th St NW & I St NW, Washington, DC 20005"))

    def test_clean_address_pre_clean_repl(self):
        self.assertEqual("430 E St NW", clean_address("Glass entry, 430 E St., NW"))
        self.assertEqual("430 E St NW", clean_address("glass entry, 430 E St NW, WDC"))
        self.assertEqual(THURGOOD, clean_address("Thurgood Marshall Building"))
        self.assertEqual("2 Lincoln Memorial Circle NW", clean_address("Lincoln Memorial, Washington, DC"))
        self.assertEqual("850 10th St NW", clean_address("850 10th St NW at the corner with Palmer Alley NW"))
        self.assertEqual("920 Massachusetts Ave NW", clean_address("920 Mass. (N. side at glass passageway)"))
        self.assertEqual("1813 Wiltberger St NW", clean_address("Across from 1813 Wiltberger NW, WeWork Shaw Building"))

    def test_clean_address_other_repl(self):
        self.assertEqual(MLK, clean_address("MLK Library"))
        self.assertEqual("Some address Rd", clean_address("Some address Road"))
        self.assertEqual("111 Massachusetts Ave NW", clean_address("111 Mass Ave NW "))
        self.assertEqual("444 E St NW",
                         clean_address("444 E St NW (Nat'l Law Enforcement Museum; two smaller glass bldgs"))
        self.assertEqual(CONVENTION_CTR, clean_address("Convention Center (L St between 7th and 9th, glass walkway)"))
        self.assertEqual("100 Maryland Ave SW", clean_address("US Botanic Garden, Southern Exposure courtyard, north wall"))
        self.assertEqual("950-980 Maine Ave SW", clean_address("950 - 980 Maine SW, east side between buildings"))
        self.assertEqual(CONVENTION_CTR, clean_address("Convention Center (7th St), at Morris American Bar"))
        self.assertEqual(CONVENTION_CTR, clean_address("Convention Center (9th St between L and Mount Vernon Place)"))
        self.assertEqual("3001 Connecticut Ave NW", clean_address("The National Zoo"))
        self.assertEqual("99 New York Ave NE", clean_address("ATF Building, NY Avenue"))
        self.assertEqual("801 Mt Vernon Pl NW", clean_address("Convention Center                   (9th between K and L)"))
        self.assertEqual(CONVENTION_CTR, clean_address("Convention Center (9th Street between L and M NW), 9th Street close to L at glass rounding"))
        self.assertEqual("1805 7th St NW", clean_address("1805 7th st nw (uncf) south side"))
        self.assertEqual(CONVENTION_CTR, clean_address("Convention Center, SE corner at 7th and NY Avenue"))
        self.assertEqual("20th St and K St NW", clean_address("Eagle Bank, NW corner, 20th and K Sts. NW"))
        self.assertEqual(THURGOOD, clean_address("Thurgood Marshall Bldg, NW"))
        self.assertEqual("1 Dupont Circle NW", clean_address("1 Dupont Circle NW side"))
        self.assertEqual("100 F St NE", clean_address("SEC Building, 100 F Street NE"))
        self.assertEqual("1090 I St NW", clean_address("1090 I Street, NW  WDC 20268"))
        self.assertEqual("1st and E St NW", clean_address("First and E Streets, NW (NE side of intersection)"))
        self.assertEqual(MLK, clean_address("Martin Luther King Library         901 G Street, NW"))
        self.assertEqual(DOE, clean_address("DOE Building, 1000 Independence Ave SW, Washington, DC 20585"))
        self.assertEqual(GU, clean_address("Lauinger Library, Georgetown University"))
        self.assertEqual(GU, clean_address("Georgetown University Lauinger Library, 37th Street NW side"))

    def test_clean_date_doubles(self):
        self.assertEqual("2018-09-30", clean_date(OrderedDict({"date": "9-30--2018"})))
        self.assertEqual("2020-10-28", clean_date(OrderedDict({"date": "10//28/20"})))

    def test_clean_date_short(self):
        self.assertEqual("2022-01-01", clean_date(OrderedDict({"date": "1/1/22"})))

    def test_clean_date_long(self):
        self.assertEqual("2021-12-12", clean_date(OrderedDict({"Date": "12-12-2021"})))

    def test_malformatted_date(self):
        self.assertEqual(UNKNOWN_DATE, clean_date(OrderedDict({"date": "12/12"})))

    def test_clean_bird(self):
        self.assertEqual("Alder Flycatcher", clean_bird("Alder"))
        self.assertEqual("Alder Flycatcher", clean_bird("Alder Flycatcher"))
        self.assertEqual("Warbler Species", clean_bird("Warbler sp."))
        self.assertEqual("Warbler Species", clean_bird("Warbler sp"))
