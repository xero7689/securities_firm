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

### Using Docker Container

1. **Build and run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

2. **Create a superuser** (in a separate terminal):
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

3. **Access the application**:
   - User interface: http://localhost:8000
   - Admin interface: http://localhost:8000/admin

**Note**: Containerized deployment is preferred for production environments.
