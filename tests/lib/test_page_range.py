import pytest

from clown_sort.lib.page_range import PageRange


def test_page_range_for_one_page():
    p = PageRange('5')
    assert p.first_page == 5
    assert p.last_page == 6


def test_page_range_for_range():
    p = PageRange('5-10')
    assert p.first_page == 5
    assert p.last_page == 10


def test_invalid_range():
    with pytest.raises(ValueError):
        p = PageRange('10-5')


def test_str():
    assert str(PageRange('5-10')) == 'PageRange(5, 10)'
