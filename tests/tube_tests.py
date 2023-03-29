from john import TestCase
from crelm import Factory


class TestSqueeze(TestCase, Factory):

    def test_squeeze_without_source_raises(self):
        tube = self.create_Tube(self.testName)

        with self.assertRaises(BaseException):
            tube.squeeze()


class TestGenerateWithText(TestCase, Factory):

    def make_plotter_source(self, min: float, max: float, width: int) -> str:
        return f'''
#include <stdio.h>

void plot(float v)
{{
    char p = '*';

    float const d = {max} - {min};
    if (d < {min})
    {{
        v = {min};
        p = '<';
    }}
    else if (d > {max})
    {{
        v = {max};
        p = '>';
    }}

    v -= {min};
    v *= (float){width} / d;

    const int j = (int)v;

    for (int i = 0; i < {width}; ++i)
    {{
        printf("%c", j == i ? p : '.');    
    }}

    puts("");
}}
    '''

    def test_source_text(self):
        # source = 'int test_source_text() { return 2; }'

        source = self.make_plotter_source(-1, 1, 10)

        actual = self.create_Tube(self.testName) \
            .set_gen_folder(self.tempFolder) \
            .add_source_text(source) \
            .squeeze()

        self.assertTrue(actual)


class TestPasteWithText(TestCase, Factory):

    def test_source_text(self):
        actual = self.create_Tube(self.testName) \
            .set_gen_folder(self.tempFolder) \
            .add_source_text('int test_source_text() { return 2; }') \
            .squeeze() \
            .test_source_text()

        self.assertEqual(2, actual)

    def test_source_header_text(self):
        actual = self.create_Tube(self.testName) \
            .set_gen_folder(self.tempFolder) \
            .add_header_text('int test_source_header_text();') \
            .add_source_text('int test_source_header_text() { return 3; }') \
            .squeeze() \
            .test_source_header_text()

        self.assertEqual(3, actual)


class TestPasteWithFile(TestCase, Factory):

    def test_source_file_without_header_raises(self):
        source = self.writeFile('test.c', 'int test_file() { return 4; }')

        tube = self.create_Tube(self.testName) \
            .add_source_file(source)

        with self.assertRaises(BaseException):
            tube.squeeze()

    def test_source_file_with_bad_header_raises(self):
        header = self.writeFile('test.h', 'int bad_test_file();')
        source = self.writeFile('test.c', 'int test_file() { return 4; }')

        sut = self.create_Tube(self.testName) \
            .add_header_file(header) \
            .add_source_file(source)

        with self.assertRaises(BaseException):
            sut.squeeze()

    def test_source_file_with_header(self):
        header = self.writeFile('test.h', 'int test_file();')
        source = self.writeFile('test.c', 'int test_file() { return 4; }')

        actual = self.create_Tube(self.testName) \
            .add_header_file(header) \
            .add_source_file(source) \
            .squeeze() \
            .test_file()

        self.assertEqual(4, actual)


class TestPasteWithFiles(TestCase, Factory):

    def test_source_files_with_headers(self):
        header1 = self.writeFile('test1.h', 'int test1_file();')
        source1 = self.writeFile('test1.c', 'int test1_file() { return 1; }')

        header2 = self.writeFile('test2.h', 'int test2_file();')
        source2 = self.writeFile('test2.c', 'int test2_file() { return 2; }')

        sut = self.create_Tube(self.testName) \
            .add_header_files([header1, header2]) \
            .add_source_files([source1, source2]) \
            .squeeze()

        actual1 = sut.test1_file()
        actual2 = sut.test2_file()

        self.assertEqual(1, actual1)
        self.assertEqual(2, actual2)

    def test_source_files_with_headers_separate(self):
        header1 = self.writeFile('test1.h', 'int test1_file();')
        source1 = self.writeFile('test1.c', 'int test1_file() { return 1; }')

        header2 = self.writeFile('test2.h', 'int test2_file();')
        source2 = self.writeFile('test2.c', 'int test2_file() { return 2; }')

        sut = self.create_Tube(self.testName) \
            .add_header_file(header1) \
            .add_source_file(source1) \
            .add_header_file(header2) \
            .add_source_file(source2) \
            .squeeze()

        actual1 = sut.test1_file()
        actual2 = sut.test2_file()

        self.assertEqual(1, actual1)
        self.assertEqual(2, actual2)


class TestMacros(TestCase, Factory):

    def test_source_text_with_source_macro(self):
        actual = self.create_Tube(self.testName) \
            .add_source_text('#define NAME test_source_text_with_source_macro\nint NAME() { return 6; }') \
            .squeeze() \
            .test_source_text_with_source_macro()

        self.assertEqual(6, actual)

    def test_source_text_with_compiler_macro(self):
        actual = self.create_Tube(self.testName) \
            .add_source_text('int NAME() { return 7; }') \
            .add_macro('NAME=test_source_text_with_compiler_macro') \
            .squeeze() \
            .test_source_text_with_compiler_macro()

        self.assertEqual(7, actual)

    def test_source_text_with_conditional_compiler_macro(self):
        sut = self.create_Tube(self.testName) \
            .add_source_text('int NAME() { return 8; }') \
            .add_macro_if(True, 'NAME=test_source_text_with_conditional_compiler_macro') \
            .squeeze()

        actual = sut.test_source_text_with_conditional_compiler_macro()

        self.assertEqual(8, actual)

    def test_source_text_with_missing_conditional_compiler_macro_raises(self):
        sut = self.create_Tube(self.testName) \
            .add_source_text('int NONAME() { return 8; }') \
            .add_macro_if(False, 'NONAME=test_source_text_with_missing_conditional_compiler_macro_raises') \
            .squeeze()

        self.assertEqual(1, len([x for x in dir(sut) if 'NONAME' == x]))

        with self.assertRaises(AttributeError):
            sut.test_source_text_with_missing_conditional_compiler_macro_raises()

class TestCompilerError(TestCase, Factory):
    def test_cdef_text(self):
        with self.assertRaises(RuntimeError):
            self.create_Tube(self.testName) \
                .add_source_text(f'this wont compile') \
                .squeeze()


