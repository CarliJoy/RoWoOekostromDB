from django.conf import settings
from django.urls import path

import oekostrom_db.anbieter.view_mirror

from . import views

urlpatterns = [
    path("", views.startpage, name="startpage"),
    path("survey", views.survey, name="survey"),
]


if settings.ROWO_MIRRORING:
    urlpatterns += [
        path(
            "mirror/<path:file_path>",
            oekostrom_db.anbieter.view_mirror.mirror,
            name="mirror",
        ),
        # Handle themes special because we can't change some of the url
        path(
            "themes/<path:file_path>",
            oekostrom_db.anbieter.view_mirror.theme,
            name="themes",
        ),
    ]
