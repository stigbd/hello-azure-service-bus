# sender

A small webserver that will send any message posted to /message to the Azure Service Bus queue.

Start the message sender server:
```bash
uv run --env-file .env fastapi dev
```

Or with uvicorn:
```
uv run --env-file=.env uvicorn app:app --host 0.0.0.0 --port 8000 --reload --reload-include "*.yaml"
```

Then in another terminal, send a message:
```bash
curl -i -X POST http://localhost:8000/message -d '{"content": "Yo!"}' -H "Content-Type: application/json"
```
