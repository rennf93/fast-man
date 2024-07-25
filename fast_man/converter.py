import json
import logging
from fastapi import FastAPI
from fastapi.routing import APIRoute
from .utils import (
    get_request_body_example,
    get_headers,
    get_parameters,
    get_responses,
)
from typing import Any, Dict
from fastapi.encoders import jsonable_encoder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_postman_collection(
    app: FastAPI,
    output_file: str = "postman_collection.json",
    input_name: str = "API Collection",
    input_host: str = "http://localhost",
    readme_file: str = "README.md",
) -> None:
    """
    Generate a Postman collection from a FastAPI app.

    Args:
        app (FastAPI):
            The FastAPI app instance.
        output_file (str):
            The output file name for the Postman collection.
        input_name (str):
            The name of the Postman collection.
        input_host (str):
            The host URL for the API.
        readme_file (str):
            The path to the README.md file for documentation.
    """
    try:
        with open(readme_file, "r") as f:
            readme_content = f.read()
    except Exception as e:
        logger.error(
            f"Error reading README.md file: {e}"
        )
        readme_content = ""

    collection: Dict[str, Any] = {
        "info": {
            "name": input_name,
            "schema": (
                "https://schema.getpostman.com/json/collection/v2.1.0/"
                "collection.json"
            ),
            "description": readme_content,
        },
        "item": [],
        "auth": {
            "type": "bearer",
            "bearer": [
                {
                    "key": "token",
                    "value": "{{access_token}}",
                    "type": "string",
                }
            ],
        },
    }

    folders = {}

    for route in app.routes:
        if isinstance(route, APIRoute):
            try:
                item = {
                    "name": route.name,
                    "request": {
                        "url": f"{input_host}{route.path}",
                        "method": route.methods.pop(),
                        "description": route.summary or "",
                        "header": get_headers(
                            route
                        ),
                        "body": {
                            "mode": "raw",
                            "raw": jsonable_encoder(
                                get_request_body_example(
                                    route
                                )
                            ),
                        },
                        "params": jsonable_encoder(
                            get_parameters(
                                route
                            )
                        ),
                        "responses": jsonable_encoder(
                            get_responses(
                                route
                            )
                        ),
                    },
                }
                for tag in route.tags:
                    if tag not in folders:
                        folders[tag] = {"name": tag, "item": []}
                    folders[tag]["item"].append(item)
            except Exception as e:
                logger.error(
                    f"Error processing route {route}: {e}"
                )

    collection["item"] = list(folders.values())

    try:
        with open(output_file, "w") as f:
            json.dump(collection, f, indent=4)
        logger.info(
            f"Postman collection saved to {output_file}"
        )
    except Exception as e:
        logger.error(
            f"Error saving Postman collection to {output_file}: {e}"
        )


def main() -> None:
    """
    Main function to parse arguments
    and generate the Postman collection.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate Postman collection from FastAPI app."
    )
    parser.add_argument(
        "--app",
        required=True,
        help="Path to the FastAPI app",
    )
    parser.add_argument(
        "--output",
        default="postman_collection.json",
        help="Output file for the Postman collection",
    )
    parser.add_argument(
        "--name",
        default="API Collection",
        help="Name of the Postman collection",
    )
    parser.add_argument(
        "--host",
        default="http://localhost",
        help="Host URL for the API",
    )
    parser.add_argument(
        "--readme",
        default="README.md",
        help="Path to the README.md file for documentation",
    )

    args = parser.parse_args()

    try:
        app_module, app_var = args.app.split(":")
        app = getattr(
            __import__(
                app_module,
                fromlist=[app_var]
            ),
            app_var
        )

        generate_postman_collection(
            app, args.output, args.name, args.host, args.readme
        )
    except Exception as e:
        logger.error(
            f"Error importing FastAPI app from {args.app}: {e}"
        )


if __name__ == "__main__":
    main()
