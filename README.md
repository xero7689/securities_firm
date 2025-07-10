# Securities Firm Account Opening Demo

This project is a securities firm account opening demo powered by Django.

## Python Requirements

- **Python**: >= 3.12
- **Django**: >= 5.2.4
- **Package Management**: [uv](https://docs.astral.sh/uv/guides/)

## Running the Project

### Using uv (Host Machine)

1. **Install uv** (if not already installed):
   Follow the [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/)

2. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd securities_firm
   ```

3. **Install dependencies**:

   ```bash
   uv sync
   ```

4. **Run database migrations**:

   ```bash
   uv run python manage.py migrate
   ```

5. **Create a superuser** (administrator account):

   ```bash
   uv run python manage.py createsuperuser
   ```

6. **Start the development server**:

   ```bash
   uv run python manage.py runserver
   ```

7. **Access the application**:
   - User interface: http://localhost:8000
   - Admin interface: http://localhost:8000/admin

## Testing

### Unit Testing with uv

This project uses pytest and pytest-django for testing. Tests are configured to run with Django settings automatically.

**Important**: While Django's development server (`python manage.py runserver`) is suitable for local development and testing, it should **never be used in production environments** due to security and performance limitations.

1. **Run all tests**:

   ```bash
   uv run pytest -v
   ```

2. **Run specific test module**:

   ```bash
   uv run pytest accounts -v
   ```

3. **Run tests with coverage**:

   ```bash
   uv run pytest --cov=. -v
   ```

**Note**: Tests are configured in `pyproject.toml` to automatically use `securities_firm.settings` as the Django settings module.

## Docker Deployment

### Environment Setup

1. **Create a `.env` file** in the project root for environment variables:

   ```bash
   cp example-env .env
   ```

2. **Edit the `.env` file** and update the values:

   - Change `POSTGRES_PASSWORD` to a secure password
   - Change `DJANGO_SECRET_KEY` to a secure secret key
   - Modify other settings as needed for your environment

   See `example-env` for the complete list of required environment variables.

### Using Docker Container

1. **Build and run with Docker Compose**:

   ```bash
   docker-compose up --build
   ```

2. **Create a superuser** (in a separate terminal):

   ```bash
   docker-compose exec app python manage.py createsuperuser
   ```

3. **Access the application**:
   - User interface: http://localhost:8080
   - Admin interface: http://localhost:8080/admin

**Note**: The Docker container runs the application using **uvicorn** as the ASGI server, which is production-ready and optimized for performance.

### Uvicorn Configuration

The containerized setup supports several uvicorn configuration options through environment variables:

- `UVICORN_WORKER_NUMS`: Number of worker processes (default: 1)
- `UVICORN_DEBUG_RELOAD`: Enable auto-reload on code changes (default: false)
  - When set to `true`, uvicorn will automatically reload the server when source code changes
  - **Important**: When `--reload` is enabled, the `UVICORN_WORKER_NUMS` setting has no effect as uvicorn runs in single-process mode for development
  - Use `UVICORN_DEBUG_RELOAD=true` for development environments only
  - Set to `false` for production to enable multi-worker mode

### Important Notes for Production Deployment

**Development vs Production**:

- The containerized setup includes automatic database migrations and static file collection on startup via `entrypoint.sh`
- This is intended for **development and testing environments only**

**Production Deployment**:
For production deployments, database migrations and static file collection should be handled in CI/CD pipeline rather than automatically on container startup:

## Contributing

### Code Formatting and Linting

This project uses Ruff for code formatting and linting. Before contributing, please ensure your code is properly formatted and linted:

```bash
ruff check --config ruff.toml --extend-select I --fix .; ruff format
```
