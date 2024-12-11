from typing import Any

from cactus.components.cloud.models import InstanceType
from cactus.components.schemas import BaseSchema
from pydantic import conlist
from pydantic import field_validator

KERNELS = {
    'neuralactivitycubic': {
        'PYTHON_VERSION': '3.11',
        'UNIQUE_ENV_NAME': 'neuralactivitycubic',
        'KERNEL_DISPLAY_NAME': 'Python (with NA3)',
        'PIP_PACKAGES': ['neuralactivitycubic'],
    },
    'sklearn': {
        'PYTHON_VERSION': '3.13',
        'UNIQUE_ENV_NAME': 'sklearn',
        'KERNEL_DISPLAY_NAME': 'Python (with scikit-learn)',
        'PIP_PACKAGES': ['scikit-learn'],
    },
    'nbdev': {
        'PYTHON_VERSION': '3.13',
        'UNIQUE_ENV_NAME': 'nbdev',
        'KERNEL_DISPLAY_NAME': 'Python (with nbdev)',
        'PIP_PACKAGES': ['nbdev'],
    },
}


class InstanceCreateSchema(BaseSchema):
    size: InstanceType = InstanceType.SMALL
    python_env: conlist(str, min_length=1)

    @field_validator('python_env')
    @classmethod
    def validate_python_env(cls, values: list[str]) -> list[dict[str, Any]]:
        envs = []

        for value in values:
            if value not in KERNELS:
                raise ValueError(f'"{value}" is unsupported python environment')
            envs.append(KERNELS[value])

        return envs
