import pytest

from pandamonium.util import AssociativeTable


def test_creation():
    a_table = AssociativeTable()
    a_table = AssociativeTable('foo', 'bar', 'baz')
    assert hasattr(a_table, 'foo')
    assert hasattr(a_table, 'bar')
    assert hasattr(a_table, 'baz')
    assert a_table._column['foo'] is a_table.foo
    assert a_table._column['bar'] is a_table.bar
    assert a_table._column['baz'] is a_table.baz
    # TODO: Assert absense of other attributes that don't start with _?


def test_presence():
    element = 'a'
    a_table = AssociativeTable('foo')
    assert element not in a_table
    a_table.foo.add(element)
    assert element in a_table
    assert element in a_table.foo


def test_get():
    element = 'foo'
    a_table = AssociativeTable('foo')
    with pytest.raises(KeyError):
        a_table[element]
    with pytest.raises(KeyError):
        a_table.get(element)
    with pytest.raises(KeyError):
        a_table.foo[element]
    with pytest.raises(KeyError):
        a_table.foo.get(element)
    a_table.foo.add(element)
    assert a_table[element] == set()
    assert a_table.foo[element] == set()


def test_delete_simple():
    element = 'a'
    a_table = AssociativeTable('foo')
    with pytest.raises(KeyError):
        del a_table[element]
    a_table.foo.add(element)
    del a_table[element]
    assert element not in a_table


def test_delete_complex():
    element_a = 'a'
    element_b = 'b'
    a_table = AssociativeTable('foo', 'bar')
    a_table.foo.add(element_a)
    a_table.bar.add(element_b)
    a_table._assoc(element_a, element_b)
    del a_table[element_b]
    assert a_table[element_a] == set()


def test_unique_elements():
    element = 'a'
    a_table = AssociativeTable('foo', 'bar')
    a_table.foo.add(element)
    with pytest.raises(ValueError):
        a_table.bar.add(element)


def test_association():
    elem_aa = 'aa'
    elem_ab = 'ab'
    elem_ba = 'ba'
    elem_bb = 'bb'
    a_table = AssociativeTable('foo', 'bar')
    a_table.foo.add(elem_aa)
    a_table.foo.add(elem_ab)
    a_table.bar.add(elem_ba)
    a_table.bar.add(elem_bb)
    a_table._assoc(elem_aa, elem_ba)
    a_table._assoc(elem_ab, elem_bb)
    assert a_table[elem_aa] == set([elem_ba])
    assert a_table[elem_bb] == set([elem_ab])
    assert a_table.get(elem_aa, elem_ab) == set([elem_ba, elem_bb])


def test_dissociation():
    elem_a = 'a'
    elem_b = 'b'
    a_table = AssociativeTable('foo', 'bar')
    a_table.foo.add(elem_a)
    a_table.foo.add(elem_b)
    a_table._assoc(elem_a, elem_b)
    a_table._dissoc(elem_a, elem_b)
    assert a_table[elem_a] == set()
    assert a_table[elem_b] == set()


def test_association_with_filter():
    elem_a = 'a'
    elem_b = 'b'
    elem_c = 'c'
    a_table = AssociativeTable('foo', 'bar', 'baz')
    a_table.foo.add(elem_a)
    a_table.bar.add(elem_b)
    a_table.baz.add(elem_c)
    a_table._assoc(elem_a, elem_b)
    a_table._assoc(elem_b, elem_c)
    assert a_table[elem_b] == set([elem_a, elem_c])
    assert a_table.get(elem_b, tables=(a_table.foo, )) == set(elem_a)
    assert a_table.get(elem_b, tables=(a_table.baz, )) == set(elem_c)
    assert a_table.get(elem_b, tables=(a_table.foo, a_table.baz)) == \
        set([elem_a, elem_c])


def test_path():
    elem_a = 'a'
    elem_b = 'b'
    elem_c = 'c'
    a_table = AssociativeTable('foo', 'bar', 'baz')
    a_table.foo.add(elem_a)
    a_table.bar.add(elem_b)
    a_table.baz.add(elem_c)
    a_table._assoc(elem_a, elem_b)
    a_table._assoc(elem_b, elem_c)
    assert a_table.get(elem_a, path=(a_table.bar, a_table.baz)) == set(elem_c)
