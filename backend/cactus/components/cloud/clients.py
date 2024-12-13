import base64
import time as tm
from pathlib import Path
from textwrap import dedent
from textwrap import indent
from uuid import UUID
from uuid import uuid4

from cactus.components.cloud.models import Instance
from cactus.components.repo.validators import RepoValidator
from cactus.components.repo.validators import get_repo_validator
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
        template_id: UUID,
        security_group_id: UUID,
        host_url: str,
        github_oauth_client_id: str,
        github_oauth_client_secret: str,
        setup_environment_script_path: Path,
        repo_validator: RepoValidator,
    ) -> None:
        self.client = ExoscaleClient(api_key, api_secret, zone=zone)
        self.template_id = template_id
        self.security_group_id = security_group_id
        self.host_url = host_url

        self.github_oauth_client_id = github_oauth_client_id
        self.github_oauth_client_secret = github_oauth_client_secret

        self.setup_environment_script = setup_environment_script_path.read_text()
        self.repo_validator = repo_validator

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

    def find_instance(self, redirect_id: UUID) -> Instance | None:
        instances = self.list_instances()

        for instance in instances:
            if instance.labels.get('redirect_id') == str(redirect_id):
                return instance

    def create_instance(self, payload: InstanceCreateSchema) -> Instance:
        redirect_id = uuid4()

        setup_environment_commands = ''
        for env in payload.python_envs or []:
            packages = "', '".join(env['PIP_PACKAGES'])

            setup_environment_commands += f"""
                /usr/local/bin/setup_environment.sh \
                '{env["PYTHON_VERSION"]}' '{env["UNIQUE_ENV_NAME"]}' '{env["KERNEL_DISPLAY_NAME"]}' \
                '{packages}'"""

        for repo_url in payload.repo_urls or []:
            repo = self.repo_validator.get_validation_results(str(repo_url))
            setup_environment_commands += f"""
                /usr/local/bin/setup_environment.sh \
                '{repo["PYTHON_VERSION"].lstrip('>=')}' '{repo["UNIQUE_ENV_NAME"]}' '{repo["UNIQUE_ENV_NAME"]}' \
                --url '{repo_url}'"""

        setup_environment_script = '\n' + indent(self.setup_environment_script, ' ' * 18)

        user_data = dedent(
            f"""
            #cloud-config
            write_files:
              - path: /usr/local/bin/setup_environment.sh
                permissions: '0755'
                owner: root:root
                content: | {setup_environment_script}
            runcmd:
              - >
                sed -i
                -e "s|GITHUB_OAUTH_CLIENT_ID|{self.github_oauth_client_id}|g"
                -e "s|GITHUB_OAUTH_CLIENT_SECRET|{self.github_oauth_client_secret}|g"
                -e "s|GITHUB_OAUTH_CALLBACK_URL|{self.host_url}/vms/oauth/{redirect_id}|g"
                /opt/tljh/config/config.yaml
              - "tljh-config reload"
              - "systemctl stop jupyterhub"
              - | {setup_environment_commands}
              - "systemctl start jupyterhub"
            """
        )

        response = self.client.create_instance(
            public_ip_assignment='inet4',
            labels={'redirect_id': str(redirect_id)},
            security_groups=[{'id': str(self.security_group_id)}],
            instance_type={'id': str(payload.size.to_id())},
            template={'id': str(self.template_id)},
            ssh_key={'name': 'antonio_key', 'fingerprint': '02:51:97:3e:d9:e3:a8:e2:fb:c7:b6:57:14:f9:c5:34'},
            disk_size=50,
            user_data=base64.b64encode(user_data.encode()).decode(),
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


def get_cloud_client(
    settings: Settings = Depends(get_settings), repo_validator: RepoValidator = Depends(get_repo_validator)
) -> CloudClient:
    setup_environment_script_path = Path(__file__).parent / 'create_tljh_kernel.sh'

    return CloudClient(
        settings.cloud_api_key,
        settings.cloud_api_secret,
        settings.cloud_zone,
        settings.cloud_template_id,
        settings.cloud_security_group_id,
        settings.cloud_host_url,
        settings.github_oauth_client_id,
        settings.github_oauth_client_secret,
        setup_environment_script_path,
        repo_validator,
    )
