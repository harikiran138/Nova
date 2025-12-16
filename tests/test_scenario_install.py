import sys
try:
    import colorama
    print("colorama is installed.")
except ImportError:
    print("colorama is missing. Expecting Nova to install it.")
    raise
