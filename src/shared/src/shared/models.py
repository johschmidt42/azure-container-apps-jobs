from pydantic import BaseModel, computed_field
from pydantic_settings import BaseSettings


class ServiceBusQueueSettings(BaseSettings):
    service_bus_namespace: str = "joh-service-bus-namespace"
    queue_name: str = "messages"

    @computed_field
    @property
    def service_bus_url(self) -> str:
        return f"{self.service_bus_namespace}.servicebus.windows.net"


class StorageQueueSettings(BaseSettings):
    storage_account: str = "johstorageacc"
    queue_name: str = "messages"

    @computed_field
    @property
    def storage_queue_url(self) -> str:
        return f"https://{self.storage_account}.queue.core.windows.net"

    @computed_field
    @property
    def poison_queue_name(self) -> str:
        return f"{self.queue_name}-poison"


class StorageBlobSettings(BaseSettings):
    storage_account: str = "johannesstorageacc"
    container_name: str = "data"
    blob_name: str = "test.txt"

    @computed_field
    @property
    def storage_blob_url(self) -> str:
        return f"https://{self.storage_account}.blob.core.windows.net"


class OrderEvent(BaseModel):
    order_id: str
    msg: str
