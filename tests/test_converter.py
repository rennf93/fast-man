import json
import pytest
from fastapi import FastAPI, Header, Query, status, Body, Request
from fastapi.testclient import TestClient
from pydantic import BaseModel
from fast_man.converter import generate_postman_collection



class Item(BaseModel):
    name: str
    description: str = None


class ResponseItem(BaseModel):
    name: str
    description: str = None
    id: int



@pytest.fixture
def app():
    app = FastAPI()

    @app.get(
        "/items/{item_id}",
        summary="Get an item",
        response_model=ResponseItem,
        status_code=status.HTTP_200_OK
    )
    async def read_item(
        item_id: int,
        q: str = Query(None, description="Query string for the item"),
        user_agent: str = Header(None, description="User-Agent header")
    ):
        return {"id": item_id, "name": "Item name", "description": "Item description"}

    @app.post(
        "/items/",
        summary="Create an item",
        response_model=ResponseItem,
        status_code=status.HTTP_201_CREATED
    )
    async def create_item(
        # request: Request,
        item: Item = Body(..., examples={"default": {"summary": "An example item", "value": {"name": "Example item", "description": "Example description"}}}),
        token: str = Header(None, description="Authorization token")
    ):
        return {"id": 1, **item.model_dump()}

    return app



@pytest.fixture
def client(app):
    return TestClient(app)



def test_generate_postman_collection(app, client):
    output_file = "postman_collection.json"
    generate_postman_collection(app, str(output_file), "Test API", "http://testserver")

    with open(output_file) as f:
        collection = json.load(f)

    assert collection["info"]["name"] == "Test API"
    assert collection["info"]["schema"] == "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    assert "item" in collection
    assert len(collection["item"]) == 2

    get_item = collection["item"][0]
    assert get_item["name"] == "read_item"
    assert get_item["request"]["url"] == "http://testserver/items/{item_id}"
    assert get_item["request"]["method"] == "GET"
    assert get_item["request"]["description"] == "Get an item"
    assert get_item["request"]["header"] == [{"key": "user_agent", "value": "{{user_agent}}"}]
    assert get_item["request"]["body"]["mode"] == "raw"
    assert json.loads(get_item["request"]["body"]["raw"]) == {}
    assert sorted(get_item["request"]["params"], key=lambda x: x["name"]) == sorted([
        {"name": "item_id", "in": "path", "required": True, "schema": {}},
        {"name": "q", "in": "query", "required": False, "schema": {}}
    ], key=lambda x: x["name"])
    assert get_item["request"]["responses"] == {
        "200": {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "description": {"default": None, "title": "Description", "type": "string"},
                            "id": {"title": "Id", "type": "integer"},
                            "name": {"title": "Name", "type": "string"},
                        },
                        "required": ["name", "id"],
                        "title": "ResponseItem"
                    }
                }
            }
        }
    }

    create_item = collection["item"][1]
    assert create_item["name"] == "create_item"
    assert create_item["request"]["url"] == "http://testserver/items/"
    assert create_item["request"]["method"] == "POST"
    assert create_item["request"]["description"] == "Create an item"
    assert create_item["request"]["header"] == [{"key": "token", "value": "{{token}}"}]
    assert create_item["request"]["body"]["mode"] == "raw"
    assert json.loads(create_item["request"]["body"]["raw"]) == {"name": "Example item", "description": "Example description"}
    assert create_item["request"]["params"] == []
    assert create_item["request"]["responses"] == {
        "201": {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "description": {"default": None, "title": "Description", "type": "string"},
                            "id": {"title": "Id", "type": "integer"},
                            "name": {"title": "Name", "type": "string"},
                        },
                        "required": ["name", "id"],
                        "title": "ResponseItem"
                    }
                }
            }
        }
    }

    # Test the endpoints using TestClient
    response = client.get("/items/1", headers={"user-agent": "test-agent"}, params={"q": "test-query"})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "Item name", "description": "Item description"}

    response = client.post("/items/", json={"name": "test", "description": "test description"})
    assert response.status_code == 201
    assert response.json() == {"id": 1, "name": "test", "description": "test description"}



def test_generate_postman_collection_with_auth(app, client):
    output_file = "postman_collection_with_auth.json"
    generate_postman_collection(app, str(output_file), "Test API with Auth", "http://testserver")

    with open(output_file) as f:
        collection = json.load(f)

    assert collection["auth"]["type"] == "bearer"
    assert collection["auth"]["bearer"][0]["key"] == "token"
    assert collection["auth"]["bearer"][0]["value"] == "{{access_token}}"
    assert collection["auth"]["bearer"][0]["type"] == "string"

    # Test the endpoints using TestClient
    response = client.get("/items/1", headers={"Authorization": "Bearer test-token"})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "Item name", "description": "Item description"}

    response = client.post("/items/", json={"name": "test", "description": "test description"}, headers={"Authorization": "Bearer test-token"})
    assert response.status_code == 201
    assert response.json() == {"id": 1, "name": "test", "description": "test description"}