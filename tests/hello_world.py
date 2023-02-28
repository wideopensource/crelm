from crelm import Tube

paste = Tube('libhello_world') \
    .set_source_folder_from(__file__) \
    .add_header('hello_world.h') \
    .add_source('hello_world.c') \
    .squeeze()

if paste:
    paste.hello_world()
