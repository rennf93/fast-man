import json
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fast_man.converter import generate_postman_collection



@pytest.fixture
def app():
    app = FastAPI()

    @app.get("/items/{item_id}", summary="Get an item")
    async def read_item(item_id: int):
        return {"item_id": item_id}

    @app.post("/items/", summary="Create an item")
    async def create_item(item: dict):
        return item

    return app



@pytest.fixture
def client(app):
    return TestClient(app)



def test_generate_postman_collection(app, client, tmp_path):
    output_file = tmp_path / "postman_collection.json"
    generate_postman_collection(app, str(output_file), "Test API", "http://testserver")

    with open(output_file) as f:
        collection = json.load(f)

    assert collection["info"]["name"] == "Test API"
    assert collection["info"]["schema"] == "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    print(f"collection: {collection}")
    assert "item" in collection
    assert len(collection["item"]) == 2

    get_item = collection["item"][0]
    assert get_item["name"] == "read_item"
    assert get_item["request"]["url"] == "http://testserver/items/{item_id}"
    assert get_item["request"]["method"] == "GET"
    assert get_item["request"]["description"] == "Get an item"

    create_item = collection["item"][1]
    assert create_item["name"] == "create_item"
    assert create_item["request"]["url"] == "http://testserver/items/"
    assert create_item["request"]["method"] == "POST"
    assert create_item["request"]["description"] == "Create an item"
    assert create_item["request"]["body"]["mode"] == "raw"
    assert json.loads(create_item["request"]["body"]["raw"]) == {}

    # Test the endpoints using TestClient
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json() == {"item_id": 1}

    response = client.post("/items/", json={"name": "test"})
    assert response.status_code == 200
    assert response.json() == {"name": "test"}



def test_generate_postman_collection_with_auth(app, client, tmp_path):
    output_file = tmp_path / "postman_collection_with_auth.json"
    generate_postman_collection(app, str(output_file), "Test API with Auth", "http://testserver")

    with open(output_file) as f:
        collection = json.load(f)

    assert collection["auth"]["type"] == "bearer"
    assert collection["auth"]["bearer"][0]["key"] == "token"
    assert collection["auth"]["bearer"][0]["value"] == "{{access_token}}"
    assert collection["auth"]["bearer"][0]["type"] == "string"

    # Test the endpoints using TestClient
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json() == {"item_id": 1}

    response = client.post("/items/", json={"name": "test"})
    assert response.status_code == 200
    assert response.json() == {"name": "test"}
