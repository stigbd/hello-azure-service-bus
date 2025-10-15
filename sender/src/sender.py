# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Example to show sending message(s) to a Service Bus Queue asynchronously.

Warning:
ServiceBusClient, ServiceBusSender, and ServiceBusMessageBatch are not coroutine-safe.
Do not share these instances between coroutines without proper coroutine-safe
management using mechanisms like asyncio.Lock.

"""

import asyncio
import logging
import os
import sys
from datetime import UTC, datetime

from azure.servicebus import ServiceBusMessage
from azure.servicebus.aio import ServiceBusClient

AZURE_SERVICE_BUS_CONNECTION_STRING = os.environ["AZURE_SERVICE_BUS_CONNECTION_STRING"]
AZURE_SERVICE_BUS_QUEUE_NAME = os.environ["AZURE_SERVICE_BUS_QUEUE_NAME"]

# Set up logger:
# 1. Get a logger instance
# It's good practice to name your logger, often using __name__ for module-specific logs.
logger = logging.getLogger("hello-azure-service-bus.sender")
# 2. Set the logging level for the logger
# Messages with a severity level lower than this will be ignored.
# Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
logger.setLevel(logging.DEBUG)
# 3. Create a console handler (to display logs on the console)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)  # Set handler-specific level


# 4. Create a formatter (to define the log message format)
class CustomFormatter(logging.Formatter):
    """Custom formatter to include ISO 8601 timestamp with milliseconds and timezone."""

    def formatTime(self, record: logging.LogRecord, datefmt: str | None = None) -> str:  # noqa: N802
        """Return the creation time of the specified LogRecord as formatted text."""
        _ = datefmt  # Unused parameter
        return (
            datetime.fromtimestamp(record.created)
            .astimezone(UTC)
            .isoformat(timespec="milliseconds")
        )


formatter = CustomFormatter(fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# 5. Add the formatter to the handlers
console_handler.setFormatter(formatter)
# 6. Add the handlers to the logger
logger.addHandler(console_handler)
# Optional: Prevent log messages from being propagated to the root logger
logger.propagate = False
# Get the logger for Azure Service Bus
servicebus_logger = logging.getLogger("azure.servicebus")
servicebus_logger.setLevel(logging.WARNING)  # Or logging.ERROR, logging.CRITICAL
# You might also want to control logs from the underlying AMQP library
# which is often used by Service Bus
amqp_logger = logging.getLogger("uamqp")
amqp_logger.setLevel(logging.WARNING)


async def main() -> None:
    """Set up the client and send a message."""
    logger.info("Starting the sender")
    async with ServiceBusClient.from_connection_string(
        AZURE_SERVICE_BUS_CONNECTION_STRING
    ) as servicebus_client:
        logger.info("Creating the ServiceBusClient")
        async with servicebus_client:
            logger.info("Getting the sender")
            sender = servicebus_client.get_queue_sender(
                queue_name=AZURE_SERVICE_BUS_QUEUE_NAME
            )
            logger.info("Creating the ServiceBusSender context")
            async with sender:
                logger.info("Sending message...")
                message = ServiceBusMessage(
                    f"Hello World. The time is {datetime.now(tz=UTC)}"
                )
                await sender.send_messages(message)

    logger.info("Send message is done.")


asyncio.run(main())
