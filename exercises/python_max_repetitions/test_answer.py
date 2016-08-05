import pytest
import answer


@pytest.mark.parametrize('string, char, count', [
    ("", None, 0),
    ("foo", "o", 2),
    ("d,fdfgmdfibmfidfvk,ofl,we34$dvdsvdfffffffffffffffdlf,dfl,dfl,dsfdd", "f", 15),
])
def test_answer_correct(string, char, count):
    assert answer.get_max_repetitions(string) == (char, count)
