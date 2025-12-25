import sys
try:
    import pytz
    print("pytz is already installed.")
except ImportError:
    print("pytz is missing. This script should fail initially.")
    raise
