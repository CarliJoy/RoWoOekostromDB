import logging

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Layout, Row, Submit
from django.conf import settings
from django.db.models.query_utils import DeferredAttribute
from django.forms import Form
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.generic.edit import UpdateView

from .models import Anbieter, CompanySurvey2024

logger = logging.getLogger(__name__)


def startpage(request: HttpRequest) -> HttpResponse:
    context = {
        "count_active": Anbieter.objects.filter(active=True).count(),
    }

    return render(request, "anbieter/startpage.html", context)


def gen_survey_helper() -> FormHelper:
    helper = FormHelper()
    helper.form_group_wrapper_class = "form-group"
    helper.form_class = "from form-horizontal"
    helper.field_class = "col-sm-6"
    helper.label_class = "col-sm-4"
    layout_list = []
    for field_name in CompanySurvey2024._field_order:
        field = getattr(CompanySurvey2024, field_name)
        if hasattr(field, "__html__"):
            layout_list.append(HTML(field.__html__()))
        else:
            if isinstance(field, DeferredAttribute):
                field = field.field
            if hasattr(field, "bootstrap_field"):
                layout_list.append(field.bootstrap_field(field_name))
            else:
                layout_list.append(field_name)
    layout_list.append(Row(Submit("Speichern", "Speichern", css_class="mb-5 mt-3")))
    helper.add_layout(Layout(*layout_list))
    return helper


class SurveyView(UpdateView):
    model = CompanySurvey2024

    fields = "__all__"

    template_name = "anbieter/survey.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context |= {
            "rowo_url": "/mirror" if settings.ROWO_MIRRORING else "/static",
            "teaser": "Fragebogen für Ökostrom GmbH",
            # Get template errors to disappear
            "tag": "div",
            "wrapper_class": "form-group row align-items-center",
        }
        return context

    def get_form(self, form_class=None) -> Form:
        form = super().get_form(form_class)
        form.helper = gen_survey_helper()
        return form

    def get_object(self, queryset=None) -> CompanySurvey2024:  # noqa: ARG002
        return CompanySurvey2024()
