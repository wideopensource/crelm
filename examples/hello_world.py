from crelm import Factory

paste = Factory().create_Tube('hello_world') \
    .set_source_folder_relative(__file__) \
    .add_header_file('hello_world.h') \
    .add_source_file('hello_world.c') \
    .squeeze()

if paste:
    paste.hello_world()
