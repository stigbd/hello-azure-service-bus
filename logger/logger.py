from datetime import datetime, UTC
import time
import logging
import sys


# 1. Get a logger instance
# It's common practice to name the logger using __name__ for module-specific logging.
logger = logging.getLogger(__name__)

# 2. Set the logging level for the logger
# Messages below this level will be ignored.
# Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
logger.setLevel(logging.INFO)

# 3. Create a handler to direct log messages to a destination
# StreamHandler for console output
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)  # Set handler's level

# FileHandler for writing to a file
file_handler = logging.FileHandler("app.log")
file_handler.setLevel(logging.INFO)  # Set handler's level


# 4. Create a formatter to define the log message structure
# Set a date format to iso 8601 with milliseconds and UTC timezone:
class MicrosecondsFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        return (
            datetime.fromtimestamp(record.created)
            .astimezone(UTC)
            .isoformat(timespec="milliseconds")
        )


formatter = MicrosecondsFormatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# 5. Add the formatter to the handlers
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# 6. Add the handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# 7. Use the logger to emit messages
logger.debug("This is a debug message.")
logger.info("This is an info message.")
logger.warning("This is a warning message.")
logger.error("This is an error message.")
logger.critical("This is a critical message.")

# sleep "indefinitely" to keep the application running
try:
    while True:
        time.sleep(3600)
except KeyboardInterrupt:
    logger.info("Application interrupted and is shutting down.")
