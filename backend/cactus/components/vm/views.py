from uuid import UUID

from cactus.components.cloud.clients import CloudClient
from cactus.components.cloud.clients import get_cloud_client
from cactus.components.vm.schemas import InstanceCreateSchema
from fastapi import APIRouter
from fastapi import Depends

router = APIRouter(prefix='/vms', tags=['VMs'])


@router.get('/', summary='List all VMs.')
def list_vms(
    cloud_client: CloudClient = Depends(get_cloud_client),
):
    """List all VMs."""

    return cloud_client.list_instances()


@router.post('/', summary='Create a new VM.')
def create_vm(
    body: InstanceCreateSchema,
    cloud_client: CloudClient = Depends(get_cloud_client),
):
    """Create a new VM."""

    return cloud_client.create_instance(body)


@router.delete('/{instance_id}', summary='Delete an existing VM.')
def delete_vm(
    instance_id: UUID,
    cloud_client: CloudClient = Depends(get_cloud_client),
):
    """Delete an existing VM."""

    return cloud_client.delete_instance(instance_id)
