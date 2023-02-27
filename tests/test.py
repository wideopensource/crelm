from crelm import Tube
from os.path import dirname, realpath

paste = Tube('libtest') \
    .set_source_folder(dirname(realpath(__file__))) \
    .add_header('leibniz.h') \
    .add_source('leibniz.c') \
    .squeeze()

if paste:
    print(paste.so)

    from sys import path
    path.append('gen')

    import libtest

    state = libtest.ffi.new('struct leibniz_state_t *')

    libtest.lib.leibniz_init(state)

    while True:
        print(libtest.lib.leibniz_run(state))
