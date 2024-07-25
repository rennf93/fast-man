import json
from fastapi import (
    Body,
    Cookie,
    Depends,
    FastAPI,
    Header,
    HTTPException,
    Path,
    Query,
    Security,
    status,
)
from fastapi.security import (
    APIKeyHeader,
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
)
from fastapi.testclient import TestClient
from fast_man.converter import generate_postman_collection
from pydantic import BaseModel, Field
import pytest
from typing import Optional

# Security schemes
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token"
)
api_key_scheme = APIKeyHeader(
    name="X-API-Key"
)


# Models
class Item(BaseModel):
    name: str = Field(
        ...,
        json_schema_extra="Item name"
    )
    description: Optional[str] = Field(
        None,
        json_schema_extra="Item description"
    )


class ResponseItem(BaseModel):
    name: str = Field(
        ...,
        json_schema_extra="Item name"
    )
    description: Optional[str] = Field(
        None,
        json_schema_extra="Item description"
    )
    id: int = Field(
        ...,
        json_schema_extra=1
    )


class ErrorResponse(BaseModel):
    detail: str = Field(
        ...,
        json_schema_extra="Error detail"
    )


class User(BaseModel):
    username: str = Field(
        ...,
        json_schema_extra="john"
    )
    email: str = Field(
        ...,
        json_schema_extra="john@example.com"
    )


class Token(BaseModel):
    access_token: str = Field(
        ...,
        json_schema_extra="fake-token"
    )
    token_type: str = Field(
        ...,
        json_schema_extra="bearer"
    )


class SecureData(BaseModel):
    data: str = Field(
        ...,
        json_schema_extra="This is secure data"
    )


# Dependencies
def get_current_user(
    token: str = Depends(oauth2_scheme)
) -> User:
    if token == "fake-token":
        return User(
            username="john",
            email="john@example.com"
        )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        response_model=ErrorResponse,
    )


def get_api_key(
    api_key: str = Security(api_key_scheme)
) -> str:
    if api_key == "fake-api-key":
        return api_key
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid API Key",
        response_model=ErrorResponse,
    )


@pytest.fixture
def app():
    app = FastAPI()

    @app.get(
        path="/items/{item_id}",
        summary="Get an item",
        response_model=ResponseItem,
        status_code=status.HTTP_200_OK,
        tags=["Items"],
        responses={
            status.HTTP_200_OK: {
                "description": "Successful Response",
                "model": ResponseItem,
            },
            status.HTTP_404_NOT_FOUND: {
                "description": "Item not found",
                "model": ErrorResponse,
            },
        },
    )
    async def read_item(
        item_id: int = Path(
            ...,
            description="The ID of the item to retrieve"
        ),
        q: Optional[str] = Query(
            None,
            description="Query string for the item"
        ),
        user_agent: Optional[str] = Header(
            None,
            description="User-Agent header"
        ),
        cookie_id: Optional[str] = Cookie(
            None,
            description="Cookie ID"
        ),
    ) -> ResponseItem:
        if item_id == 1:
            return ResponseItem(
                id=item_id,
                name="Item name",
                description="Item description"
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
            response_model=ErrorResponse,
        )

    @app.post(
        path="/items/",
        summary="Create an item",
        response_model=ResponseItem,
        status_code=status.HTTP_201_CREATED,
        tags=["Items"],
        responses={
            status.HTTP_201_CREATED: {
                "description": "Successful Response",
                "model": ResponseItem,
            },
            status.HTTP_401_UNAUTHORIZED: {
                "description": "Unauthorized",
                "model": ErrorResponse,
            },
        },
    )
    async def create_item(
        item: Item = Body(
            ...,
            examples={
                "default": {
                    "summary": "An example item",
                    "value": {
                        "name": "Example item",
                        "description": "Example description",
                    },
                }
            },
        ),
        authorization: Optional[str] = Header(
            None,
            description="Authorization token"
        ),
    ) -> ResponseItem:
        if authorization != "Bearer test-token":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized",
                response_model=ErrorResponse,
            )
        return ResponseItem(
            id=1, **item.model_dump()
        )

    @app.post(
        path="/token",
        summary="Get a token",
        response_model=Token,
        status_code=status.HTTP_200_OK,
        tags=["Auth"],
        responses={
            status.HTTP_200_OK: {
                "description": "Successful Response",
                "model": Token,
            },
            status.HTTP_400_BAD_REQUEST: {
                "description": "Invalid credentials",
                "model": ErrorResponse,
            },
        },
    )
    async def login(
        form_data: OAuth2PasswordRequestForm = Depends()
    ) -> Token:
        if form_data.username == "john" and form_data.password == "secret":
            return Token(
                access_token="fake-token",
                token_type="bearer",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credentials",
            response_model=ErrorResponse,
        )

    @app.get(
        path="/users/me",
        summary="Get current user",
        response_model=User,
        status_code=status.HTTP_200_OK,
        tags=["Users"],
        dependencies=[
            Depends(
                get_current_user
            )
        ],
        responses={
            status.HTTP_200_OK: {
                "description": "Successful Response",
                "model": User,
            },
            status.HTTP_401_UNAUTHORIZED: {
                "description": "Unauthorized",
                "model": ErrorResponse,
            },
        },
    )
    async def read_users_me(
        current_user: User = Depends(
            get_current_user
        )
    ) -> User:
        return current_user

    @app.get(
        path="/secure-data",
        summary="Get secure data",
        response_model=SecureData,
        status_code=status.HTTP_200_OK,
        tags=["Secure"],
        dependencies=[
            Security(
                get_api_key
            )
        ],
        responses={
            status.HTTP_200_OK: {
                "description": "Successful Response",
                "model": SecureData,
            },
            status.HTTP_403_FORBIDDEN: {
                "description": "Forbidden",
                "model": ErrorResponse,
            },
        },
    )
    async def get_secure_data(
        api_key: str = Security(
            get_api_key
        )
    ) -> SecureData:
        return SecureData(
            data="This is secure data"
        )

    return app


@pytest.fixture
def client(app):
    return TestClient(app)


def test_generate_postman_collection(
    app,
    client
):
    output_file = "postman_collection.json"
    generate_postman_collection(
        app,
        str(output_file),
        "Test API",
        "http://testserver"
    )

    with open(output_file) as f:
        collection = json.load(f)

    schema = (
        "https://schema.getpostman.com/json/collection/v2.1.0/"
        "collection.json"
    )

    assert collection["info"]["name"] == "Test API"
    assert collection["info"]["schema"] == schema
    assert "item" in collection
    assert len(collection["item"]) > 0

    folder_names = [
        folder["name"]
        for folder in collection["item"]
    ]
    assert "Items" in folder_names
    assert "Auth" in folder_names
    assert "Users" in folder_names
    assert "Secure" in folder_names

    items_folder = next(
        folder
        for folder in collection["item"]
        if folder["name"] == "Items"
    )
    assert len(items_folder["item"]) == 2

    url = "http://testserver/items/{item_id}"

    get_item = items_folder["item"][0]
    assert get_item["name"] == "read_item"
    assert get_item["request"]["url"] == url
    assert get_item["request"]["method"] == "GET"
    assert get_item["request"]["description"] == "Get an item"
    assert get_item["request"]["header"] == [
        {
            "key": "user_agent",
            "value": "{{user_agent}}",
        }
    ]
    assert get_item["request"]["body"]["mode"] == "raw"
    assert get_item["request"]["body"]["raw"] == {}
    assert sorted(
        get_item["request"]["params"],
        key=lambda x: x["name"]
    ) == sorted(
        [
            {
                "name": "item_id",
                "in": "path",
                "required": True,
                "schema": {
                    "type": "int",
                    "description": "The ID of the item to retrieve",
                    "default": None,
                    "example": "",
                },
            },
            {
                "name": "q",
                "in": "query",
                "required": False,
                "schema": {
                    "type": "Optional",
                    "description": "Query string for the item",
                    "default": "",
                    "example": "",
                },
            },
        ],
        key=lambda x: x["name"],
    )
    assert get_item["request"]["responses"] == {
        "200": {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "description": {
                                "anyOf": [
                                    {
                                        "type": "string",
                                    },
                                    {
                                        "type": "null",
                                    },
                                ],
                                "default": None,
                                "title": "Description",
                            },
                            "id": {
                                "title": "Id",
                                "type": "integer"
                            },
                            "name": {
                                "title": "Name",
                                "type": "string",
                            },
                        },
                        "required": [
                            "name",
                            "id"
                        ],
                        "title": "ResponseItem",
                    }
                }
            },
        },
        "404": {
            "description": "Item not found",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "detail": {
                                "title": "Detail",
                                "type": "string",
                            }
                        },
                        "required": ["detail"],
                        "title": "ErrorResponse",
                    }
                }
            },
        },
    }

    url = "http://testserver/items/"

    create_item = items_folder["item"][1]
    assert create_item["name"] == "create_item"
    assert create_item["request"]["url"] == url
    assert create_item["request"]["method"] == "POST"
    assert create_item["request"]["description"] == "Create an item"
    assert create_item["request"]["header"] == [
        {
            "key": "authorization",
            "value": "{{authorization}}",
        }
    ]
    assert create_item["request"]["body"]["mode"] == "raw"
    assert create_item["request"]["body"]["raw"] == {
        "name": "Example item",
        "description": "Example description",
    }
    assert create_item["request"]["params"] == []
    assert create_item["request"]["responses"] == {
        "201": {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "description": {
                                "anyOf": [
                                    {
                                        "type": "string",
                                    },
                                    {
                                        "type": "null",
                                    },
                                ],
                                "default": None,
                                "title": "Description",
                            },
                            "id": {
                                "title": "Id",
                                "type": "integer",
                            },
                            "name": {
                                "title": "Name",
                                "type": "string",
                            },
                        },
                        "required": [
                            "name",
                            "id"
                        ],
                        "title": "ResponseItem",
                    }
                }
            },
        },
        "401": {
            "description": "Unauthorized",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "detail": {
                                "title": "Detail",
                                "type": "string",
                            }
                        },
                        "required": ["detail"],
                        "title": "ErrorResponse",
                    }
                }
            },
        },
    }

    response = client.get(
        "/items/1",
        headers={
            "user_agent": "test-agent"
        },
        params={
            "q": "test-query"
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "name": "Item name",
        "description": "Item description",
    }

    response = client.post(
        "/items/",
        json={
            "name": "test",
            "description": "test description"
        },
        headers={
            "authorization": "Bearer test-token",
        },
    )
    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "name": "test",
        "description": "test description",
    }


def test_generate_postman_collection_with_auth(
    app,
    client
):
    output_file = "postman_collection_with_auth.json"
    generate_postman_collection(
        app,
        str(output_file),
        "Test API with Auth",
        "http://testserver"
    )

    with open(output_file) as f:
        collection = json.load(f)

    assert collection["auth"]["type"] == "bearer"
    assert collection["auth"]["bearer"][0]["key"] == "token"
    assert collection["auth"]["bearer"][0]["value"] == "{{access_token}}"
    assert collection["auth"]["bearer"][0]["type"] == "string"

    folder_names = [
        folder["name"]
        for folder in collection["item"]
    ]
    assert "Items" in folder_names
    assert "Auth" in folder_names
    assert "Users" in folder_names
    assert "Secure" in folder_names

    items_folder = next(
        folder
        for folder in collection["item"]
        if folder["name"] == "Items"
    )
    assert len(items_folder["item"]) == 2

    get_item = items_folder["item"][0]
    assert sorted(
        get_item["request"]["params"],
        key=lambda x: x["name"],
    ) == sorted(
        [
            {
                "name": "item_id",
                "in": "path",
                "required": True,
                "schema": {
                    "type": "int",
                    "description": "The ID of the item to retrieve",
                    "default": None,
                    "example": "",
                },
            },
            {
                "name": "q",
                "in": "query",
                "required": False,
                "schema": {
                    "type": "Optional",
                    "description": "Query string for the item",
                    "default": "",
                    "example": "",
                },
            },
        ],
        key=lambda x: x["name"],
    )

    response = client.get(
        "/items/1",
        headers={
            "Authorization": "Bearer test-token"
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "name": "Item name",
        "description": "Item description",
    }

    response = client.post(
        "/items/",
        json={
            "name": "test",
            "description": "test description",
        },
        headers={
            "Authorization": "Bearer test-token",
        },
    )
    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "name": "test",
        "description": "test description",
    }
