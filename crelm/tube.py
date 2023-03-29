from os.path import dirname, realpath, join as path_join, exists
from os import remove, mkdir
from pexpect import run as pexpect_run
from tempfile import gettempdir
from typing import List, TypeVar
from cffi import FFI
from importlib import import_module, reload

from .factory import Factory

TSelf = TypeVar('TSelf', bound='Tube')


class Tube:
    _GENERATED_FILENAME_BASE = 'crelm_generated'
    _PREPROCESSOR_FILENAME_BASE = 'crelm_cpp'

    def __init__(self, name: str):
        self._name = name

        self._source_folder = '.'
        self._target_folder = None
        self._imports = []
        self._header_filenames = []
        self._source_filenames = []
        self._source_text = ''
        self._header_text = ''
        self._macros = []
        self._compiler_args = []
        self._lib_path = None
        self._temp_folderbame = path_join(gettempdir(), 'crelm')
        self._gen_foldername = path_join(self._temp_folderbame, name)
        self._verbose = False

        if not exists(self._temp_folderbame):
            mkdir(self._temp_folderbame)

    @ property
    def _preprocessor_source_filename(self) -> str:
        # return self._make_gen_filename(Tube._PREPROCESSOR_FILENAME_BASE + '.h')
        return Tube._PREPROCESSOR_FILENAME_BASE + '.c'

    @ property
    def _generated_header_filename(self) -> str:
        # return self._make_gen_filename(Tube._GENERATED_FILENAME_BASE + '.h')
        return Tube._GENERATED_FILENAME_BASE + '.h'

    @ property
    def _generated_source_filename(self) -> str:
        # return self._make_gen_filename(Tube._GENERATED_FILENAME_BASE + '.c')
        return Tube._GENERATED_FILENAME_BASE + '.c'

    @ property
    def _module_name(self):
        return f'lib{self._name}'

    def _make_gen_filename(self, filename: str) -> str:
        return path_join(self._gen_foldername, filename)

    def _make_source_fullpath(self, filename: str) -> str:
        return path_join(self._source_folder, filename)

    def _create_gen_folder(self):
        folder_name = self._make_gen_filename('')
        if not exists(folder_name):
            mkdir(folder_name)

    def _load_file(self, filename: str) -> str:
        gen_filename = self._make_gen_filename(filename)

        with open(gen_filename, 'rt') as f:
            return f.read()

    def _save_file(self, filename: str, text: str):
        gen_filename = self._make_gen_filename(filename)

        if self._verbose:
            print(f'saving text "{text}" to {gen_filename}')

        with open(gen_filename, 'wt') as f:
            f.write(text)

    def _delete_file(self, filename: str):
        gen_filename = self._make_gen_filename(filename)

        if self._verbose:
            print(f'deleting file {gen_filename}')

        try:
            remove(gen_filename)
        except:
            pass

    @ property
    def compile_defines(self) -> str:
        return ' '.join([f'-D{macro}' for macro in self._macros])

    def _preprocess_text(self, source: str, strip_includes: bool = False) -> str:
        if strip_includes:
            source = '\n'.join(
                [line.strip() for line in source.split('\n') if not line.startswith('#include')]).strip()

        self._save_file(self._preprocessor_source_filename, source)

        filename = self._make_gen_filename(self._preprocessor_source_filename)
        command = f'gcc -w -E {self.compile_defines} {filename}'

        output, status = pexpect_run(command, withexitstatus=True)
        if status != 0:
            if self._verbose:
                print(output.decode())
            return None

        lines = output.decode().split('\n')

        return '\n'.join(
            [line.strip() for line in lines if not line.startswith('#')]).strip()

    def _preprocess_headers(self) -> str:

        headers = '\n'.join(
            [f'#include "{x}"' for x in self._header_filenames])

        amalgamated_header_filename = self._make_gen_filename('amalgamated_headers.h')

        with open(amalgamated_header_filename, 'wt') as f:
            f.write(headers)

        command = f'gcc -w -E {self.compile_defines} {amalgamated_header_filename}'
        if self._verbose:
            print(f'_preprocess_headers: {command}')

        output, status = pexpect_run(command, withexitstatus=True)
        if status != 0:
            if self._verbose:
                print(output.decode())
            return None

        lines = output.decode().split('\n')

        return '\n'.join(
            [line.strip() for line in lines if not line.startswith('#')]).strip()

    def _generate(self) -> bool:
        self._create_gen_folder()

        self._delete_file(self._generated_header_filename)

        self._save_file(self._generated_source_filename,
                        self._source_text + '\n')

        if 0 != len(self._source_text):

            if 0 == len(self._header_text):
                text = self._preprocess_text(
                    self._source_text, strip_includes=True)

                self._header_text = Factory().create_LibCrelm().make(text)

                if self._verbose:
                    print(
                        f'makeheaders: {self._source_text} -> {self._header_text}')
            else:
                self._header_text = self._preprocess_text(self._header_text)

                self._save_file(self._generated_header_filename,
                                self._header_text + '\n')

        if len(self._header_text):
            self._header_text = self._preprocess_text(self._header_text)

            self._save_file(self._generated_header_filename,
                            self._header_text + '\n')
        else:
            self._save_file(self._generated_header_filename,
                            self._header_text + '\n')

        self._header_filenames += [
            self._make_gen_filename(self._generated_header_filename)]

        self._cdef = self._preprocess_headers()

        if self._verbose:
            print(f'cdef: {self._cdef}')

        return True

    def _build_headers(self) -> str:
        headers = '\n'.join(
            [f'#include "{x}"' for x in self._header_filenames])

        return headers

    def _build_compiler_args(self) -> List[str]:
        args = self._compiler_args
        args += [f'-D{x}' for x in self._macros]
        return args

    def _build(self) -> None:
        self._delete_file(self._module_name)

        if self._verbose:
            print(f'header_text: {self._header_text}')
            print(f'source_text: {self._source_text}')

        if 0 == (len(self._source_filenames) + len(self._source_text)):
            raise RuntimeError("No sources specified")

        if 0 != len(self._source_filenames) and 0 == (len(self._header_filenames) + len(self._header_text)):
            raise RuntimeError("Source file supplied without header")

        if not self._generate():
            raise RuntimeError("Failed to generate")

        source_filenames = self._source_filenames + \
            [self._make_gen_filename(self._generated_source_filename)]

        headers = self._build_headers()
        args = self._build_compiler_args()

        if self._verbose:
            print(f'module: {self._module_name}')
            print(f'cdef: {self._cdef}')
            print(f'headers: {headers}')
            print(f'sources: {source_filenames}')
            print(f'args: {args}')
            print(f'verbose: {self._verbose}')
            print(f'gen folder: {self._gen_foldername}')

        ffibuilder = FFI()

        try:
            ffibuilder.cdef(self._cdef)
        except:
            print(self._cdef)
            raise RuntimeError("invalid cdef")
        
        
        ffibuilder.set_source(self._module_name,
                              headers,
                              sources=source_filenames,
                              extra_compile_args=args,
                              libraries=[],
                              include_dirs=[],
                              library_dirs=[],
                              )

        try:
            self._lib_path = ffibuilder.compile(
                tmpdir=self._gen_foldername,
                verbose=self._verbose)
        except:
            raise RuntimeError('Compilation failed')

        if self._verbose:
            print(f'lib: {self._lib_path}')

    def verbose(self, v: bool = True) -> TSelf:
        self._verbose = v
        return self

    def supress_warning(self, warning: str) -> TSelf:
        self._compiler_args.append(f'-Wno-{warning}')
        return self

    def save_compiler_temps(self) -> TSelf:
        self._compiler_args.append('-save-temps=obj')
        return self

    def set_gen_folder(self, path: str) -> TSelf:
        # self._gen_foldername = path
        return self

    def set_source_folder(self, folder: str):
        self._source_folder = folder
        return self

    def set_source_folder_from(self, filename: str):
        self.set_source_folder(dirname(realpath(filename)))
        return self

    def add_header_file(self, filename: str) -> TSelf:
        fullpath = self._make_source_fullpath(filename)
        self._header_filenames.append(fullpath)
        return self

    def add_header_files(self, filenames: List[str]) -> TSelf:
        for filename in filenames:
            self.add_header_file(filename)
        return self

    def add_header_text(self, text: str) -> TSelf:
        self._header_text += '\n' + text
        return self

    def add_source_file(self, filename: str) -> TSelf:
        fullpath = self._make_source_fullpath(filename)
        self._source_filenames.append(fullpath)
        return self

    def add_source_files(self, filenames: List[str]) -> TSelf:
        for filename in filenames:
            self.add_source_file(filename)
        return self

    def add_source_text(self, text: str) -> TSelf:
        self._source_text += '\n' + text
        return self

    def add_macro(self, macro: str) -> TSelf:
        self._macros.append(macro)
        return self

    def add_macros(self, macros: List[str]) -> TSelf:
        for macro in macros:
            self._macros.append(macro)
        return self

    def add_macro_if(self, predicate: bool, macro: str) -> TSelf:
        if predicate:
            self._macros.append(macro)
        return self

    class Paste:
        def __init__(self, tube: TSelf):

            self._tube = tube

            for attr in dir(self._tube._lib):
                self.__setattr__(attr, getattr(self._tube._lib, attr))

        @ classmethod
        def choose(cls, name: str, path=None):
            return Tube(name) \
                .set_gen_folder(path if path else '') \
                .squeeze(build=False)

        def new(self, typename: str):
            return self._tube._ffi.new(f"{typename} *")

        def new_char_array(self, v):
            if isinstance(v, str):
                return self._tube._ffi.new(f"char[]", v.encode('utf-8'))

            if isinstance(v, int):
                return self._tube._ffi.new(f"char[{v}]")

            return None

        def string(self, var):
            return self._tube._ffi.string(var).decode('utf-8')

    def squeeze(self, build: bool = True) -> TSelf:
        if build:
            self._build()

        from sys import path
        path.append(self._gen_foldername)

        try:
            module = import_module(self._module_name)
        except:
            raise RuntimeError('Unable to load module')

        reload(module)
        self._lib = module.lib
        self._ffi = module.ffi

        return Tube.Paste(self)
