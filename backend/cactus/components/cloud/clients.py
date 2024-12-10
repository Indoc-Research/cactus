import base64
import time as tm
from textwrap import dedent
from uuid import UUID
from uuid import uuid4

from cactus.components.cloud.models import Instance
from cactus.components.vm.schemas import InstanceCreateSchema
from cactus.config import Settings
from cactus.config import get_settings
from exoscale.api.v2 import Client as ExoscaleClient
from fastapi import Depends


class CloudClient:
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        zone: str,
        cloud_template_id: UUID,
        security_group_id: UUID,
        host_instance_id: UUID,
        github_oauth_client_id: str,
        github_oauth_client_secret: str,
    ) -> None:
        self.client = ExoscaleClient(api_key, api_secret, zone=zone)
        self.cloud_template_id = cloud_template_id
        self.security_group_id = security_group_id
        self.host_instance_id = host_instance_id

        self.github_oauth_client_id = github_oauth_client_id
        self.github_oauth_client_secret = github_oauth_client_secret

    def wait_for_operation_state(self, operation_id: UUID, status: str = 'success', timeout: int = 300) -> None:
        end_time = tm.perf_counter() + timeout

        while tm.perf_counter() < end_time:
            operation = self.client.get_operation(id=operation_id)
            if operation['state'] == status:
                return
            tm.sleep(10)

        raise TimeoutError

    def list_instances(self):
        response = self.client.list_instances()
        instances = [Instance.model_validate(instance) for instance in response['instances']]

        return instances

    def get_instance(self, instance_id: UUID) -> Instance:
        response = self.client.get_instance(id=instance_id)
        instance = Instance.model_validate(response)

        return instance

    def create_instance(self, payload: InstanceCreateSchema) -> Instance:
        redirect_id = uuid4()

        user_data = dedent(
            f"""
            #cloud-config
            runcmd:
              - "PUBLIC_IP=$(hostname -I | awk '{{print $1}}')"
              - "GITHUB_OAUTH_CALLBACK_URL=http://$PUBLIC_IP:8080/callback/{redirect_id}/"
              - >
                sed -i
                -e "s|GITHUB_OAUTH_CLIENT_ID|{self.github_oauth_client_id}|g"
                -e "s|GITHUB_OAUTH_CLIENT_SECRET|{self.github_oauth_client_secret}|g"
                -e "s|GITHUB_OAUTH_CALLBACK_URL|$GITHUB_OAUTH_CALLBACK_URL|g"
                /opt/tljh/config/config.yaml
              - "tljh-config reload"
            """
        ).encode()

        response = self.client.create_instance(
            public_ip_assignment='inet4',
            labels={'redirect_id': str(redirect_id)},
            security_groups=[{'id': str(self.security_group_id)}],
            instance_type={'id': str(payload.size.to_id())},
            template={'id': str(self.cloud_template_id)},
            ssh_key={'name': 'antonio_key', 'fingerprint': '02:51:97:3e:d9:e3:a8:e2:fb:c7:b6:57:14:f9:c5:34'},
            disk_size=50,
            user_data=base64.b64encode(user_data).decode(),
        )

        operation_id = UUID(response['id'])
        self.wait_for_operation_state(operation_id)

        instance_id = UUID(response['reference']['id'])
        instance = self.get_instance(instance_id)

        return instance

    def delete_instance(self, instance_id: UUID) -> Instance:
        instance = self.get_instance(instance_id)

        response = self.client.delete_instance(id=instance_id)
        operation_id = UUID(response['id'])
        self.wait_for_operation_state(operation_id)

        return instance


def get_cloud_client(settings: Settings = Depends(get_settings)) -> CloudClient:
    return CloudClient(
        settings.cloud_api_key,
        settings.cloud_api_secret,
        settings.cloud_zone,
        settings.cloud_template_id,
        settings.cloud_security_group_id,
        settings.cloud_host_instance_id,
        settings.github_oauth_client_id,
        settings.github_oauth_client_secret,
    )
