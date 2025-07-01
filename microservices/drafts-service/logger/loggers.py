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

# golbal variables
LOGGER_NAME                     = "drafts-service"
DEFAULT_LOG_LEVEL               = "INFO"        # default
LOCAL_LOGGING_ENABLED           = True          # default
CONSOLE_LOGGING_ENABLED         = True          # default
BETTER_STACK_LOGGING_ENABLED    = True          # default

# get .env virables
# => setting the log-level as specified in .env
# => if not specified, default is DEFAULT_LOG_LEVEL
# => options are: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = os.getenv("LOG_LEVEL", DEFAULT_LOG_LEVEL).upper()

# => setting the Source-token and Ingesting-host-url for logging as specified in .env
BETTER_STACK_SOURCE_TOKEN = os.getenv("BETTER_STACK_SOURCE_TOKEN")
BETTER_STACK_HOST_URL = os.getenv("BETTER_STACK_HOST_URL")

# get logger
# => init logger instance
root_logger = logging.getLogger(LOGGER_NAME) 

# create handler
# => determine where to ship the logs
stream_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler(f'./{LOGGER_NAME}.log')
better_stack_handler = LogtailHandler(
    source_token = BETTER_STACK_SOURCE_TOKEN,
    host = BETTER_STACK_HOST_URL
)

# create & set formatter
# => init the formatting of a log piece and attach it to the handlers
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
root_logger_formmater = BetterFormatter()
stream_handler.setFormatter(root_logger_formmater)
file_handler.setFormatter(root_logger_formmater)
better_stack_handler.setFormatter(root_logger_formmater)

# set handler
# => attach the handlers to the logger
root_logger.handlers = []
root_logger.addHandler(stream_handler)
root_logger.addHandler(file_handler)
root_logger.addHandler(better_stack_handler)

# set log-level
# => setting the log-level to our logger
root_logger.setLevel(LOG_LEVEL)

# initial logs
root_logger.info(f"'{LOGGER_NAME}' root logger is initialized!")
if not LOCAL_LOGGING_ENABLED:
    root_logger.warning(f"local logging for {LOGGER_NAME} is disabled!")
if not CONSOLE_LOGGING_ENABLED:
    root_logger.warning(f"console logging for {LOGGER_NAME} is disabled!")
if not BETTER_STACK_LOGGING_ENABLED:
    root_logger.warning(f"better-stack (cloud) logging for {LOGGER_NAME} is disabled!")
elif not (BETTER_STACK_SOURCE_TOKEN and BETTER_STACK_HOST_URL):
    root_logger.warning("BetterStack logging enabled but is not configured! Please set BETTER_STACK_SOURCE_TOKEN and BETTER_STACK_HOST_URL environment variables.")

