import logging
import sys

from azure.identity import DefaultAzureCredential
from azure.servicebus import ServiceBusClient, ServiceBusMessage

from shared.models import ServiceBusQueueSettings
from shared.utils import generate_order_msg

logger: logging.Logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))
logger.setLevel(logging.INFO)


def write_to_service_bus_queue(content: str) -> None:
    """
    Args:
        content (str): The content to be written to the queue.

    Returns:
        None

    """
    settings: ServiceBusQueueSettings = ServiceBusQueueSettings()
    credential: DefaultAzureCredential = DefaultAzureCredential()

    msg: ServiceBusMessage = ServiceBusMessage(body=content)

    with ServiceBusClient(
        fully_qualified_namespace=settings.service_bus_url,
        credential=credential,
    ) as servicebus_client:
        with servicebus_client.get_queue_sender(
            queue_name=settings.queue_name
        ) as sender:
            sender.send_messages(message=msg, timeout=60)

    logger.info(content)


def run() -> None:
    """
    Writes the content generated from the `generate_order_msg()` method to a queue using the `write_to_queue()` method, and logs any exceptions that occur.

    Returns:
        None

    Raises:
        Exception: If an error occurs while writing to the queue or generating the order message.

    """
    try:
        content: str = generate_order_msg()
        write_to_service_bus_queue(content=content)
    except Exception as ex:
        logger.exception(ex)
        raise ex


if __name__ == "__main__":
    run()
