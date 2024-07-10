import json
import logging
from fastapi import FastAPI
from fastapi.routing import APIRoute
from .utils import get_request_body_example, get_headers, get_parameters, get_responses
from typing import Any, Dict



# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



def generate_postman_collection(
    app: FastAPI,
    output_file: str = 'output.json',
    input_name: str = 'API Collection',
    input_host: str = 'http://localhost'
) -> None:
    """
    Generate a Postman collection from a FastAPI app.

    Args:
        app (FastAPI): The FastAPI app instance.
        output_file (str): The output file name for the Postman collection.
        input_name (str): The name of the Postman collection.
        input_host (str): The host URL for the API.
    """
    collection: Dict[str, Any] = {
        "info": {
            "name": input_name,
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": [],
        "auth": {
            "type": "bearer",
            "bearer": [
                {
                    "key": "token",
                    "value": "{{access_token}}",
                    "type": "string"
                }
            ]
        }
    }

    for route in app.routes:
        if isinstance(route, APIRoute):
            try:
                item = {
                    "name": route.name,
                    "request": {
                        "url": f"{input_host}{route.path}",
                        "method": route.methods.pop(),
                        # "method": list(route.methods)[0],
                        "description": route.summary or "",
                        "header": get_headers(route),
                        "body": {
                            "mode": "raw",
                            "raw": json.dumps(get_request_body_example(route), indent=4)
                        },
                        "params": get_parameters(route),
                        "responses": get_responses(route)
                    }
                }
                collection["item"].append(item)
            except Exception as e:
                logger.error(f"Error processing route {route.name}: {e}")

    try:
        with open(output_file, 'w') as f:
            json.dump(collection, f, indent=4)
        logger.info(f"Postman collection saved to {output_file}")
    except Exception as e:
        logger.error(f"Error saving Postman collection to {output_file}: {e}")



def main() -> None:
    """
    Main function to parse arguments and generate the Postman collection.
    """
    import argparse
    parser = argparse.ArgumentParser(description='Generate Postman collection from FastAPI app.')
    parser.add_argument('--app', required=True, help='Path to FastAPI app instance')
    parser.add_argument('--output', default='output.json', help='Output file name')
    parser.add_argument('--name', default='API Collection', help='Name of the Postman collection')
    parser.add_argument('--host', default='http://localhost', help='Host URL for the API')
    args = parser.parse_args()

    try:
        app_module = __import__(args.app)
        app = getattr(app_module, 'app')
        generate_postman_collection(app, args.output, args.name, args.host)
    except Exception as e:
        logger.error(f"Error importing FastAPI app from {args.app}: {e}")



if __name__ == '__main__':
    main()