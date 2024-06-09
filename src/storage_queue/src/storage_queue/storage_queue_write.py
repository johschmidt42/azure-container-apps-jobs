import logging
import sys

from azure.identity import DefaultAzureCredential
from azure.storage.queue import QueueClient, QueueMessage
from shared.models import StorageQueueSettings
from shared.utils import generate_order_msg

logger: logging.Logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))
logger.setLevel(logging.INFO)


def write_to_storage_queue(content: str) -> None:
    """
    Args:
        content (str): The content to be written to the queue.

    Returns:
        None

    """
    settings: StorageQueueSettings = StorageQueueSettings()
    credential: DefaultAzureCredential = DefaultAzureCredential()
    queue_client: QueueClient = QueueClient(
        settings.storage_queue_url,
        queue_name=settings.queue_name,
        credential=credential,
    )
    msg: QueueMessage = queue_client.send_message(content=content, time_to_live=-1)
    logger.info(msg)


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
        write_to_storage_queue(content=content)
    except Exception as ex:
        logger.exception(ex)
        raise ex


if __name__ == "__main__":
    run()
