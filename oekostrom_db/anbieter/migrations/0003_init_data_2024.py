import datetime
import json
import logging
import typing
from pathlib import Path
from zoneinfo import ZoneInfo

from django.db import migrations

if typing.TYPE_CHECKING:
    from django.apps.registry import Apps
    from django.db.backends.base.schema import BaseDatabaseSchemaEditor
    from django.db.models import Model


BASE_DIR = Path(__file__).parent.parent.parent.parent

DATA_DIR = BASE_DIR / "oekostrom-recherche" / "scraped_data"
logger = logging.getLogger(__name__)

# Get the timezone object for Berlin
berlin_timezone = ZoneInfo("Europe/Berlin")


class ScrapeAdder:
    def __init__(self, json_file: str, model_name: str):
        self.json_file = json_file
        self.model_name = model_name

    def __call__(
        self,
        apps: "Apps",
        schema_editor: "BaseDatabaseSchemaEditor",  # noqa ARG001
    ) -> None:
        # Get the user model
        model: type[Model] = apps.get_model("anbieter", self.model_name)

        target = DATA_DIR / self.json_file
        with target.open("r") as f:
            data: dict[str, typing.Any] = json.load(f)

        scraped = datetime.datetime.fromisoformat(data["create"])

        if scraped.tzinfo is None:
            scraped = scraped.replace(tzinfo=berlin_timezone)

        okay: int = 0
        failed: int = 0

        for result in data["results"]:
            name = result["name"]
            del result["name"]
            result["scrape_date"] = scraped
            try:
                model.objects.update_or_create(name=name, defaults=result)
            except Exception:
                logger.exception(f"Failed to create: {name} for {self.json_file}")
                failed += 1
            else:
                okay += 1
        logger.info(f"Imported {self.json_file} {okay=}, {failed=}")


class Migration(migrations.Migration):
    dependencies = [
        ("anbieter", "0002_create_models"),
    ]

    operations = [
        migrations.RunPython(ScrapeAdder("oekotest.json", "Oekotest")),
        migrations.RunPython(ScrapeAdder("okpower.json", "OkPower")),
        migrations.RunPython(ScrapeAdder("rowo2019.json", "Rowo2019")),
        migrations.RunPython(ScrapeAdder("stromauskunft.json", "Stromauskunft")),
        migrations.RunPython(ScrapeAdder("verivox.json", "Verivox")),
    ]
