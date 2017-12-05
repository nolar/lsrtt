import collections

from lsrtt.db._chunks import ichunk


def test_ichunk_is_iterable():
    chunks = ichunk([], 10)
    assert isinstance(chunks, collections.Iterable)
    assert not isinstance(chunks, collections.Container)
    assert not isinstance(chunks, (list, tuple))


def test_ichunk_accepts_iterable_src():
    gen = (i for i in range(15))
    chunks = list(ichunk(gen, 10))
    assert len(chunks) == 2
    assert len(chunks[0]) == 10
    assert len(chunks[1]) == 5
    assert chunks[1] == [10, 11, 12, 13, 14]


def test_ichunk_precisely_sized_src():
    longlist = [i for i in range(100)]
    chunks = list(ichunk(longlist, 10))
    assert len(chunks) == 10
    assert len(chunks[0]) == 10
    assert len(chunks[-1]) == 10
    assert chunks[0] == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert chunks[-1] == [90, 91, 92, 93, 94, 95, 96, 97, 98, 99]


def test_ichunk_small_src():
    longlist = [i for i in range(5)]
    chunks = list(ichunk(longlist, 10))
    assert len(chunks) == 1
    assert chunks[0] == [0, 1, 2, 3, 4]


def test_ichunk_partial_src_gives_partial_end_chunk():
    longlist = [i for i in range(25)]
    chunks = list(ichunk(longlist, 10))
    assert len(chunks) == 3
    assert chunks[0] == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert chunks[1] == [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
    assert chunks[2] == [20, 21, 22, 23, 24]


def test_ichunk_empty_src_gives_no_chunks_at_all():
    chunks = list(ichunk([], 10))
    assert len(chunks) == 0
