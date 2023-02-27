from crelm import Tube
from os.path import dirname, realpath

paste = Tube('libhello_world') \
    .set_source_folder(dirname(realpath(__file__))) \
    .add_header('hello_world.h') \
    .add_source('hello_world.c') \
    .squeeze()

if paste:
    import libhello_world

    libhello_world.lib.hello_world()
