from cactus.components.repo.validators import RepoValidator
from cactus.components.repo.validators import get_repo_validator
from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import JSONResponse

router = APIRouter(prefix='/repos', tags=['Repos'])


@router.get('/validate/{repo_url:path}', summary='Validate repo dependencies.')
def validate_repo(
    repo_url: str,
    repo_validator: RepoValidator = Depends(get_repo_validator),
):
    """Validate that the repo includes all the required dependency information for the setup."""

    if repo_validator.is_repo_valid(repo_url):
        return JSONResponse(status_code=200, content={'message': 'Valid'})

    return JSONResponse(status_code=400, content={'message': 'Invalid'})
