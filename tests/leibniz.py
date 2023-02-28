from crelm import Tube

paste = Tube('libtest') \
    .set_source_folder_from(__file__) \
    .add_header('leibniz.h') \
    .add_source('leibniz.c') \
    .squeeze()

print(dir(paste))

if paste:
    state = paste.new('struct leibniz_state_t')

    paste.leibniz_init(state)

    for i in range(10):
        print(paste.leibniz_run(state))
