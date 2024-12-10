from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel
from pydantic import Field


class Instance(BaseModel):
    id: UUID
    name: str
    public_ip: str = Field(alias='public-ip', serialization_alias='public_ip')


class InstanceType(StrEnum):
    MICRO: str = 'micro'
    TINY: str = 'tiny'
    SMALL: str = 'small'
    MEDIUM: str = 'medium'
    LARGE: str = 'large'

    def to_id(self) -> UUID:
        return {
            'micro': UUID('71004023-bb72-4a97-b1e9-bc66dfce9470'),
            'tiny': UUID('b6cd1ff5-3a2f-4e9d-a4d1-8988c1191fe8'),
            'small': UUID('21624abb-764e-4def-81d7-9fc54b5957fb'),
            'medium': UUID('b6e9d1e8-89fc-4db3-aaa4-9b4c5b1d0844'),
            'large': UUID('c6f99499-7f59-4138-9427-a09db13af2bc'),
        }.get(self)
