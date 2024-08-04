import logging
import os
import secrets
import typing

from django.db import migrations

if typing.TYPE_CHECKING:
    from django.apps.registry import Apps
    from django.contrib.auth.models import User
    from django.db.backends.base.schema import BaseDatabaseSchemaEditor


logger = logging.getLogger(__name__)


def create_superuser(
    apps: "Apps",
    schema_editor: "BaseDatabaseSchemaEditor",  # noqa ARG001
) -> None:
    # Get the user model
    user_model: type[User] = apps.get_model("auth", "User")

    # Fetch the password from environment variable
    password = os.environ.get("DJANGO_ROOT_PASSWORD")
    if not password:
        password = secrets.token_urlsafe(32)
        logger.warning(
            "Error: DJANGO_ROOT_PASSWORD environment variable not set. "
            "A random password was selected."
        )
    else:
        logger.info("Creating superuser given from environment variable.")

    # Create the superuser
    user_model.objects.create_superuser(
        username="rowo", email="energie@robinwood.de", password=password
    )


class Migration(migrations.Migration):
    dependencies = []

    operations = [
        migrations.RunPython(create_superuser),
    ]
