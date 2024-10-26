import logging
from typing import TYPE_CHECKING

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Layout, Row, Submit
from django.conf import settings
from django.db.models.query_utils import DeferredAttribute
from django.forms import Form, ModelForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic.edit import UpdateView

from .models import Anbieter, CompanySurvey2024, SurveyAccess

if TYPE_CHECKING:
    from django.db.models import Field


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
                field: Field = field.field
            if hasattr(field, "bootstrap_field"):
                layout_list.append(field.bootstrap_field(field_name))
            elif getattr(field, "editable", False):
                layout_list.append(field_name)
    layout_list.append(Row(Submit("Speichern", "Speichern", css_class="mb-5 mt-3")))
    helper.add_layout(Layout(*layout_list))
    return helper


class SurveyView(UpdateView):
    model = CompanySurvey2024
    fields = "__all__"
    template_name = "anbieter/survey.html"

    survey_access: SurveyAccess  # Store the SurveyAccess instance for easy access

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context |= {
            "rowo_url": "/mirror" if settings.ROWO_MIRRORING else "/static",
            "rowo_hp": "https://robinwood.de",
            "teaser": f"Fragebogen für <strong>{self.survey_access.anbieter.name}</strong>",
            # Get template errors to disappear
            "tag": "div",
            "wrapper_class": "form-group row align-items-center",
        }
        return context

    def get_form(self, form_class=None) -> Form:
        form = super().get_form(form_class)
        form.helper = gen_survey_helper()
        return form

    def get_object(
        self,
        queryset: CompanySurvey2024 | None = None,  # noqa: ARG002
    ) -> CompanySurvey2024:
        # Retrieve survey via SurveyAccess code and increment access count
        self.survey_access = get_object_or_404(SurveyAccess, code=self.kwargs["code"])
        self.survey_access.increment_access_count()
        return self.survey_access.survey

    def form_valid(self, form: ModelForm) -> HttpResponse:
        # Check if a newer revision has been created
        if form.instance.revision != self.survey_access.current_revision:
            form.add_error(
                field=None,
                error=(
                    "Diese Umfrage wurde zwischenzeitlich von einer anderen Person bzw. "
                    "in einen anderen Browserfenster gespeichert. "
                    "Ein speichern dieser Version ist daher nicht mehr möglich. "
                    "Öffnen Sie den Umfragelink erneut um fortzufahren."
                ),
            )
            return self.form_invalid(form)

        # Increment revision and save a new CompanySurvey2024 instance
        new_revision = self.survey_access.current_revision + 1
        form.instance.revision = new_revision
        form.instance.anbieter = self.survey_access.anbieter

        # Save the new revision instance
        new_survey = form.save(commit=False)
        new_survey.pk = None  # Ensures a new instance is created
        new_survey.save()

        # Update SurveyAccess to point to the new revision
        self.survey_access.survey = new_survey
        self.survey_access.current_revision = new_revision
        self.survey_access.save()

        # Render the form with additional context "status": "saved"
        context = self.get_context_data(form=form, status="saved")
        return self.render_to_response(context)
