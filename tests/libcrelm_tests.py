from john import TestCase

# todo foss: this is a bit hacky
# from crelm import VerboseFactory as Factory
# from crelm import DebugFactory as Factory
from crelm import Factory


class TestMakeHeaders(TestCase, Factory):

    def test_make_headers_simple(self):
        expected = "int a();"
        actual = self.create_LibCrelm().make(expected)
        assert expected == actual

    def test_make_headers_function(self):
        expected = "void b();"
        actual = self.create_LibCrelm().make("void b() { return 1; }")
        assert expected == actual

    def test_make_headers_function_int(self):
        expected = "int c();"
        actual = self.create_LibCrelm().make("int c() { return 1; }")
        assert expected == actual

    def test_make_headers_functions(self):
        expected = "int d();\nint e();"
        actual = self.create_LibCrelm().make(
            "int d() { return 1; } int e() { return 1; }")
        assert expected == actual
