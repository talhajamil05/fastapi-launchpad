import os
import shutil
from pathlib import Path
import pytest
from typer.testing import CliRunner
from fastapi_launchpad.cli import cli

runner = CliRunner()


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for testing."""
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(Path.cwd().parent)


def test_version():
    """Test version command."""
    result = runner.invoke(cli, ["version"])
    assert result.exit_code == 0
    assert "FastAPI Launchpad v" in result.stdout


def test_basic_project_creation(temp_dir):
    """Test creating a basic project without database."""
    result = runner.invoke(cli, ["project", "test-basic"])
    assert result.exit_code == 0

    project_path = temp_dir / "test_basic"
    assert project_path.exists()
    assert (project_path / "src" / "main.py").exists()
    assert (project_path / "requirements.txt").exists()
    assert (project_path / ".env").exists()
    assert (project_path / ".env.example").exists()


def test_postgres_creation(temp_dir):
    """Test creating a project with PostgreSQL async."""
    result = runner.invoke(cli, ["project", "test-postgres", "--database", "postgres"])
    assert result.exit_code == 0

    project_path = temp_dir / "test_postgres"
    assert project_path.exists()

    db_config = (project_path / "src" / "database.py").read_text()
    assert "create_engine" in db_config
    assert "sessionmaker" in db_config

    requirements = (project_path / "requirements.txt").read_text()
    assert "psycopg2-binary" in requirements

    env_content = (project_path / ".env").read_text()
    assert "postgresql://" in env_content


def test_mysql_creation(temp_dir):
    """Test creating a project with MySQL sync."""
    result = runner.invoke(cli, ["project", "test-mysql", "--database", "mysql"])
    assert result.exit_code == 0

    project_path = temp_dir / "test_mysql"
    assert project_path.exists()

    db_config = (project_path / "src" / "database.py").read_text()
    assert "create_engine" in db_config
    assert "sessionmaker" in db_config

    requirements = (project_path / "requirements.txt").read_text()
    assert "mysqlclient" in requirements
    assert "sqlalchemy" in requirements

    env_content = (project_path / ".env").read_text()
    assert "mysql://" in env_content


def test_mongodb_creation(temp_dir):
    """Test creating a project with MongoDB."""
    result = runner.invoke(cli, ["project", "test-mongodb", "--database", "mongodb"])
    assert result.exit_code == 0

    project_path = temp_dir / "test_mongodb"
    assert project_path.exists()

    db_config = (project_path / "src" / "database.py").read_text()
    assert "motor.motor_asyncio" in db_config

    requirements = (project_path / "requirements.txt").read_text()
    assert "motor" in requirements

    env_content = (project_path / ".env").read_text()
    assert "DATABASE_URL" in env_content
    assert "MONGO_DATABASE_NAME" in env_content


def test_invalid_project_name(temp_dir):
    """Test invalid project names."""
    result = runner.invoke(cli, ["project", "123test"])
    assert result.exit_code == 1
    assert "cannot start with a number" in result.stdout

    result = runner.invoke(cli, ["project", "test project"])
    assert result.exit_code == 0
    assert (temp_dir / "test_project").exists()


def test_invalid_database(temp_dir):
    """Test invalid database choice."""
    result = runner.invoke(cli, ["project", "test-invalid", "--database", "invalid"])
    assert result.exit_code == 1
    assert "Invalid database choice" in result.stdout


def test_current_directory_creation(temp_dir):
    """Test creating project in current directory."""
    os.mkdir("test-current")
    os.chdir("test-current")

    result = runner.invoke(cli, ["project", "."])
    assert result.exit_code == 0

    assert (Path.cwd() / "src").exists()
    assert (Path.cwd() / "src" / "main.py").exists()

    os.chdir("..")
