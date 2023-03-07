import os
import pexpect
from typing import List, TypeVar
from os.path import dirname, realpath

from cffi import FFI

TSelf = TypeVar('TSelf', bound='Tube')


class Tube:
    def __init__(self, name: str):
        self._name = name

        self._source_folder = '.'
        self._target_folder = None
        self._imports = []
        self._header_filenames = []
        self._source_filenames = []
        self._macros = []
        self._lib_path = None
        self._gen_foldername = 'gen'
        self._verbose = True

    def _make_fullpath(self, filename: str) -> str:
        return os.path.join(self._source_folder, filename)

    def _load_file(self, filename: str) -> str:
        with open(filename) as f:
            return f.read()

    def _build_cdef(self) -> bool:
        headers = ' '.join(
            [f'{x}' for x in self._header_filenames])

        macros = ' '.join([f'-D{macro}' for macro in self._macros])

        command = f'gcc -w -E {macros} {headers}'

        output, status = pexpect.run(command, withexitstatus=True)
        if status != 0:
            self._cdef = output.decode()
            return False

        lines = output.decode().split('\n')
        self._cdef = '\n'.join(
            [line.strip() for line in lines if not line.startswith('#')]).strip()

        print(f"preproc: {command} -> {self._cdef}")

        return True

    def _build_headers(self) -> str:
        headers = '\n'.join(
            [f'#include "{x}"' for x in self._header_filenames])
        return headers  # self._apply_preprocessor(headers)

    def _build_defines(self) -> str:

        lines = []
        # f'#define {x[0]} {x[1] if len(x) > 1 else ""}' for x in [m.split('=') for m in self._macros]]

        return '\n'.join(lines)

    def _build_compiler_args(self) -> List[str]:
        args = []
        args += [f'-D{x}' for x in self._macros]
        args.append('-save-temps=obj')

        print(args)
        return args

    def set_source_folder(self, folder: str):
        self._source_folder = folder
        return self

    def set_source_folder_from(self, filename: str):
        self.set_source_folder(dirname(realpath(filename)))
        return self

    def add_header(self, filename: str) -> TSelf:
        fullpath = self._make_fullpath(filename)
        self._header_filenames.append(fullpath)
        return self

    def add_headers(self, filenames: List[str]) -> TSelf:
        for filename in filenames:
            self.add_header(filename)
        return self

    def add_source(self, filename: str) -> TSelf:
        fullpath = self._make_fullpath(filename)
        self._source_filenames.append(fullpath)
        return self

    def add_sources(self, filenames: List[str]) -> TSelf:
        for filename in filenames:
            self.add_source(filename)
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

    def new(self, typename: str):
        return self._ffi.new(f"{typename} *")

    class Paste:
        def __init__(self, tube: TSelf):
            self._tube = tube

            self.new = tube.new

            for attr in dir(tube._lib):
                self.__setattr__(attr, getattr(tube._lib, attr))

    def build(self) -> TSelf:
        if 0 == len(self._header_filenames):
            raise RuntimeError("No headers specified")

        if 0 == len(self._source_filenames):
            raise RuntimeError("No sources specified")

        if not self._build_cdef():
            raise RuntimeError(f"Failed to generate cdef ({self._cdef})")

        print(self._build_defines())

        ffibuilder = FFI()
        ffibuilder.cdef(self._cdef)
        ffibuilder.set_source(self._name,
                              self._build_defines() + '\n' + self._build_headers(),
                              sources=self._source_filenames,
                              extra_compile_args=self._build_compiler_args(),
                              libraries=[],
                              include_dirs=[],
                              library_dirs=[],
                              )

        self._lib_path = ffibuilder.compile(
            tmpdir=self._gen_foldername,
            verbose=self._verbose)

        return self

    def squeeze(self) -> TSelf:
        from sys import path
        path.append(self._gen_foldername)

        import importlib
        module = importlib.import_module(f"{self._name}")
        self._lib = module.lib
        self._ffi = module.ffi

        return Tube.Paste(self)
