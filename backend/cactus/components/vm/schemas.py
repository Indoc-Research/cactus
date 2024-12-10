from cactus.components.cloud.models import InstanceType
from cactus.components.schemas import BaseSchema


class InstanceCreateSchema(BaseSchema):
    size: InstanceType = InstanceType.SMALL
    python_env: list[str]
