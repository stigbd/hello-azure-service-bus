# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Example to show receiving batch messages from a Service Bus Queue asynchronously."""

import asyncio
import logging
import os
import sys
from asyncio.exceptions import CancelledError
from datetime import UTC, datetime

import uvicorn
from azure.servicebus.aio import ServiceBusClient
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

AZURE_SERVICE_BUS_CONNECTION_STRING = os.environ["AZURE_SERVICE_BUS_CONNECTION_STRING"]
AZURE_SERVICE_BUS_QUEUE_NAME = os.environ["AZURE_SERVICE_BUS_QUEUE_NAME"]

# Set up logger:
# 1. Get a logger instance
# It's good practice to name your logger, often using __name__ for module-specific logs.
logger = logging.getLogger("hello-azure-service-bus.receiver")
# 2. Set the logging level for the logger
# Messages with a severity level lower than this will be ignored.
# Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
logger.setLevel(logging.INFO)
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


# Expose a health check endpoint using FastAPI:
async def simple_web_server() -> None:
    """Set up simple web server to expose a health check endpoint."""
    api = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

    @api.get("/health")
    async def health_check() -> dict:
        return {"status": "ok"}

    Instrumentator().instrument(api).expose(api)

    # Run the web server
    config = uvicorn.Config(api, host="0.0.0.0", port=8000, log_level="info")  # noqa: S104
    server = uvicorn.Server(config)
    await server.serve()


async def main() -> None:
    """Set up the client and receive messages."""
    logger.info("Starting the web server")
    running_tasks = set()
    task = asyncio.create_task(simple_web_server())
    running_tasks.add(task)
    task.add_done_callback(lambda t: running_tasks.remove(t))

    logger.info("Setting up the service bus client")
    async with (
        ServiceBusClient.from_connection_string(
            AZURE_SERVICE_BUS_CONNECTION_STRING
        ) as servicebus_client,
        servicebus_client,
    ):
        logger.info("Setting up the receiver")
        receiver = servicebus_client.get_queue_receiver(
            queue_name=AZURE_SERVICE_BUS_QUEUE_NAME
        )
        async with receiver:
            logger.info("Listening for messages...")
            async for message in receiver:
                log_msg = f"Received: {message}"
                logger.info(log_msg)
                await receiver.complete_message(message)


while True:
    try:
        asyncio.run(main())
    except CancelledError:
        logger.info("Program cancelled. Exiting...")
        break
    except KeyboardInterrupt:
        logger.info("Program interrupted by user. Exiting...")
        break
