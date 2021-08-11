from cacheflow import python
import unittest


class TestParsing(unittest.TestCase):
    def test_inputs(self):
        res = python.parse_code(
            'a = 2\n'
            + 'c = a + b\n'
            + 'b = 4\n'
            + 'c = c + 1\n'
        )
        self.assertEqual(res['inputs'], {'b'})
        self.assertEqual(res['outputs'], {'a', 'b', 'c'})

        res = python.parse_code(
            'def foo(c=d):\n'
            + '    a = b\n'
        )
        self.assertEqual(res['inputs'], {'b', 'd'})
        self.assertEqual(res['outputs'], {'foo'})

        res = python.parse_code(
            'lambda c=d: (a := b)\n',
        )
        self.assertEqual(res['inputs'], {'b', 'd'})
        self.assertEqual(res['outputs'], set())

        res = python.parse_code(
            'def foo():\n'
            + '    global a\n'
            + '    a = b\n'
        )
        self.assertEqual(res['inputs'], {'b'})
        self.assertEqual(res['outputs'], {'foo', 'a'})

        res = python.parse_code(
            'class Foo(D):\n'
            + '    global a\n'
            + '    a = b\n'
            + '    c = 2\n'
        )
        self.assertEqual(res['inputs'], {'b', 'D'})
        self.assertEqual(res['outputs'], {'Foo', 'a'})

        res = python.parse_code(
            '[a + d for b in c for a in b]\n'
        )
        self.assertEqual(res['inputs'], {'c', 'd'})
        self.assertEqual(res['outputs'], set())

        res = python.parse_code(
            '{a: d for b in c for a in b}\n'
        )
        self.assertEqual(res['inputs'], {'c', 'd'})
        self.assertEqual(res['outputs'], set())

        res = python.parse_code(
            'from a.b import c as d\n'
            + 'import e.f.g as h'
        )
        self.assertEqual(res['inputs'], set())
        self.assertEqual(res['outputs'], {'d', 'h'})
        self.assertEqual(res['imports'], {'a.b.c', 'e.f.g'})
