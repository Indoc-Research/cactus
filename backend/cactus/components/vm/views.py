from uuid import UUID

from cactus.components.cloud.clients import CloudClient
from cactus.components.cloud.clients import get_cloud_client
from cactus.components.vm.schemas import InstanceCreateSchema
from cactus.components.vm.schemas import InstanceStatusResponseSchema
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi.responses import Response

router = APIRouter(prefix='/vms', tags=['VMs'])


@router.get('/', summary='List all the VMs.')
def list_vms(
    cloud_client: CloudClient = Depends(get_cloud_client),
):
    """List all the VMs."""

    return cloud_client.list_instances()


@router.post('/', summary='Create a VM.')
def create_vm(
    body: InstanceCreateSchema,
    cloud_client: CloudClient = Depends(get_cloud_client),
):
    """Create a VM."""

    return cloud_client.create_instance(body)


@router.get('/{instance_id}', summary='Get the VM.')
def get_vm(
    instance_id: UUID,
    cloud_client: CloudClient = Depends(get_cloud_client),
):
    """Get the VM."""

    return cloud_client.get_instance(instance_id)


@router.get('/{instance_id}/status', summary='Get the status of services on the VM.')
def get_vm_services_status(
    instance_id: UUID,
    cloud_client: CloudClient = Depends(get_cloud_client),
):
    """Get the status of services on the VM."""

    status = cloud_client.get_instance_status(instance_id)

    return InstanceStatusResponseSchema(jhub=status)


@router.delete('/{instance_id}', summary='Delete the VM.')
def delete_vm(
    instance_id: UUID,
    cloud_client: CloudClient = Depends(get_cloud_client),
):
    """Delete the VM."""

    return cloud_client.delete_instance(instance_id)


@router.get('/oauth/{redirect_id}', summary='OAuth callback.')
def oauth_callback(
    redirect_id: UUID,
    request: Request,
    cloud_client: CloudClient = Depends(get_cloud_client),
):
    """OAuth callback."""

    instance = cloud_client.find_instance(redirect_id)

    if not instance:
        return Response(status_code=404)

    return RedirectResponse(
        url=f'http://{instance.public_ip}:{cloud_client.jhub_port}/hub/oauth_callback?{request.query_params}'
    )
