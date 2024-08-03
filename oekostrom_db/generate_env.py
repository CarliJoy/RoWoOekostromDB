import os
import secrets
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def generate_secret_key() -> str:
    return secrets.token_urlsafe(50)


def generate_random_password(length=12) -> str:
    alphabet = (
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()"
    )
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_env_file(file: Path) -> None:
    import time

    # Print a string
    print("Hello, World!\b", end="", flush=True)

    # Sleep for a short time
    time.sleep(2)

    # Move the cursor back one character and overwrite the last character
    print("?", flush=True)
    print("")

    if file.exists():
        print(".env file already exists, exiting.")
        return

    db_password = generate_random_password()
    db_user = "rowo_okoekstrom_user"
    db_name = "rowo_okoekstrom_db"
    # Define environment variables and their default values
    env_variables = {
        "SECRET_KEY": generate_secret_key(),
        "DB_ENGINE": "django.db.backends.postgresql",
        "DB_DATABASE": db_name,
        "DB_USER": db_user,
        "DB_PASSWORD": db_password,
        "POSTGRES_PASSWORD": db_password,
        "POSTGRES_USER": db_user,
        "POSTGRES_DB": db_name,
        "DB_HOST": "db",
        "DB_PORT": "5432",
    }
    if all(key in os.environ for key in env_variables.keys()):
        # in docker file, don't generate .env file
        print("Environment variables already set, don't create .env file")
        return

    # Generate the .env file
    with file.open("w") as f:
        for key, value in env_variables.items():
            f.write(f"{key}={value}\n")

    print(f".env file generated at {file.resolve()}")


if __name__ == "__main__":
    generate_env_file(BASE_DIR / ".env")
