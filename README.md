# fast-man

FastPostman is a project that aims to automate the creation of `postman_collection.json` for a FastAPI app. This tool simplifies the process of generating Postman collections, making it easier to test and document your FastAPI APIs.

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
fast-man --app core.main:app --output postman_collection.json --name "test-api" --host "http://test.com:8000/api/v1"
```

### Command-Line Arguments

- `--app`: The path to the FastAPI app instance (required).
- `--output`: The output file name for the Postman collection (default: `postman_collection.json`).
- `--name`: The name of the Postman collection (default: `API Collection`).
- `--host`: The host URL for the API (default: `http://localhost`).

## Example

Here is an example of how to use `fast-man`.

Given the project structure:

```
my-project/
├── core/
│   ├── main.py
├── tests/
│   ├── test_main.py
```

You can generate the Postman collection using the following command at root:

```bash
export PYTHONPATH=$(pwd)
pip install fastapi pydantic requests numpy==1.26.4
pip install -e /Users/renzof/Documents/GitHub/fast-man
fast-man --app core.main:app --output postman_collection.json --name "test-api" --host "http://test.com:8000/api/v1"
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

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

## Contact

For any questions or issues, please contact Renzo Franceschini at [your-email@example.com].

## Acknowledgements

Special thanks to the FastAPI and Pydantic communities for their excellent libraries and documentation.