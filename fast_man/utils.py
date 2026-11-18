from fastapi.routing import APIRoute
from fastapi.security.base import SecurityBase
from typing import List, Dict, Any
from pydantic import BaseModel
from pydantic_core import PydanticUndefined
import logging
import traceback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _default_of(param: Any) -> Any:
    default = param.field_info.default
    return None if default is PydanticUndefined else default


def get_request_body_example(route: APIRoute) -> Dict[str, Any]:
    """
    Get the example request body for a given route.

    Args:
        route (APIRoute): The route to get the request body example for.

    Returns:
        Dict[str, Any]: The example request body.
    """
    try:
        if route.body_field:
            body_type = route.body_field.field_info.annotation
            if issubclass(body_type, BaseModel):
                if route.body_field.field_info.examples:
                    example = next(
                        iter(route.body_field.field_info.examples.values())
                    ).get("value", {})
                else:
                    example = body_type.model_json_schema().get(
                        "example", {}
                    )
                return example
            elif isinstance(body_type, dict):
                return body_type
            elif isinstance(body_type, list):
                return [body_type[0].model_json_schema()]
        return {}
    except Exception as e:
        logger.error(
            f"Error in get_request_body_example: {e}\n{traceback.format_exc()}"
        )
        return {}


def get_headers(route: APIRoute) -> List[Dict[str, str]]:
    """
    Get the headers required for a given route.

    Args:
        route (APIRoute): The route to get the headers for.

    Returns:
        List[Dict[str, str]]: The list of headers.
    """
    try:
        headers = []
        for dependency in route.dependant.dependencies:
            if isinstance(dependency.call, SecurityBase):
                headers.append(
                    {
                        "key": "Authorization",
                        "value": "Bearer {{access_token}}",
                    }
                )
        for param in route.dependant.header_params:
            headers.append(
                {
                    "key": param.name,
                    "value": f"{{{{{param.name}}}}}",
                }
            )
        return headers
    except Exception as e:
        logger.error(
            f"Error in get_headers: {e}\n{traceback.format_exc()}"
        )
        return []


def get_parameters(route: APIRoute) -> List[Dict[str, Any]]:
    """
    Get the parameters for a given route.

    Args:
        route (APIRoute):
        The route to get the parameters for.

    Returns:
        List[Dict[str, Any]]:
        The list of parameters.
    """
    try:
        parameters = []
        for param in route.dependant.query_params:
            parameters.append(
                {
                    "name": param.name,
                    "in": "query",
                    "required": param.field_info.is_required(),
                    "schema": {
                        "type": (
                            param.field_info.annotation.__name__
                            if hasattr(
                                param.field_info.annotation,
                                "__name__"
                            )
                            else str(param.field_info.annotation)
                        ),
                        "description": (
                            param.field_info.description
                            if param.field_info.description
                            else ""
                        ),
                        "default": (
                            _default_of(param)
                            if _default_of(param) is not None
                            else ""
                        ),
                        "example": (
                            param.field_info.extra.get(
                                "example", ""
                            )
                            if hasattr(
                                param.field_info,
                                "extra"
                            )
                            else ""
                        ),
                    },
                }
            )
        for param in route.dependant.path_params:
            parameters.append(
                {
                    "name": param.name,
                    "in": "path",
                    "required": True,
                    "schema": {
                        "type": (
                            param.field_info.annotation.__name__
                            if hasattr(
                                param.field_info.annotation,
                                "__name__"
                            )
                            else str(param.field_info.annotation)
                        ),
                        "description": (
                            param.field_info.description
                            if param.field_info.description
                            else ""
                        ),
                        "default": _default_of(param),
                        "example": (
                            param.field_info.extra.get(
                                "example",
                                ""
                            )
                            if hasattr(
                                param.field_info,
                                "extra"
                            )
                            else ""
                        ),
                    },
                }
            )
        return parameters
    except Exception as e:
        logger.error(
            f"Error in get_parameters: {e}\n{traceback.format_exc()}"
        )
        return []


def get_responses(route: APIRoute) -> Dict[str, Dict[str, Any]]:
    """
    Get the responses for a given route.

    Args:
        route (APIRoute): The route to get the responses for.

    Returns:
        Dict[str, Dict[str, Any]]: The dictionary of responses.
    """
    try:
        responses = {}
        if route.responses:
            for status_code, response in route.responses.items():
                if isinstance(response, dict):
                    content = (
                        response.get("content", {})
                        .get("application/json", {})
                        .get("schema", {})
                    )
                    if not content and "model" in response:
                        content = response["model"].model_json_schema()
                    responses[str(status_code)] = {
                        "description": response.get(
                            "description",
                            ""
                        ),
                        "content": {
                            "application/json": {
                                "schema": content
                            }
                        },
                    }
                elif isinstance(response, BaseModel):
                    responses[str(status_code)] = {
                        "description": response.__doc__,
                        "content": {
                            "application/json": {
                                "schema": response.model_json_schema()
                            }
                        },
                    }
        elif route.response_model:
            if isinstance(route.response_model, list):
                schema = [
                    model.model_json_schema()
                    for model in route.response_model
                ]
            else:
                schema = route.response_model.model_json_schema()
            responses[str(route.status_code)] = {
                "description": route.response_model.__doc__,
                "content": {
                    "application/json": {
                        "schema": schema
                    }
                },
            }
        return responses
    except Exception as e:
        logger.error(
            f"Error in get_responses: {e}\n{traceback.format_exc()}"
        )
        return {}
