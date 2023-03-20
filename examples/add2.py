from crelm import Factory

paste = Factory(debug=False, verbose=True).create_Tube('add2') \
    .add_source_text('int add2(int a, int b) { return a + b; }') \
    .squeeze()

print(f'2 + 3 = {paste.add2(2, 3)}')
