from selenium import webdriver

def get_new_browser():
     #self.browser = webdriver.Firefox()
     browser = webdriver.PhantomJS()
     browser.set_window_size(1120, 550)
     return browser


def read_file_as_string(file):
    f = ''
    htmlfile = open(file)

    for l in htmlfile:
        f +=l
    
    return f

