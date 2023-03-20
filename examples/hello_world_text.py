from crelm import Factory

source = '''
#include <stdio.h>

void hello_world() { puts("hello world text!\\n"); }
'''

paste = Factory().create_Tube('hello_world_text') \
    .add_source_text(source) \
    .squeeze()

if paste:
    paste.hello_world()
