
MEASUREMENT_IS_ACTIVE = False
PAUSE_IS_ACTIVE = False
VALUES = []
LONGTERM_VALUES = []
STREED_WIDTH = 0
LIMIT_VALUE = 5
TABLENAME = "na"
IS_LISTING = False
WARN_LEVEL = 0

def setWarnLevel(level):
    global WARN_LEVEL
    if WARN_LEVEL < level:
        WARN_LEVEL = level
