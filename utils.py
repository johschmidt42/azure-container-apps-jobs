import logging
import sys
import uuid

from models import OrderEvent

logger: logging.Logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))
logger.level = logging.INFO


def generate_order_msg() -> str:
    """
    Generate an order message.

    Returns:
        str: The JSON representation of the order event.
    """
    order_id: str = str(uuid.uuid4())
    logger.info(f"Generating a new order msg: {order_id}")
    order_event: OrderEvent = OrderEvent(order_id=order_id, msg="Hello World")
    return order_event.model_dump_json()


def process_message(order_event: OrderEvent) -> None:
    """
    Processes a given order event message.

    Args:
        order_event: An instance of the OrderEvent class representing the order event message to be processed.

    Raises:
        Exception: If an error occurs during the processing of the message.

    Returns:
        None: No value is returned.
    """
    try:
        ...

    except Exception as ex:
        logger.exception(ex)
        logger.error("Failed to process message!")
        raise ex


def process_message_fail(order_event: OrderEvent) -> None:
    raise ValueError("Can't process message!")
