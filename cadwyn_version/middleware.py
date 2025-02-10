import datetime
import inspect
from contextlib import AsyncExitStack
from contextvars import ContextVar
from datetime import date
from typing import Annotated, Any, cast, Generic

from fastapi import Header, Request, Response
from fastapi._compat import _normalize_errors
from fastapi.dependencies.utils import get_dependant, solve_dependencies
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, DispatchFunction, RequestResponseEndpoint
from starlette.types import ASGIApp

from cadwyn.structure.common import VersionTypeVar
from cadwyn.structure.versions import version_to_str

def _get_api_version_dependency(api_version_header_name: str, version_example: str, version_type: type):
    def api_version_dependency(**kwargs: Any):
        return next(iter(kwargs.values()))

    api_version_dependency.__signature__ = inspect.Signature(
        parameters=[
            inspect.Parameter(
                api_version_header_name.replace("-", "_"),
                inspect.Parameter.KEYWORD_ONLY,
                annotation=Annotated[version_type, Header(examples=[version_example])],
                default=version_example,
            ),
        ],
    )
    return api_version_dependency


class HeaderVersioningMiddleware(BaseHTTPMiddleware, Generic[VersionTypeVar]):
    def __init__(
        self,
        app: ASGIApp,
        *,
        api_version_header_name: str,
        api_version_var: ContextVar[VersionTypeVar] | ContextVar[VersionTypeVar | None],
        default_response_class: type[Response] = JSONResponse,
        dispatch: DispatchFunction | None = None,
        version_type: type = datetime.date,
        version_example: str = "2000-08-23"
    ) -> None:
        super().__init__(app, dispatch)
        self.api_version_header_name = api_version_header_name
        self.api_version_var = api_version_var
        self.default_response_class = default_response_class
        # We use the dependant to apply fastapi's validation to the header, making validation at middleware level
        # consistent with validation and route level.
        self.version_type = version_type
        self.version_header_validation_dependant = get_dependant(
            path="",
            call=_get_api_version_dependency(api_version_header_name, version_example, self.version_type),
        )

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ):
        # We handle api version at middleware level because if we try to add a Dependency to all routes, it won't work:
        # we use this header for routing so the user will simply get a 404 if the header is invalid.
        api_version: VersionTypeVar | None = None
        if self.api_version_header_name in request.headers:
            async with AsyncExitStack() as async_exit_stack:
                solved_result = await solve_dependencies(
                    request=request,
                    dependant=self.version_header_validation_dependant,
                    async_exit_stack=async_exit_stack,
                    embed_body_fields=False,
                )
                if solved_result.errors:
                    return self.default_response_class(status_code=422, content=_normalize_errors(solved_result.errors))
                api_version = cast(self.version_type, solved_result.values[self.api_version_header_name.replace("-", "_")])
                self.api_version_var.set(api_version)

        response = await call_next(request)

        if api_version is not None:
            # We return it because we will be returning the **matched** version, not the requested one.
            response.headers[self.api_version_header_name] = version_to_str(api_version)

        return response
