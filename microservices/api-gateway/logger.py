import  logging
import  os
import  sys
from    logtail     import LogtailHandler 

#-------------------------------------------------------------------
#                       for the team members!                       
#                                                                   
# this is an invitation link for our BetterStack log manager:       
# https://betterstack.com/users/join/rVni4YUQE3YgwzCe3AX7Ebgt       
#                                                                   
#-------------------------------------------------------------------

BETTER_STACK_LOGGING_ENABLED = True

# get .env virables
# => setting the log-level as specified in .env
# => if not specified, default is "INFO"
# => options are: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# => setting the Source-token and Ingesting-host-url for logging as specified in .env
BETTER_STACK_SOURCE_TOKEN = os.getenv("BETTER_STACK_SOURCE_TOKEN")
BETTER_STACK_HOST_URL = os.getenv("BETTER_STACK_HOST_URL")
if not (BETTER_STACK_SOURCE_TOKEN or BETTER_STACK_HOST_URL):
    BETTER_STACK_LOGGING_ENABLED = False

# get logger
# => init logger instance
gateway_logger = logging.getLogger("api-gateway") 

# create formatter
# => init the formatting of a log piece
class BetterFormatter(logging.Formatter):
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
gateway_log_formmater = BetterFormatter()

# create handler
# => determine where to ship the logs
stream_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler('./api_gateway.log')
if BETTER_STACK_LOGGING_ENABLED:
    better_stack_handler = LogtailHandler(
        source_token = BETTER_STACK_SOURCE_TOKEN,
        host = BETTER_STACK_HOST_URL
    )

# set formatter
# => attach the log formmater to the handlers
stream_handler.setFormatter(gateway_log_formmater)
file_handler.setFormatter(gateway_log_formmater)
if BETTER_STACK_LOGGING_ENABLED:
    better_stack_handler.setFormatter(gateway_log_formmater)

# set handler
# => attach the handlers to the logger
gateway_logger.handlers = []
gateway_logger.addHandler(stream_handler)
gateway_logger.addHandler(file_handler)
if BETTER_STACK_LOGGING_ENABLED:
    gateway_logger.addHandler(better_stack_handler)
else:
    gateway_logger.warning("BetterStack logging is not configured. Please set LOG_TOKEN and LOG_HOST_URL environment variables.")

# set log-level
# => setting the log-level to our logger
gateway_logger.setLevel(LOG_LEVEL)