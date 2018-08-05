import logging
import os
from pprint import pformat

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
# These are the sequences need to get colored ouput

RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

def formatter_message(message, use_color = True):
    if use_color:
        message = message.replace("$RESET", RESET_SEQ).replace("$BOLD", BOLD_SEQ)
    else:
        message = message.replace("$RESET", "").replace("$BOLD", "")
    return message

COLORS = {
    'INFO': WHITE,
    'DEBUG': BLUE,
    'WARNING': YELLOW,
    'CRITICAL': RED,
    'ERROR': RED,
    'REQ': MAGENTA,
    'RREQ': GREEN
}

class ColoredFormatter(logging.Formatter):
    def __init__(self, msg, use_color = True):
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color
    def format(self, record):
        levelname = record.levelname
        # If an env filter is set and message matches filter, colorize it
        if 'LOGFILTER' in os.environ and os.environ['LOGFILTER'] in str(record.msg):
            record.msg = BOLD_SEQ + COLOR_SEQ % (30 + CYAN) + str(record.msg) + RESET_SEQ
            return logging.Formatter.format(self, record)
        if self.use_color and levelname in COLORS:
            levelname_color = COLOR_SEQ % (30 + COLORS[levelname]) + levelname + RESET_SEQ
            record.levelname = levelname_color
            if levelname in ['WARNING', 'ERROR', 'REQ', 'RREQ']:
                record.msg = COLOR_SEQ % (30 + COLORS[levelname]) + str(record.msg) + RESET_SEQ
            elif levelname == 'CRITICAL':
                record.msg = record.filename + ':' + str(record.lineno) + COLOR_SEQ % (30 + CYAN) + '\n' + pformat(record.msg) + RESET_SEQ
            elif levelname == 'DEBUG':
                # Colorize API calls
                record.msg = str(record.msg)
                record.msg = record.msg.replace(
                    'API method call from',
                    BOLD_SEQ + COLOR_SEQ % (30 + MAGENTA) + 'API method call from' + RESET_SEQ
                )
        return logging.Formatter.format(self, record)


