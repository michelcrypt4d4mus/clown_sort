from clown_sort.util.string_helper import strip_bad_chars


def test_strip_bad_chars():
    assert(strip_bad_chars('$food = truth!') == '$food = truth_')
    assert(strip_bad_chars('who - knew') == 'who - knew')
