import logging
import sys
import os
from logtail import LogtailHandler 

#####################################################################
#                       for the team members!                       #
#                                                                   #
# this is an invitation link for our BetterStack log manager:       #
# https://betterstack.com/users/join/rVni4YUQE3YgwzCe3AX7Ebgt       #
#####################################################################

# get .env virables
# => setting the log-level as specified in .env
# => if not specified, default is "INFO"
# => options are: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()

# => setting the Source token for logging as specified in .env
BETTER_STACK_SOURCE_TOKEN = os.getenv("LOG_TOKEN")

# get logger
# => init logger instance
gateway_logger = logging.getLogger("api-gateway") 

# create formatter
# => init the formatting of a log piece
class InfoOnlyFormatter(logging.Formatter):
    def __init__(self):
        self.info_fmt = "[%(asctime)s] %(levelname)s:\t\t%(message)s"
        self.other_fmt = "[%(asctime)s] %(levelname)s:\t%(message)s"
        super().__init__(fmt=self.other_fmt)

    def format(self, record):
        if record.levelno == logging.INFO:
            self._style._fmt = self.info_fmt
        else:
            self._style._fmt = self.other_fmt
        return super().format(record)

gateway_log_formmater = InfoOnlyFormatter()

# create handler
# => determine where to ship the logs
stream_handler  = logging.StreamHandler(sys.stdout)
file_handler    = logging.FileHandler('./api_gateway.log')
better_stack_handler = LogtailHandler(source_token=BETTER_STACK_SOURCE_TOKEN)

# set formatter
# => attach the log formmater to the handlers
stream_handler.setFormatter(gateway_log_formmater)
file_handler.setFormatter(gateway_log_formmater)

# set handler
# => attach the handlers to the logger
gateway_logger.handlers = [
    stream_handler,
    file_handler,
    better_stack_handler
    ]

# set log-level
# => setting the log-level to our logger
gateway_logger.setLevel(LOG_LEVEL)