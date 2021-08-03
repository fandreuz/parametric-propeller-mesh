from src.steroid_dict import SteroidDict

def test_normal_dict():
    dc = SteroidDict()
    dc['a'] = 2
    dc['b'] = 3

    assert dc['a'] == 2
    assert dc['b'] == 3

def test_update():
    dc = SteroidDict({'a':2,'b':9})
    assert dc['a'] == 2
    assert dc['b'] == 9

def test_computed_dict():
    dc = SteroidDict()
    dc['a'] = 2
    dc['b'] = 3

    dc['cmp'] = lambda dc: dc['a']*2
    assert dc['cmp'] == 4

    dc['cmp2'] = lambda dc: dc['a']+dc['b']
    assert dc['cmp2'] == 5

    # should not commute
    dc['cmp3'] = lambda dc: dc['a']-dc['b']
    assert dc['cmp3'] == -1
    dc['cmp4'] = lambda dc: dc['b']-dc['a']
    assert dc['cmp4'] == 1

def test_template():
    dc = SteroidDict()
    dc['a'] = 2
    dc['b'] = 3

    tmp = 'a is @a, and b is @b, and also a is @a'
    dc.set_computable_template('tmp', tmp, repetable=False)

    assert dc['tmp'] == 'a is 2, and b is 3, and also a is 2'

def test_repetable_template():
    dc = SteroidDict()
    dc['a'] = [1,2,3,4]
    dc['b'] = [5,6,7,8]

    tmp = 'a is @a, and b is @b'
    dc.set_computable_template('tmp', tmp, repetable=True)

    assert dc['tmp'] == """a is 1, and b is 5
a is 2, and b is 6
a is 3, and b is 7
a is 4, and b is 8"""

def test_repetable_template_uneven_number():
    dc = SteroidDict()
    dc['a'] = [1,2,3]
    dc['b'] = [5,6,7,8]

    tmp = 'a is @a, and b is @b'
    dc.set_computable_template('tmp', tmp, repetable=True)

    assert dc['tmp'] == """a is 1, and b is 5
a is 2, and b is 6
a is 3, and b is 7"""

def test_repetable_template_uneven_number2():
    dc = SteroidDict()
    dc['a'] = 1
    dc['b'] = [5,6,7,8]

    tmp = 'a is @a, and b is @b'
    dc.set_computable_template('tmp', tmp, repetable=True)

    assert dc['tmp'] == """a is 1, and b is 5
a is 1, and b is 6
a is 1, and b is 7
a is 1, and b is 8"""

def test_repetable_template_nolists():
    dc = SteroidDict()
    dc['a'] = 1
    dc['b'] = 2

    tmp = 'a is @a, and b is @b'
    dc.set_computable_template('tmp', tmp, repetable=True)

    assert dc['tmp'] == """a is 1, and b is 2"""

def test_keys():
    dc = SteroidDict()
    dc['a'] = [1,2,3]
    dc['b'] = [5,6,7,8]

    tmp = 'a is @a, and b is @b'
    dc.set_computable_template('tmp', tmp, repetable=True)

    assert set(dc.keys()) == set(['a','b','tmp'])

def test_values():
    dc = SteroidDict()
    dc['a'] = 1
    dc['b'] = 2

    tmp = 'a is @a, and b is @b'
    dc.set_computable_template('tmp', tmp, repetable=True)

    assert set(dc.values()) == set([1,2,'a is 1, and b is 2'])
