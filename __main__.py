from sys import exit

from crelm import Factory


def demo() -> int:
    print('Initialising Crelm Factory...')

    source = r'''
#include <stdio.h>

#define STRINGIFY(S) STRINGIFY2(S)
#define STRINGIFY2(S) #S
#define GREETING hello

int GREETING(char const *who)
{ 
    printf(STRINGIFY(GREETING) " %s!\n", who); 

    return 1729; 
}
'''
    print(
        f'...and using this C code:\n{source}\nto test it...\n')

    tube = Factory().create_Tube('hellocrelm').add_source_text(source)

    paste = tube.squeeze()

    print(paste.hello(b'crelm'))

    print('\n..., which should have printed "Hello crelm!" followed the smallest integer that can be written as the sum of two cubes in two different ways')

    print(
        f'In the process it generated this declaration:\n\n{tube._cdef}\n\nwhich has had the GREETING macro expanded by the preprocessor')

    return 42

if '__main__' == __name__:

    exit(demo())
