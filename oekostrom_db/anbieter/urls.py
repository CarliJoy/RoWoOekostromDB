from django.conf import settings
from django.urls import path

from . import view_mirror, views

urlpatterns = [
    path("", views.startpage, name="startpage"),
    path("survey/fail", views.fail, name="fail_view"),
    path("survey/<str:code>/", views.SurveyView.as_view(), name="survey_update"),
]


if settings.ROWO_MIRRORING:
    urlpatterns += [
        path(
            "mirror/<path:file_path>",
            view_mirror.mirror,
            name="mirror",
        ),
        # Handle themes special because we can't change some of the url
        path(
            "themes/<path:file_path>",
            view_mirror.theme,
            name="themes",
        ),
    ]
