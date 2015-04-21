
def read_file_as_string(file):
    f = ''
    htmlfile = open(file)

    for l in htmlfile:
        f +=l
    
    return f

