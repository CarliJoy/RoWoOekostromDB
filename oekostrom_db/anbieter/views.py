import logging
from typing import TYPE_CHECKING, Any

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Submit
from django.conf import settings
from django.db.models.query_utils import DeferredAttribute
from django.forms import Form, ModelForm
from django.forms import models as model_forms
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.safestring import SafeString
from django.views.generic.edit import UpdateView

from .field_helper import get_fill_status
from .layouts import (
    Alert,
    LayoutElement,
    PercentChecker,
    Section,
    State,
)
from .models import Anbieter, CompanySurvey2024, SurveyAccess

if TYPE_CHECKING:
    from django.db.models import Field


logger = logging.getLogger(__name__)


def startpage(request: HttpRequest) -> HttpResponse:
    context = {
        "count_active": Anbieter.objects.filter(active=True).count(),
    }

    return render(request, "anbieter/startpage.html", context)


def render_section(name: str) -> str:
    return f"<small style='text-transform: uppercase'>{name}</small>"


class FormHelperExpanded(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_to_section: dict[str, str] = {}
        self.field_to_name: dict[str, str] = {}

    def get_field_name(self, name: str) -> str:
        section = ""
        if name in self.field_to_section:
            section = f"{render_section(self.field_to_section[name])} - "
        desc = self.field_to_name.get(name, name)
        return f'<a href="#div_id_{name}">{section}{desc}</a>'

    def gen_error_list(self, error_list: dict[str | None, list[str] | str]) -> str:
        result = '<ul class="errorlist">'
        for key, values in error_list.items():
            if isinstance(values, str):
                values = [values]  # noqa: PLW2901

            if key:
                result = (
                    f"{result}<li>{self.get_field_name(key)}:\n<ul class='errorlist'>"
                )

            for value in values:
                result = f"{result}<li>{value}</li>"

            if key:
                result = f"{result}</ul></li>"
        return SafeString(result)


def gen_survey_helper(  # noqa: PLR0912, PLR0915
    form: ModelForm,  # noqa: ARG001
    state: State,
    add_save_button: bool,
) -> FormHelper:
    helper = FormHelperExpanded()
    helper.form_group_wrapper_class = "form-group"
    helper.form_class = "from form-horizontal"
    helper.field_class = "col-sm-6"
    helper.label_class = "col-sm-4"
    helper.form_action = "#content-start"
    field_list = []

    if form.is_bound:
        data = form.cleaned_data
    else:
        data = form.initial

    checks_failed: list[tuple[str, str]] = []
    section = ""
    section_id = ""
    for field_name in CompanySurvey2024._field_order:
        field = getattr(CompanySurvey2024, field_name)
        if isinstance(field, PercentChecker):
            layout, check_okay = field.check(data)
            field_list.append(layout)
            if not check_okay:
                checks_failed.append((section, section_id))
        elif isinstance(field, LayoutElement):
            if isinstance(field, Section):
                section = field.name
                section_id = field_name
            field.field_name = field_name
            field_list.append(field)
        else:
            if isinstance(field, DeferredAttribute):
                field: Field = field.field
            if getattr(field, "name", False):
                helper.field_to_section[field.name] = section
                helper.field_to_name[field.name] = field.verbose_name
            if hasattr(field, "bootstrap_field"):
                field_list.append(field.bootstrap_field(field_name))
            elif getattr(field, "editable", False):
                field_list.append(field_name)
    if add_save_button:
        field_list.append(Row(Submit("Speichern", "Speichern", css_class="mb-5 mt-3")))

    alerts: list[Alert] = []
    if state in CompanySurvey2024.state_labels:
        alert_gen = CompanySurvey2024.state_labels[state]
        if form.errors:
            alerts.append(alert_gen(helper.gen_error_list(form.errors)))
        else:
            alerts.append(alert_gen())

    if checks_failed:
        alert_gen = CompanySurvey2024.state_labels[State.saved_with_warning]
        extra_content = "".join(
            f"<li><a href='#id-section-{field_id}'>{render_section(name)}</a></li>"
            for name, field_id in checks_failed
        )
        extra_content = f'<ul class="errorlist">{extra_content}</ul>'
        alerts.append(alert_gen(extra_content))
    helper.add_layout(Layout(*alerts, *field_list))
    return helper


class RevisionModelForm(ModelForm):
    def __init__(self, *args, current_revision: int, request_path: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_revision = current_revision
        self.request_path = request_path

    def clean(self) -> dict[str, Any]:
        data = super().clean() or self.cleaned_data
        data["_fill_status"] = get_fill_status(data)
        if self.is_bound:
            if data.get("revision") != self.current_revision:
                self.add_error(
                    field=None,
                    error=SafeString(
                        "Diese Umfrage wurde zwischenzeitlich von einer anderen Person bzw. "
                        "in einen anderen Browserfenster gespeichert. "
                        "Das Speichern dieser Version ist daher nicht mehr möglich. "
                        f"Öffnen Sie den "
                        f"<a href='{self.request_path}' target='_blank'>Umfragelink</a> "
                        f"erneut um fortzufahren."
                    ),
                )
        return data


class SurveyView(UpdateView):
    model = CompanySurvey2024
    fields = "__all__"
    template_name = "anbieter/survey.html"

    object: CompanySurvey2024
    survey_access: SurveyAccess  # Store the SurveyAccess instance for easy access

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reset_form: bool = False
        self.state: State = State.start
        self.view_mode: bool = False
        self.rev: int | None = None

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.view_mode: bool = request.GET.get("view") is not None
        if "rev" in request.GET:
            self.rev = int(request.GET["rev"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rev = ""
        if self.view_mode:
            rev = f"<small>Rev. {self.object.revision}/{self.survey_access.current_revision}</small>"
        context |= {
            "rowo_url": "/mirror" if settings.ROWO_MIRRORING else "/static",
            "rowo_hp": "https://robinwood.de",
            "teaser": f"Ökostrom Fragebogen für <br /><h3>{self.survey_access.anbieter.name}</h3>{rev}",
            # Get template errors to disappear
            "tag": "div",
            "wrapper_class": "form-group row align-items-center",
        }
        return context

    def get_form_class(self) -> type[RevisionModelForm]:
        return model_forms.modelform_factory(
            self.model, fields=self.fields, form=RevisionModelForm
        )

    def get_form(self, form_class=None) -> Form:
        form: ModelForm = super().get_form(form_class)
        add_save_button = not self.view_mode
        if self.view_mode:
            for field in form.fields.values():
                field.disabled = True
            if self.survey_access.current_revision == self.object.revision:
                self.state = State.view_only
            else:
                self.state = State.view_old
        elif form.is_bound:
            # only overwrite state if form is bound, as otherwise the state was already set
            # in either in init or the get_form call before
            if form.is_valid():
                if form.has_changed():
                    self.state = State.saved
                else:
                    self.state = State.unchanged
            else:
                print(repr(form.errors))
                print(form.errors)
                self.state = State.error
        form.helper = gen_survey_helper(form, self.state, add_save_button)
        return form

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["current_revision"] = self.survey_access.current_revision
        kwargs["request_path"] = self.request.path
        if self.reset_form:
            for elm in ("data", "files"):
                if elm in kwargs:
                    del kwargs[elm]
        return kwargs

    def get_object(
        self,
        queryset: CompanySurvey2024 | None = None,  # noqa: ARG002
    ) -> CompanySurvey2024:
        # Retrieve survey via SurveyAccess code and increment access count
        self.survey_access = get_object_or_404(SurveyAccess, code=self.kwargs["code"])
        if self.view_mode:
            if self.rev:
                return get_object_or_404(
                    CompanySurvey2024,
                    anbieter=self.survey_access.anbieter,
                    revision=self.rev,
                )
        else:
            self.survey_access.increment_access_count()
        return self.survey_access.survey

    def form_valid(self, form: ModelForm) -> HttpResponse:
        if not form.has_changed():
            # Nothing has changed, so keep revision as it is
            return self.render_to_response(self.get_context_data(form=form))
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
        self.survey_access.changed = timezone.now()
        self.survey_access.save()

        # recreate form, reset request
        self.object = self.get_object()
        self.reset_form = True
        form = self.get_form()
        # Render the form with additional context "status": "saved"
        context = self.get_context_data(form=form)
        return self.render_to_response(context)
