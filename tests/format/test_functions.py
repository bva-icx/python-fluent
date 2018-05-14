from __future__ import absolute_import, unicode_literals

import unittest

from fluent.context import MessageContext
from fluent.resolver import FluentReferenceError

from ..syntax import dedent_ftl


class TestFunctionCalls(unittest.TestCase):

    def setUp(self):
        self.ctx = MessageContext(['en-US'], use_isolating=False,
                                  functions={'IDENTITY': lambda x: x})
        self.ctx.add_messages(dedent_ftl("""
            foo = Foo
                .attr = Attribute
            pass-nothing       = { IDENTITY() }
            pass-string        = { IDENTITY("a") }
            pass-number        = { IDENTITY(1) }
            pass-message       = { IDENTITY(foo) }
            pass-attr          = { IDENTITY(foo.attr) }
            pass-external      = { IDENTITY($ext) }
            pass-function-call = { IDENTITY(IDENTITY(1)) }
        """))

    def test_accepts_strings(self):
        val, errs = self.ctx.format('pass-string', {})
        self.assertEqual(val, "a")
        self.assertEqual(len(errs), 0)

    def test_accepts_numbers(self):
        val, errs = self.ctx.format('pass-number', {})
        self.assertEqual(val, "1")
        self.assertEqual(len(errs), 0)

    def test_accepts_entities(self):
        val, errs = self.ctx.format('pass-message', {})
        self.assertEqual(val, "Foo")
        self.assertEqual(len(errs), 0)

    def test_accepts_attributes(self):
        val, errs = self.ctx.format('pass-attr', {})
        self.assertEqual(val, "Attribute")
        self.assertEqual(len(errs), 0)

    def test_accepts_externals(self):
        val, errs = self.ctx.format('pass-external', {'ext': 'Ext'})
        self.assertEqual(val, "Ext")
        self.assertEqual(len(errs), 0)

    def test_accepts_function_calls(self):
        val, errs = self.ctx.format('pass-function-call', {})
        self.assertEqual(val, "1")
        self.assertEqual(len(errs), 0)

    def test_wrong_arity(self):
        val, errs = self.ctx.format('pass-nothing', {})
        self.assertEqual(val, "IDENTITY()")
        self.assertEqual(len(errs), 1)
        self.assertEqual(type(errs[0]), TypeError)


class TestMissing(unittest.TestCase):

    def setUp(self):
        self.ctx = MessageContext(['en-US'], use_isolating=False)
        self.ctx.add_messages(dedent_ftl("""
            missing = { MISSING(1) }
        """))

    def test_falls_back_to_name_of_function(self):
        val, errs = self.ctx.format("missing", {})
        self.assertEqual(val, "MISSING()")
        self.assertEqual(errs,
                         [FluentReferenceError("Unknown function: MISSING")])
