
from tempfile import gettempdir


class FactoryState:
    _lib_debug = None
    _lib_release = None
    _gen_folder = None

    def __init__(self, factory, verbose: bool = False, debug: bool = False, path=None):
        self.factory = factory
        self._verbose = verbose
        self._debug = debug

        if not path and not FactoryState._gen_folder:
            Factory._gen_folder = gettempdir()

        if path and path != FactoryState._gen_folder:
            FactoryState._gen_folder = path
            FactoryState._lib_debug = None
            FactoryState._lib_release = None

    @property
    def lib(self):
        return FactoryState._lib_debug if self._debug else FactoryState._lib_release

    def build_lib(self):
        if self._debug and not FactoryState._lib_debug:
            FactoryState._lib_debug = self.factory._build_lib(
                verbose=self._verbose,
                debug=True,
                path=FactoryState._gen_folder)

        if not self._debug and not FactoryState._lib_release:
            FactoryState._lib_release = self.factory._build_lib(
                verbose=self._verbose,
                debug=False,
                path=FactoryState._gen_folder)

        return self.lib


class Factory:

    def __init__(self, verbose: bool = False, debug: bool = False, path=None):
        self.factory_state = FactoryState(factory=self,
                                          verbose=verbose, debug=debug, path=path)

    def _build_lib(self, verbose: bool, debug: bool, path: str):
        from .tube import Tube

        if verbose:
            print(f'building libcrelm, DEBUG={debug}, gen folder={path}')

        return Tube(f'crelm_{"debug" if debug else "release"}') \
            .verbose(verbose) \
            .set_gen_folder(path) \
            .set_source_folder_from(__file__) \
            .add_header_text('int make_header(char const *source, char *header);') \
            .add_source_file('makeheaders_crelm.c') \
            .add_macro_if(debug, 'DEBUG') \
            .save_compiler_temps() \
            .supress_warning('format-overflow') \
            .supress_warning('sign-compare') \
            .supress_warning('unused-function') \
            .supress_warning('stringop-truncation') \
            .squeeze()

    def create_LibCrelm(self):
        from .libcrelm import LibCrelm

        return LibCrelm(lib=self.factory_state.build_lib())

    def create_Tube(self, name: str):
        from .tube import Tube

        return Tube(name=name)


class VerboseFactory(Factory):

    def __init__(self, debug: bool = False, path=None):
        super().__init__(verbose=True, debug=debug, path=path)


class DebugFactory(Factory):

    def __init__(self, verbose: bool = False, path=None):
        super().__init__(verbose=verbose, debug=True, path=path)


class VerboseDebugFactory(Factory):

    def __init__(self, path=None):
        super().__init__(verbose=True, debug=True, path=path)
