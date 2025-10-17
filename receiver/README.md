# receiver

Start the receiver:

```bash
uv run --env-file .env receiver.py
```

Need to investigate the following error:
```
Connection closed with error: [b'amqp:connection:forced', b"The connection was closed by container '7bbfe513364a4f4fbd07d5e35a3603c2_G0' because it did not have any active links in the past 300000 milliseconds. TrackingId:7bbfe513364a4f4fbd07d5e35a3603c2_G0, SystemTracker:gateway1, Timestamp:2025-10-17T09:17:12", None]
```
