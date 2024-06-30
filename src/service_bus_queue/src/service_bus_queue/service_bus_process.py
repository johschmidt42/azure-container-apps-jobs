import json
import logging
import sys
from typing import List

from azure.identity import DefaultAzureCredential
from azure.servicebus import ServiceBusClient, ServiceBusReceivedMessage
from shared.models import OrderEvent, ServiceBusQueueSettings
from shared.utils import process_message

logger: logging.Logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))
logger.setLevel(logging.INFO)


class ServiceBusQueue:
    """Service Bus queue class."""

    def __init__(self):
        """Initialize the service bus queue class."""
        self.settings: ServiceBusQueueSettings = ServiceBusQueueSettings()
        self.credential: DefaultAzureCredential = DefaultAzureCredential()

    def run(self) -> None:
        """Process service bus queue messages.

        Uses system-provided dead-lettering.

        Returns: None

        """
        with ServiceBusClient(
            fully_qualified_namespace=self.settings.service_bus_url,
            credential=self.credential,
        ) as servicebus_client:
            with servicebus_client.get_queue_receiver(
                queue_name=self.settings.queue_name
            ) as receiver:
                # This part should always work. Otherwise, Azure Container Apps will
                # endlessly process the same (visible) message,
                # because the message will not be read/processed.
                messages: List[ServiceBusReceivedMessage] = receiver.receive_messages(
                    max_message_count=1, max_wait_time=5
                )

                msg: None | ServiceBusReceivedMessage = next(iter(messages), None)

                # exit early if no messages are present
                if msg is None:
                    logger.info("No messages received")
                    return None

                logger.info(
                    f"Processing a new message from service bus queue: {msg.message_id}"
                )

                try:
                    order_event: OrderEvent = OrderEvent(**json.loads(str(msg)))
                    process_message(order_event=order_event)
                    receiver.complete_message(
                        message=msg
                    )  # removes the message from the queue

                except Exception as ex:
                    logger.exception(ex)
                    raise ex

                return None


if __name__ == "__main__":
    process: ServiceBusQueue = ServiceBusQueue()
    process.run()
