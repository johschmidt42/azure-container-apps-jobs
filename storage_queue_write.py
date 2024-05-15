import logging
import sys
import uuid

from azure.identity import DefaultAzureCredential
from azure.storage.queue import QueueClient

from models import OrderEvent, StorageQueueSettings

logger: logging.Logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))
logger.level = logging.INFO


def write_queue() -> None:
    try:
        order_id: str = str(uuid.uuid4())
        logger.info(f"Writing a new message to storage queue: {order_id}")

        settings: StorageQueueSettings = StorageQueueSettings()
        credential = DefaultAzureCredential()
        queue_client: QueueClient = QueueClient(
            settings.storage_queue_url,
            queue_name=settings.queue_name,
            credential=credential,
        )

        content: str = OrderEvent(
            order_id=order_id, msg="Hello World"
        ).model_dump_json()
        msg: str = queue_client.send_message(content=content, time_to_live=-1)
        logger.info(msg)
        return
    except Exception as ex:
        logger.exception(ex)


if __name__ == "__main__":
    write_queue()
