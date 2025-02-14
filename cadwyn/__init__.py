import importlib.metadata

from .applications import Cadwyn
from .changelogs import hidden
from .route_generation import VersionedAPIRouter, generate_versioned_routers
from .schema_generation import generate_versioned_models, migrate_response_body
from .structure import (
    HeadVersion,
    RequestInfo,
    ResponseInfo,
    Version,
    VersionBundle,
    VersionChange,
    VersionChangeWithSideEffects,
    convert_request_to_next_version_for,
    convert_response_to_previous_version_for,
    endpoint,
    enum,
    schema,
)

__version__ = importlib.metadata.version("cadwyn_version")
__all__ = [
    "Cadwyn",
    "HeadVersion",
    "RequestInfo",
    "ResponseInfo",
    "Version",
    "VersionBundle",
    "VersionChange",
    "VersionChangeWithSideEffects",
    "VersionedAPIRouter",
    "convert_request_to_next_version_for",
    "convert_response_to_previous_version_for",
    "endpoint",
    "enum",
    "generate_versioned_models",
    "generate_versioned_routers",
    "hidden",
    "migrate_response_body",
    "schema",
]
