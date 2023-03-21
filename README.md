# Crelm
The Crelm package provides a relatively simple API around the CFFI system. Give it C code or source files, it gives you a package with bindings to functions and `struct`s. Easiest way to get started is hack up the examples in [the repo](https://github.com/wideopensource/crelm/tree/main/examples).

### Installation

pip3 install crelm

### Simple Demo

```
from crelm import Factory

paste = Factory(debug=False, verbose=True).create_Tube('add2') \
    .add_source_text('int add2(int a, int b) { return a + b; }') \
    .squeeze()

print(f'2 + 3 = {paste.add2(2, 3)}')
```
