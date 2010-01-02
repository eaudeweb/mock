# Copyright (C) 2007-20010 Michael Foord
# E-mail: fuzzyman AT voidspace DOT org DOT uk
# http://www.voidspace.org.uk/python/mock/
from __future__ import with_statement

import os
import sys
import unittest
this_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if not this_dir in sys.path:
    # Fix for running tests on the Mac 
    sys.path.insert(0, this_dir)


if 'testextendmock' in sys.modules:
    # Fix for running tests under Wing
    import tests
    import testextendmock
    tests.testextendmock = testextendmock

from testcase import TestCase

from mock import Mock
from extendmock import mocksignature, MagicMock


class TestMockSignature(TestCase):

    def testFunction(self):
        def f(a):
            pass
        mock = Mock()
        
        f2  = mocksignature(f, mock)
        self.assertRaises(TypeError, f2)
        mock.return_value = 3
        self.assertEquals(f2('foo'), 3)
        mock.assert_called_with('foo')
    
    
    def testMethod(self):
        class Foo(object):
            def method(self, a, b):
                pass
        
        f = Foo()
        mock = Mock()
        mock.return_value = 3
        f.method = mocksignature(f.method, mock)
        self.assertEquals(f.method('foo', 'bar'), 3)
        mock.assert_called_with('foo', 'bar')


    def testFunctionWithDefaults(self):
        def f(a, b=None):
            pass
        mock = Mock()
        f2  = mocksignature(f, mock)
        f2(3)
        mock.assert_called_with(3, None)
        mock.reset()
        
        f2(1, 7)
        mock.assert_called_with(1, 7)
        

class TestMagicMock(TestCase):
    
    def testRepr(self):
        mock = MagicMock()
        self.assertEqual(repr(mock), object.__repr__(mock))
        mock.__repr__ = lambda self: 'foo'
        self.assertEqual(repr(mock), 'foo')


    def testStr(self):
        mock = MagicMock()
        self.assertEqual(str(mock), object.__str__(mock))
        mock.__str__ = lambda self: 'foo'
        self.assertEqual(str(mock), 'foo')
    
    
    def testDictMethods(self):
        mock = MagicMock()
        
        self.assertRaises(TypeError, lambda: mock['foo'])
        def _del():
            del mock['foo']
        def _set():
            mock['foo'] = 3
        self.assertRaises(TypeError, _del)
        self.assertRaises(TypeError, _set)
        
        _dict = {}
        def getitem(s, name):
            return _dict[name]    
        def setitem(s, name, value):
            _dict[name] = value
        def delitem(s, name):
            del _dict[name]
        
        mock.__setitem__ = setitem
        mock.__getitem__ = getitem
        mock.__delitem__ = delitem
        
        self.assertRaises(KeyError, lambda: mock['foo'])
        mock['foo'] = 'bar'
        self.assertEquals(_dict, {'foo': 'bar'})
        self.assertEquals(mock['foo'], 'bar')
        del mock['foo']
        self.assertEquals(_dict, {})
            
            
    def testNumeric(self):
        original = mock = MagicMock()
        mock.value = 0
        
        self.assertEqual(mock.__add__(3), NotImplemented)
        
        def add(self, other):
            mock.value += other
            return self
        mock.__add__ = add
        self.assertEqual(mock + 3, mock)
        self.assertEqual(mock.value, 3)
        
        self.assertEqual(mock.__iadd__(3), NotImplemented)        
        mock.__iadd__ = add
        mock += 6
        self.assertEqual(mock, original)
        self.assertEqual(mock.value, 9)
        
        self.assertEqual(mock.__radd__(3), NotImplemented)
        mock.__radd__ = add
        self.assertEqual(7 + mock, mock)
        self.assertEqual(mock.value, 16)
    
    
    def testHash(self):
        mock = MagicMock()
        # test delegation
        self.assertEqual(hash(mock), Mock.__hash__(mock))
        
        def _hash(s):
            return 3
        mock.__hash__ = _hash
        self.assertEqual(hash(mock), 3)
    
    
    def testNonZero(self):
        m = MagicMock()
        self.assertTrue(bool(m))
        
        nonzero = lambda s: False
        m.__nonzero__ = nonzero
        self.assertFalse(bool(m))
    
        
    def testComparison(self):
        self. assertEqual(MagicMock() < 3, object() < 3)
        self. assertEqual(MagicMock() > 3, object() > 3)
        self. assertEqual(MagicMock() <= 3, object() <= 3)
        self. assertEqual(MagicMock() >= 3, object() >= 3)
        
        mock = MagicMock()
        def comp(s, o):
            return True
        mock.__lt__ = mock.__gt__ = mock.__le__ = mock.__ge__ = comp
        self. assertTrue(mock < 3)
        self. assertTrue(mock > 3)
        self. assertTrue(mock <= 3)
        self. assertTrue(mock >= 3)

    
    def testEquality(self):
        mock = MagicMock()
        self.assertEqual(mock, mock)
        self.assertNotEqual(mock, MagicMock())
        self.assertNotEqual(mock, 3)
        
        def eq(self, other):
            return other == 3
        mock.__eq__ = eq
        self.assertTrue(mock == 3)
        self.assertFalse(mock == 4)
        
        def ne(self, other):
            return other == 3
        mock.__ne__ = ne
        self.assertTrue(mock != 3)
        self.assertFalse(mock != 4)
    
    
    def testLenContainsIter(self):
        mock = MagicMock()
        
        self.assertRaises(TypeError, len, mock)
        self.assertRaises(TypeError, iter, mock)
        self.assertRaises(TypeError, lambda: 'foo' in mock)
        
        mock.__len__ = lambda s: 6
        self.assertEqual(len(mock), 6)
        
        mock.__contains__ = lambda s, o: o == 3
        self.assertTrue(3 in mock)
        self.assertFalse(6 in mock)
        
        mock.__iter__ = lambda s: iter('foobarbaz')
        self.assertEqual(list(mock), list('foobarbaz'))
        

if __name__ == '__main__':
    unittest.main()
    