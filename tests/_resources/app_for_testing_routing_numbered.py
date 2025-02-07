from fastapi import APIRouter
from starlette.responses import JSONResponse, Response

from cadwyn import Cadwyn
from cadwyn.structure.common import PydanticVersionType
from cadwyn.structure.versions import Version, VersionBundle
from packaging import version

router = APIRouter(prefix="/v1")


@router.get("/")
def homepage():
    return Response("Hello, world", media_type="text/plain")


@router.get("/users/{username}/{page}")
def users_api(username: str, page: int):
    return JSONResponse(
        {"users": [{"username": username, "page": page}]},
    )


@router.get("/users")
def users():
    return Response("All users", media_type="text/plain")


@router.get("/doggies/{dogname}")
def doggies_api(dogname: str):
    return JSONResponse({"doggies": [{"dogname": dogname}]})


versions = [
    "1.0.0",
    "1.1.1",
    "1.1.2",
    "2.1.0",
    "3.1.1",
    "1.1.3",
]
mixed_hosts_app_numbered = Cadwyn(versions=VersionBundle(Version("2.0")), version_type=PydanticVersionType)
for version in versions:
    mixed_hosts_app_numbered.add_header_versioned_routers(
        router,
        header_value=version,
    )
