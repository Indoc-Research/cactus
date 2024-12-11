from uuid import UUID

from cactus.components.cloud.clients import CloudClient
from cactus.components.cloud.clients import get_cloud_client
from cactus.components.vm.schemas import InstanceCreateSchema
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi.responses import Response

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

    return RedirectResponse(url=f'http://{instance.public_ip}:8080/hub/oauth_callback?{request.query_params}')
