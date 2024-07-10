from fastapi.routing import APIRoute
from fastapi.openapi.models import APIKey
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List, Dict, Any
from pydantic import BaseModel
import logging
import json



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



def get_request_body_example(route: APIRoute) -> Dict[str, Any]:
    """
    Get the example request body for a given route.

    Args:
        route (APIRoute): The route to get the request body example for.

    Returns:
        Dict[str, Any]: The example request body.
    """
    if route.body_field:
        if issubclass(route.body_field.type_, BaseModel):
            example = route.body_field.type_.model_json_schema().get('example', {})
            return example
        elif isinstance(route.body_field.type_, dict):
            return route.body_field.type_
    return {}



def get_headers(route: APIRoute) -> List[Dict[str, str]]:
    """
    Get the headers required for a given route.

    Args:
        route (APIRoute): The route to get the headers for.

    Returns:
        List[Dict[str, str]]: The list of headers.
    """
    headers = []
    for dependency in route.dependant.dependencies:
        if isinstance(dependency.security_scopes, (APIKey, OAuth2PasswordBearer, OAuth2PasswordRequestForm)):
            headers.append({
                "key": "Authorization",
                "value": "Bearer {{access_token}}"
            })
    return headers



def get_parameters(route: APIRoute) -> List[Dict[str, Any]]:
    """
    Get the parameters for a given route.

    Args:
        route (APIRoute): The route to get the parameters for.

    Returns:
        List[Dict[str, Any]]: The list of parameters.
    """
    parameters = []
    for param in route.dependant.query_params:
        parameters.append({
            "name": param.name,
            "in": "query",
            "required": param.required,
            "schema": param.field_info.json_schema_extra() if param.field_info else {}
        })
    for param in route.dependant.path_params:
        parameters.append({
            "name": param.name,
            "in": "path",
            "required": True,
            "schema": param.field_info.json_schema_extra() if param.field_info else {}
        })
    return parameters



def get_responses(route: APIRoute) -> Dict[str, Dict[str, Any]]:
    """
    Get the responses for a given route.

    Args:
        route (APIRoute): The route to get the responses for.

    Returns:
        Dict[str, Dict[str, Any]]: The dictionary of responses.
    """
    responses = {}
    if route.response_model:
        if isinstance(route.response_model, dict):
            for status_code, response in route.response_model.items():
                responses[status_code] = {
                    "description": response.description,
                    "content": {
                        "application/json": {
                            "schema": response.model_json_schema()
                        }
                    }
                }
        else:
            responses["default"] = {
                "description": "Default response",
                "content": {
                    "application/json": {
                        "schema": route.response_model.model_json_schema()
                    }
                }
            }
    return responses