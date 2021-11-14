
import sys, os
from ginvoice.environment import get_resource


def __safe_path__(filename, default_path):
    if sys.argv[0].endswith('.py'):
        return os.path.join(default_path, filename)
    return get_resource(filename)


def find_css_file(filename):
    return __safe_path__(filename, "../res/css")


def find_ui_file(filename):
    return __safe_path__(filename, "../res/glade")
