import pytest

from pandamonium.util import BijectiveMap


def test_creation():
    BijectiveMap()


def test_erroneous_get():
    bmap = BijectiveMap()
    with pytest.raises(KeyError):
        bmap['foo']
    with pytest.raises(KeyError):
        bmap.get('foo')
    with pytest.raises(KeyError):
        bmap.getreverse('foo')


def test_get():
    bmap = BijectiveMap()
    bmap['foo'] = 'bar'
    assert bmap['foo'] == 'bar'
    assert bmap.get('foo') == 'bar'
    assert bmap.getreverse('bar') == 'foo'


def test_del():
    bmap = BijectiveMap()
    bmap['foo'] = 'bar'
    del bmap['foo']
    with pytest.raises(KeyError):
        bmap['foo']
