import json
import logging
import typing
from pathlib import Path

from django.db import migrations

if typing.TYPE_CHECKING:
    from django.apps.registry import Apps
    from django.db.backends.base.schema import BaseDatabaseSchemaEditor
    from django.db.models import Model


BASE_DIR = Path(__file__).parent.parent.parent.parent

DATA_DIR = BASE_DIR / "oekostrom-recherche" / "scraped_data"
COMBINED_JSON = DATA_DIR / "combined.json"

logger = logging.getLogger(__name__)

fields = {
    "rowo2019": "rowo_2019",
    "okpower": "ok_power",
}


def combine_entries(
    apps: "Apps",
    schema_editor: "BaseDatabaseSchemaEditor",  # noqa ARG001
) -> None:
    """
    Create the relations between the different anbieter
    """
    with COMBINED_JSON.open() as f:
        combined: list[dict[str, str]] = json.load(f)

    anbieter: type[Model] = apps.get_model("anbieter", "Anbieter")
    names: type[Model] = apps.get_model("anbieter", "AnbieterName")
    models: dict[str, type[Model]] = {
        "oekotest": apps.get_model("anbieter", "Oekotest"),
        "okpower": apps.get_model("anbieter", "OkPower"),
        "rowo2019": apps.get_model("anbieter", "Rowo2019"),
        "stromauskunft": apps.get_model("anbieter", "Stromauskunft"),
        "verivox": apps.get_model("anbieter", "Verivox"),
    }
    for combination in combined:
        # first find a name in the defined order
        for name_source in (
            "rowo2019",
            "verivox",
            "stromauskunft",
            "okpower",
            "oekotest",
        ):
            name = combination[name_source]
            if name:
                break
        obj, created = anbieter.objects.get_or_create(name=name)
        if created:
            logger.info(f"Created {obj.name} for {name_source}")
        for source, name in combination.items():
            if name:
                name_obj = names.objects.get_or_create(name=name, anbieter=obj)[0]
                target = models[source].objects.get(name=name)
                setattr(obj, fields.get(source, source), target)
                setattr(name_obj, fields.get(source, source), target)
                name_obj.save()
        obj.save()


class Migration(migrations.Migration):
    dependencies = [
        ("anbieter", "0004_add_name_and_more"),
    ]

    operations = [
        migrations.RunPython(combine_entries),
    ]
