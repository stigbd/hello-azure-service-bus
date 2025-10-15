# hello-azure-service-bus

This is a simple example of how to use Azure Service Bus in an async Python application.

Investigates in particular the following aspects related to receiving messages both running locally and in docker:
- how to gracefully shutdown the service bus client (SIGTERM and SIGINT)
- how to do logging
- how to expose an http endpoint for health checks
- how to expose a prometheus metrics endpoint
- how to handle MessageLockLostError

.env
```bash
AZURE_SERVICE_BUS_CONNECTION_STRING="Endpoint=sb://localhost/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=SAS_KEY_VALUE;UseDevelopmentEmulator=true;
```

To run:

```bash
docker compose up -d
```

Ref:
- https://learn.microsoft.com/en-us/azure/service-bus-messaging/test-locally-with-service-bus-emulator?tabs=docker-linux-container
