# Fast-Man

[![PyPI version](https://badge.fury.io/py/fast-man.svg?cache=none)](https://badge.fury.io/py/fast-man)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/rennf93/fast-man/actions/workflows/ci.yml/badge.svg)](https://github.com/rennf93/fast-man/actions/workflows/ci.yml)
[![Release](https://github.com/rennf93/fast-man/actions/workflows/release.yml/badge.svg)](https://github.com/rennf93/fast-man/actions/workflows/release.yml)
[![CodeQL](https://github.com/rennf93/fast-man/actions/workflows/code-ql.yml/badge.svg)](https://github.com/rennf93/fast-man/actions/workflows/code-ql.yml)

Fast-Man is a project that aims to automate the creation of `postman_collection.json` for a FastAPI app. This tool simplifies the process of generating Postman collections, making it easier to test and document your FastAPI APIs.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Using Command-Line Arguments](#using-command-line-arguments)
  - [Using in a Script](#using-in-a-script)
- [Example](#example)
- [Project Structure](#project-structure)
- [License](#license)
- [Contributing](#contributing)
- [Contact](#contact)
- [Funding](#funding)
- [Acknowledgements](#acknowledgements)

## Features

- **Automated Postman Collection Generation**: Automatically generate a Postman collection from your FastAPI app.
- **Customizable Output**: Specify the output file name, collection name, and host URL.
- **Bearer Token Authentication**: Supports bearer token authentication for secure API testing.
- **Detailed Route Information**: Includes request headers, body, parameters, and responses in the generated collection.

## Installation

You can install `fast-man` using pip:

```bash
pip install fast-man
```

## Usage

To generate a Postman collection, use the `fast-man` command-line tool. You need to provide the path to your FastAPI app, and you can optionally specify the output file, collection name, and host URL.

```bash
fast-man --app core.main:app \
--output postman_collection.json \
--name "test-api" \
--host "http://test.com:8000/api/v1" \
--readme "README.md"
```

### Using Command-Line Arguments

- `--app`: The path to the FastAPI app instance (required).
- `--output`: The output file name for the Postman collection (default: `postman_collection.json`).
- `--name`: The name of the Postman collection (default: `API Collection`).
- `--host`: The host URL for the API (default: `http://localhost`).
- `--readme`: The path to the README.md file (default: `README.md`).

> Note: If you want a custom documentation to be displayed
> in the Postman collection other than your project's README.md, you can use the `--readme` flag.

### Using in a Script

You can also use `fast-man` directly in your Python code. Here is an example:

```python
from fast_man.converter import generate_postman_collection
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

@app.post("/items/")
async def create_item(name: str):
    return {"name": name}

generate_postman_collection(
    app=app,
    output_file='postman_collection.json',
    input_name='test-api',
    input_host='http://localhost:8000',
    readme_file='README.md'
)

print("Postman collection generated successfully.")
```

## Example

Here is an example of how to use `fast-man`.

Given the project structure:

```
my-project/
├── core/
│   ├── main.py
├── tests/
│   ├── test_main.py
├── README.md
```

You can generate the Postman collection using the following command at root:

```bash
pip install fast-man
export PYTHONPATH=$(pwd)
fast-man --app core.main:app --output postman_collection.json --name "test-api" --host "http://test.com:8000/api/v1" --readme "README.md"
```

## Project Structure

The project is structured as follows:

- `fast_man/`: Contains the main code for the `fast-man` tool.
  - `__init__.py`: Initializes the package.
  - `converter.py`: Contains the logic for generating the Postman collection.
  - `utils.py`: Utility functions used by the converter.
- `tests/`: Contains tests for the `fast-man` tool.
  - `test_converter.py`: Tests for the converter module.
- `setup.py`: Setup script for packaging the project.
- `LICENSE`: License file for the project.
- `.gitignore`: Git ignore file to exclude unnecessary files from version control.

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for more details.

## Contributing

Contributions are welcomed! Please open an issue or submit a pull request on GitHub; or just get in [contact](#contact).

## Contact

For any questions or issues, please contact Renzo Franceschini at [rennf93@gmail.com].

## Funding

If you find this project useful, please consider supporting its development by making a donation. Your support is greatly appreciated!

- [GitHub Sponsors](https://github.com/sponsors/rennf93)
- [Paypal](https://paypal.me/renzof93)

## Acknowledgements

Special thanks to the FastAPI and Pydantic communities for their excellent libraries and documentation.

- [FastAPI](https://fastapi.tiangolo.com/)
- [FastAPI - Main class](https://fastapi.tiangolo.com/reference/fastapi/)
- [FastAPI - APIRouter](https://fastapi.tiangolo.com/reference/apirouter/?h=post#fastapi.APIRouter.post)
- [Pydantic](https://docs.pydantic.dev/latest/)
- [Pydantic - BaseModel](https://docs.pydantic.dev/latest/api/base_model/)
- [Pydantic - Fields](https://docs.pydantic.dev/latest/api/fields/)
