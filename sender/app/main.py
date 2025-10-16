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

import logging
import logging.config
import os
from pathlib import Path
import yaml

from azure.servicebus import ServiceBusMessage
from azure.servicebus.aio import ServiceBusClient
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel
from pythonjsonlogger.json import JsonFormatter

AZURE_SERVICE_BUS_CONNECTION_STRING = os.environ["AZURE_SERVICE_BUS_CONNECTION_STRING"]
AZURE_SERVICE_BUS_QUEUE_NAME = os.environ["AZURE_SERVICE_BUS_QUEUE_NAME"]

# Get the logger:
logger = logging.getLogger("uvicorn.error")
# Get the logger for Azure Service Bus
servicebus_logger = logging.getLogger("azure.servicebus")
servicebus_logger.setLevel(logging.WARNING)  # Or logging.ERROR, logging.CRITICAL
# You might also want to control logs from the underlying AMQP library
# which is often used by Service Bus
amqp_logger = logging.getLogger("uamqp")
amqp_logger.setLevel(logging.WARNING)


class Message(BaseModel):
    """Message model."""

    content: str


async def send_message(message: Message) -> None:
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
                msg = ServiceBusMessage(message.model_dump_json())
                await sender.send_messages(msg)

    logger.info("Send message is done.")


app = FastAPI()

Instrumentator().instrument(app).expose(app, include_in_schema=False)


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/message")
async def post_message(message: Message) -> dict:
    """Endpoint to send a message to the Service Bus Queue."""
    await send_message(message)
    return {"status": "message sent"}
