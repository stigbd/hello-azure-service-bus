# sender

A small webserver that will send any message posted to /message to the Azure Service Bus queue.

Send a single message:
```bash
uv run --env-file .env sender.py
```
