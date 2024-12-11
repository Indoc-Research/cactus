from typing import Union

import toml
import requests
import ast
from abc import ABC, abstractmethod



class RemoteRepoValidator(ABC):
    
    
    def run_validation_check(self, repo_url: str) -> dict:
        self._assert_repo_url_is_valid(repo_url)
        validation_results = self._validate_repo_content(repo_url)
        return validation_results
    
    
    @abstractmethod
    def _assert_repo_url_is_valid(self, repo_url: str) -> None:
        """ Raise ValueError if the passed URL is not valid for the corresponding source. """
        
        
    @abstractmethod
    def _validate_repo_content(self, repo_url: str) -> dict:
        """ Validate that all information required to successfully run 'pip install . -e' can be found in the repo. """




class GitHubRepoValidator(RemoteRepoValidator):
    
    
    def _assert_repo_url_is_valid(self, repo_url: str) -> None:
        owner, repo = repo_url.rstrip('/').split('/')[-2:]
        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/"
        response = requests.get(api_url)
        if response.status_code != 200:
            raise ValueError(f'Invalid GitHub URL: {repo_url}.')
        
    
    def _validate_repo_content(self, repo_url: str) -> dict:
        owner, repo = repo_url.rstrip('/').split('/')[-2:]
        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/"
        parsed_response = requests.get(api_url).json()
        evaluation_results = {}
        filenames = [file_info['name'] for file_info in parsed_response]
        if 'pyproject.toml' in filenames:
            pyproject_file_info = parsed_response[filenames.index('pyproject.toml')]
            evaluation_results['pyproject'] = self._evaluate_pyproject(pyproject_file_info)
            evaluation_results['pyproject']['last_updated_on'] = self._get_timestamp_of_last_update(owner, repo, 'pyproject.toml')
        elif 'setup.py' in filenames:
            setup_file_info = parsed_response[filenames.index('setup.py')]
            evaluation_results['setup'] = self._evaluate_setup(setup_file_info)
            evaluation_results['setup']['last_updated_on'] = self._get_timestamp_of_last_update(owner, repo, 'setup.py')
        elif 'requirements.txt' in filenames:
            requirements_file_info = parsed_response[filenames.index('requirements.txt')]
            evaluation_results['requirements'] = self._evaluate_requirements(requirements_file_info)
            evaluation_results['requirements']['last_updated_on'] = self._get_timestamp_of_last_update(owner, repo, 'requirements.txt')
        unified_results = self._unify_evaluation_results(evaluation_results)
        unified_results['url'] = repo_url
        return unified_results
    

    def _get_timestamp_of_last_update(self, owner: str, repo: str, filename: str) -> str:
        url = f"https://api.github.com/repos/{owner}/{repo}/commits"
        params = {"path": filename, "per_page": 1}
        response = requests.get(url, params=params)
        timestamp_of_last_modification = response.json()[0]["commit"]["committer"]["date"]
        return timestamp_of_last_modification
    
    
    def _evaluate_pyproject(self, file_info: dict) -> dict:
        pyproject_response = requests.get(file_info['download_url'])
        parsed_pyproject = toml.loads(pyproject_response.text)
        eval_results = {}
        if 'project' in parsed_pyproject.keys():
            if 'name' in parsed_pyproject['project'].keys():
                eval_results['package_name'] = parsed_pyproject['project']['name']
            if 'requires-python' in parsed_pyproject['project'].keys():
                eval_results['python_version'] = parsed_pyproject['project']['requires-python']
            if 'dependencies' in parsed_pyproject['project'].keys():
                eval_results['dependencies'] = parsed_pyproject['project']['dependencies']
        if ('build-system' in parsed_pyproject.keys()) & ('package_name' in eval_results.keys()):
            eval_results['is_valid'] = True
        else:
            eval_results['is_valid'] = False
        return eval_results
    
    
    def _evaluate_setup(self, setup_file_info: dict) -> dict:
        setup_response = requests.get(setup_file_info['download_url'])
        parsed_setup = self._parse_setup_response_text(setup_response.text)
        eval_results = {}
        if 'name' in parsed_setup.keys():
            eval_results['is_valid'] = True
            eval_results['package_name'] = parsed_setup['name']
        else:
            eval_results['is_valid'] = False
        # Try to find a required python version:
        if 'python_requires' in parsed_setup.keys():
            eval_results['python_version'] = parsed_setup['python_requires']
        elif 'classifiers' in parsed_setup.keys():        
            supported_versions = []
            for elem in parsed_setup['classifiers']:
                if 'Programming Language :: Python :: ' in elem:
                    python_version = float(elem.replace('Programming Language :: Python :: ', ''))
                    supported_versions.append(python_version)
            if len(supported_versions) > 0:
                eval_results['python_version'] = f'>={min(supported_versions)}'
        if 'install_requires' in parsed_setup.keys():
            eval_results['dependencies'] = parsed_setup['install_requires']
        return eval_results
    
    
    def _evaluate_requirements(self, requirements_file_info: dict) -> dict:
        requirements_response = requests.get(requirements_file_info['download_url'])
        parsed_requirements = requirements_response.text.splitlines()
        eval_results = {}
        if len(parsed_requirements) > 0:
            eval_results['is_valid'] = True
            eval_results['dependencies'] = parsed_requirements
        else:
            eval_results['is_valid'] = False
        return eval_results
    
    
    def _parse_setup_response_text(self, setup_response_text: str) -> dict:
        parsed_setup_infos = {}
        parsed_tree = ast.parse(setup_response_text)
        for node in ast.walk(parsed_tree):
            # Find the setup() call
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "setup":
                for keyword in node.keywords:
                    key = keyword.arg  # Argument name
                    value = keyword.value  # Argument value (AST node)

                    # Extract constant values (e.g., strings, numbers)
                    if isinstance(value, ast.Constant):
                        parsed_setup_infos[key] = value.value
                    # Extract list values
                    elif isinstance(value, ast.List):
                        parsed_setup_infos[key] = [elt.value for elt in value.elts if isinstance(elt, ast.Constant)]
                    # Extract dictionaries (if needed)
                    elif isinstance(value, ast.Dict):
                        parsed_setup_infos[key] = {
                            k.value: v.value for k, v in zip(value.keys, value.values)
                            if isinstance(k, ast.Constant) and isinstance(v, ast.Constant)
                        }
                    # Handle unsupported or complex expressions
                    else:
                        parsed_setup_infos[key] = f"Unsupported type: {type(value).__name__}"
        return parsed_setup_infos
    
    
    def _unify_evaluation_results(self, evaluation_results: dict) -> dict:
        unified_results = {}
        if len(evaluation_results.keys()) == 0:
            unified_results['valid_repo'] = False
        else:
            for key, param_name in [('package_name', 'UNIQUE_ENV_NAME'), ('python_version', 'PYTHON_VERSION'), ('dependencies', 'PIP_PACKAGES')]:
                unified_results[param_name] = self._get_value_from_latest_valid_source(evaluation_results, key)
            unified_results['valid_repo'] = self._check_if_all_information_are_present(unified_results)
        return unified_results   
    
    
    def _get_value_from_latest_valid_source(self, evaluation_results: dict, key: str):
        timestamps_of_valid_sources = {}
        for source in evaluation_results.keys():
            if (evaluation_results[source]['is_valid'] == True) & (key in evaluation_results[source].keys()):
                timestamps_of_valid_sources[source] = evaluation_results[source]['last_updated_on']
        if len(timestamps_of_valid_sources.keys()) > 0:
            key_of_most_recently_updated_valid_source = max(timestamps_of_valid_sources, key=timestamps_of_valid_sources.get)
            result = evaluation_results[key_of_most_recently_updated_valid_source][key]
        else:
            result = None
        return result
    
    
    def _check_if_all_information_are_present(self, unified_results: dict) -> bool:
        return all([unified_results[key] != None for key in ['UNIQUE_ENV_NAME', 'PYTHON_VERSION', 'PIP_PACKAGES']])
    
    
    
class ZenodoRepoValidator(RemoteRepoValidator):
    
    
    def _assert_repo_url_is_valid(self, repo_url: str) -> None:
        raise NotImplementedError('The ZenodoRepoValidator has not been implemented yet.')
        
    
    def _validate_repo_content(self, repo_url: str) -> dict:
        raise NotImplementedError('The ZenodoRepoValidator has not been implemented yet.')

    
    
    
class RemoteRepoValidatorFactory:
    
    @property
    def _available_remote_repo_validators(self) -> dict[str, RemoteRepoValidator]:
        available_validators = {
            'https://github.com': GitHubRepoValidator(), 
            'https://zenodo.org': ZenodoRepoValidator()
        }
        return available_validators

    
    def get_remote_repo_validator(self, repo_url: str) -> Union[RemoteRepoValidator, None]:
        matching_validator = None
        for domain_keyword, remote_repo_validator in self._available_remote_repo_validators.items():
            if repo_url.startswith(domain_keyword):
                matching_validator = remote_repo_validator
                break
        return matching_validator