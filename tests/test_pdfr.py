import os

import pyexcel as p
from nose.tools import eq_


def test_simple_pdf():
    book = p.get_book(file_name=get_fixtures("simple.pdf"))
    eq_(book.number_of_sheets(), 1)
    eq_(book[0].name, "Table 1 of 1 on page 1 of 1")


def test_complex_pdf():
    book = p.get_book(file_name=get_fixtures("CBP-7857.pdf"))
    peer_look = [
        u"16 Higher education",
        u"stude",
        u"nt",
        u"numb",
        u"ers",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
    ]
    eq_(book.number_of_sheets(), 5)
    eq_(book.Table_1_of_1_on_page_16_of_17.row[0], peer_look)


def get_fixtures(file_name):
    return os.path.join("tests", "fixtures", file_name)
