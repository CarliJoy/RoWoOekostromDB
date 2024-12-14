import copy
import json
import logging
import traceback
from typing import Any, Final
from urllib.parse import urlparse

from django import forms
from django.contrib import admin
from django.contrib.admin.utils import unquote
from django.contrib.admin.widgets import AutocompleteSelect
from django.core.mail import send_mail
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import SafeString, mark_safe
from jinja2 import Template as JinjaTemplate

from .filter import EmpfohlenFilter, SurveyStatusFilter
from .models import (
    STATUS_CHOICES,
    Anbieter,
    AnbieterName,
    CompanySurvey2024,
    Oekotest,
    OkPower,
    Rowo2019,
    Stromauskunft,
    SurveyAccess,
    Template,
    TemplateNames,
    UmfrageVersendung2024,
    Verivox,
)

NUMBER_ATTR: Final[str] = "_running_number"

logger = logging.getLogger(__name__)


class RenderException(Exception):
    def __init__(self, anbieter: Anbieter, exc: Exception) -> None:
        self._anbieter = anbieter
        self.exc = exc
        super().__init__(
            f"Failed to render template for {anbieter.name}: {type(self.exc).__name__}: {self.exc}"
        )


def get_homepage_export_data(
    template: str, include_pre: bool = False
) -> list[dict[str, str | list[str]]]:
    data: dict[str, str | list[str]] = []

    anbieter = Anbieter.objects.filter(active=True).order_by("name")
    anbieter = anbieter.select_related("survey_access", "mutter", "sells_from")

    for obj in anbieter:
        # Get related names from AnbieterNames
        related_names = obj.names.all().values_list("name", flat=True)

        # Render the Jinja2 template content using current Anbieter as context
        context = {"obj": obj, "anbieter": obj, "related_names": related_names}
        jinja_template = JinjaTemplate(template)
        try:
            rendered_content = jinja_template.render(context)
        except Exception as e:
            raise RenderException(anbieter=obj, exc=e)
        if include_pre:
            rendered_content = f"<pre>{rendered_content}</pre>"
        # Construct the JSON data
        data.append(
            {
                "title": obj.name,
                "id": obj.slug_id,
                "names": list(related_names),
                "content": rendered_content,
            }
        )
    return data


class ViewOnlyAdmin(admin.ModelAdmin):
    def has_add_permission(self, request: HttpRequest) -> bool:  # noqa ARG002
        return False

    def has_change_permission(self, request: HttpRequest, obj: Any = None):  # noqa: ARG002:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: Any = None):  # noqa: ARG002
        return False


@admin.register(SurveyAccess)
class SurveyAccessAdmin(ViewOnlyAdmin):
    search_fields = ("anbieter__name", "code")
    list_display = (
        "code",
        "anbieter_name",
        "survey_link",
        "current_revision",
        "changed",
        "access_count",
        "last_access",
    )

    @admin.display(description="Anbieter", ordering="anbieter__name")
    def anbieter_name(self, obj: SurveyAccess) -> str:
        url = reverse("admin:anbieter_anbieter_change", args=[obj.anbieter.id])
        return SafeString(f"<a href='{url}'>{obj.anbieter.name}</a>")

    @admin.display(description="Umfrage", ordering="anbieter__name")
    def survey_link(self, obj: SurveyAccess) -> str:
        url = obj.get_absolute_url()
        return SafeString(f"<a href='{url}'>Umfrage</a>")


@admin.register(CompanySurvey2024)
class SurveyAdmin(ViewOnlyAdmin):
    search_fields = ("anbieter__name",)
    list_display = ("anbieter", "revision", "created")


@admin.register(OkPower, Oekotest, Rowo2019, Stromauskunft, Verivox)
class ScraperAdmin(ViewOnlyAdmin):
    search_fields = ("name",)


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ["name"]

    change_form_template = "admin/template_change_form.html"

    def has_delete_permission(self, request: HttpRequest, obj: Template | None = None):  # noqa ARG002
        return False

    def render_change_form(  # noqa: PLR0913
        self,
        request: HttpRequest,
        context: dict[str, Any],
        add: bool = False,
        change: bool = False,
        form_url: str = "",
        obj: Template = None,
    ) -> HttpResponse:
        if change:
            context["template_previews"] = []
            if object_id := context.get("object_id"):
                obj: Template = self.get_object(request, unquote(object_id))
                if obj.name in (
                    TemplateNames.HOMEPAGE_TEXT_EXPORT,
                    TemplateNames.SURVEY2024_TXT,
                    TemplateNames.SURVEY2024_SUBJECT,
                    TemplateNames.SURVEY2024_HTML,
                ):
                    try:
                        context["template_previews"] = get_homepage_export_data(
                            obj.template,
                            include_pre=obj.name == TemplateNames.SURVEY2024_TXT,
                        )
                    except RenderException as e:
                        self.message_user(request, message=str(e), level="error")
                    context["show_save_and_continue"] = True
                    context["show_save_and_add_another"] = False
                    context["show_save"] = False
        return super().render_change_form(request, context, add, change, form_url)


@admin.register(AnbieterName)
class AnbieterNameAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = [
        "name",
        "the_anbieter_id",
        "has_rowo_2019",
        "has_oekotest",
        "has_ok_power",
        "has_stromauskunft",
        "has_verivox",
    ]
    list_per_page = 250

    @admin.display(description="Anbieter", ordering="anbieter__name")
    def the_anbieter_id(self, obj: AnbieterName) -> str:
        return str(obj.anbieter.id)

    @admin.display(
        description="Robinwood 2019", boolean=True, ordering="rowo_2019__name"
    )
    def has_rowo_2019(self, obj: AnbieterName) -> bool:
        return obj.rowo_2019 is not None

    @admin.display(description="Ökotest", boolean=True, ordering="oekotest__name")
    def has_oekotest(self, obj: AnbieterName) -> bool:
        return obj.oekotest is not None

    @admin.display(description="OK Power", boolean=True, ordering="ok_power__name")
    def has_ok_power(self, obj: AnbieterName) -> bool:
        return obj.ok_power is not None

    @admin.display(
        description="Stromauskunft", boolean=True, ordering="stromauskunft__name"
    )
    def has_stromauskunft(self, obj: AnbieterName) -> bool:
        return obj.stromauskunft is not None

    @admin.display(description="Verivox", boolean=True, ordering="verivox__name")
    def has_verivox(self, obj: AnbieterName) -> bool:
        return obj.verivox is not None

    def has_change_permission(self, request, obj=None):  # noqa ARG002
        return False

    def has_delete_permission(self, request, obj=None):  # noqa ARG002
        return False


class AnbieterNameInline(admin.TabularInline):
    model = AnbieterName
    extra = 1
    fields = ("name",)
    verbose_name_plural = "Alternative Namen für Anbieter"

    def has_change_permission(self, request, obj=None):  # noqa ARG002
        return False

    def has_delete_permission(self, request, obj=None):  # noqa ARG002
        return False


class SurveyAccessInline(admin.StackedInline):
    model = SurveyAccess
    extra = 0
    fields = (
        "code",
        "current_revision",
        "changed",
        "access_count",
        "last_access",
        "fill_status",
    )
    verbose_name_plural = "Umfrage Status"
    can_delete = False

    def get_readonly_fields(self, request, obj=None):  # noqa ARG002
        return self.fields

    def fill_status(self, obj: SurveyAccess) -> str:
        return f"{obj.survey._fill_status} %"

    def has_change_permission(self, request, obj=None):  # noqa ARG002
        return False

    def has_delete_permission(self, request, obj=None):  # noqa ARG002
        return False

    def has_add_permission(self, request, obj=None):  # noqa ARG002
        return False


autocomplete_fields = (
    "rowo_2019",
    "oekotest",
    "ok_power",
    "stromauskunft",
    "verivox",
    "mutter",
    "sells_from",
)


class AnbieterForm(forms.ModelForm):
    class Meta:
        # make autocomplete field larger
        # see https://stackoverflow.com/questions/61679332
        widgets = {
            field: AutocompleteSelect(
                Anbieter._meta.get_field(field),
                admin.site,
                attrs={
                    "data-dropdown-auto-width": "true",
                    "style": "width: 512px",
                },
            )
            for field in autocomplete_fields
        } | {
            "note": forms.Textarea(attrs={"class": "vLargeTextField", "rows": "2"}),
            "plz": forms.TextInput(attrs={"size": "6"}),
        }


@admin.register(Anbieter)
class AnbieterAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = (
        "obj_id",
        "name",
        "active",
        "german_wide",
        "has_mutter",
        "has_sells_from",
        "status",
        "homepage_url",
        "mail",
        "ee_only",
        "additional",
        "independent",
        "no_bad_money",
        "survey_answered",
        "ist_empfohlen",
    )
    list_filter = [
        "active",
        "german_wide",
        ("mutter", admin.EmptyFieldListFilter),
        ("sells_from", admin.EmptyFieldListFilter),
        "status",
        ("begruendung_extern", admin.EmptyFieldListFilter),
        "nur_oeko",
        "zusaetzlichkeit",
        "unabhaengigkeit",
        "money_for_ee_only",
        EmpfohlenFilter,
        SurveyStatusFilter,
    ]

    change_list_template = "admin/rowo_changelist.html"

    inlines = (AnbieterNameInline,)
    list_per_page = 1500
    ordering = ("name",)

    form = AnbieterForm
    autocomplete_fields = autocomplete_fields

    actions = ["init_survey_email"]

    # Add custom URL and buttons
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "export-homepage/",
                self.export_for_homepage_view,
                name="export_homepage",
            ),
        ]
        return custom_urls + urls

    def export_for_homepage_view(self, request: HttpRequest) -> HttpResponse:
        # Retrieve the template for "HOMEPAGE_TEXT_EXPORT"
        try:
            homepage_template = Template.objects.get(
                name=TemplateNames.HOMEPAGE_TEXT_EXPORT
            )
        except Template.DoesNotExist:
            self.message_user(
                request, "Homepage export template not found.", level="error"
            )
            return HttpResponseRedirect(reverse("admin:anbieter_anbieter_changelist"))

        data = get_homepage_export_data(homepage_template.template)

        # Convert the data to JSON
        response_content = json.dumps(data, indent=4)

        # Create the HTTP response with the JSON content as a file download
        response = HttpResponse(response_content, content_type="application/json")
        response["Content-Disposition"] = "attachment; filename=anbieter_export.json"

        return response

    @admin.action(description="Init Umfrageversendung")
    def init_survey_email(self, request: HttpRequest, queryset):
        obj: Anbieter
        created = 0
        already_existed = 0
        for obj in queryset:
            try:
                UmfrageVersendung2024.objects.get(anbieter=obj)
            except UmfrageVersendung2024.DoesNotExist:
                # Create the instance only if it does not exist, without copying all defaults
                new = UmfrageVersendung2024(anbieter=obj)
                new.save_base(raw=True, force_insert=True)
                created += 1
            else:
                already_existed += 1
        self.message_user(
            request, f"Umfrageversendungen initiiert {created=} {already_existed=}"
        )

    # Add the export button to the admin interface
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["extra_buttons"] = {
            "Export for Homepage": reverse("admin:export_homepage")
        }
        return super().changelist_view(request, extra_context=extra_context)

    @admin.display(description="#", ordering="id")
    def obj_id(self, obj: Anbieter) -> str:
        return f"#{obj.id:04}"

    @admin.display(description="Homepage", ordering="homepage")
    def homepage_url(self, obj: Anbieter) -> str:
        if not obj.homepage:
            return ""
        url = urlparse(obj.homepage)
        if not url.hostname:
            logger.warning(f"{obj} has invalid homepage url '{obj.homepage}'")
            return ""
        name = url.hostname.removeprefix("www.")
        return format_html(
            "<a href='{url}' target='_blank'>{name}</a>", url=obj.homepage, name=name
        )

    @admin.display(description="Mutter", ordering="mutter", boolean=True)
    def has_mutter(self, obj: Anbieter) -> bool:
        return bool(obj.mutter)

    @admin.display(description="Reseller", ordering="sells_from", boolean=True)
    def has_sells_from(self, obj: Anbieter) -> bool:
        return bool(obj.sells_from)

    @admin.display(description="100% Öko", ordering="nur_oeko", boolean=True)
    def ee_only(self, obj: Anbieter) -> bool:
        return obj.nur_oeko

    @admin.display(description="zusatz.", ordering="zusaetzlichkeit", boolean=True)
    def additional(self, obj: Anbieter) -> bool:
        return obj.zusaetzlichkeit

    @admin.display(description="unabh.", ordering="unabhaengigkeit", boolean=True)
    def independent(self, obj: Anbieter) -> bool:
        return obj.unabhaengigkeit

    @admin.display(description="💰", ordering="money_for_ee_only", boolean=True)
    def no_bad_money(self, obj: Anbieter) -> bool:
        return obj.money_for_ee_only

    @admin.display(description="📬", boolean=True)
    def survey_answered(self, obj: Anbieter) -> bool:
        return obj.survey_answered

    @admin.display(description="Umfrage 2024 (📬)")
    def survey_answered_field(self, obj: Anbieter) -> str:
        if obj.survey_access is None:
            return "Keine Umfrage versendet"
        survey_access: SurveyAccess = obj.survey_access
        if survey_access.current_revision > 1:
            return format_html(
                "📬 <a href='{url}' target='_blank'>Umfrage</a> zu {fill_status} beantwortet",
                url=survey_access.get_absolute_url(),
                fill_status=f"{survey_access.survey._fill_status:.1f}%",
            )
        return "📭 Umfrage nicht beantwortet"

    @admin.display(description="👍", boolean=True)
    def ist_empfohlen(self, obj: Anbieter) -> bool:
        return obj.ist_empfohlen

    @admin.display(description="Empfohlen 2024 (👍)", boolean=True)
    def ist_empfohlen_field(self, obj: Anbieter) -> bool:
        return obj.ist_empfohlen

    @admin.display(description="Status")
    def status_ro(self, obj: Anbieter) -> str:
        return STATUS_CHOICES.get(obj.status, f"{obj.status} - ?")

    def such_links(self, obj: Anbieter) -> str:
        return format_html(
            """
            <a href="https://www.google.com/search?q={name}", target="_blank">
                    Google Firmenname</a>, <br />
            <a href="https://www.google.com/search?q={name}+Stromkennzeichnung", target="_blank">
                    Google Stromkennzeichnung</a>, <br />
            <a href="https://www.northdata.de/{name}", target="_blank">
                    North Data</a>, <br />
            <a href="https://de.wikipedia.org/w/index.php?search={name}", target="_blank">
                    Wikipedia</a>, <br />
            """,
            name=obj.name,
        )

    def scrape_info(self, obj: Anbieter) -> str:
        result = ""
        for elm in (
            obj.rowo_2019,
            obj.oekotest,
            obj.ok_power,
            obj.stromauskunft,
            obj.verivox,
        ):
            if elm:
                result += elm.details
        return mark_safe(result)

    readonly_fields = (
        "scrape_info",
        "such_links",
        "last_updated",
        "created_at",
        "survey_answered",
        "ist_empfohlen",
        "survey_answered_field",
        "ist_empfohlen_field",
        "status_ro",
    )

    fieldsets = [
        (
            None,
            {
                "fields": [
                    "name",
                    "active",
                    "german_wide",
                    "mutter",
                    "sells_from",
                    "status_ro",
                    ("last_updated", "created_at"),
                ]
            },
        ),
        (
            "Kontakt",
            {
                "fields": [
                    "street",
                    ("plz", "city"),
                    "phone",
                    "fax",
                    "note",
                    "mail",
                ]
            },
        ),
        (
            "Kontext",
            {
                "fields": [
                    "scrape_info",
                    "such_links",
                    "homepage",
                    "north_data",
                    "wikipedia",
                ],
                "description": "Hilfreiche Infos für die Recherche",
            },
        ),
        (
            "Prüfung",
            {
                "fields": [
                    "kennzeichnung_url",
                    "ee_anteil",
                    "nur_oeko",
                    "zusaetzlichkeit",
                    "unabhaengigkeit",
                    "money_for_ee_only",
                    "survey_answered_field",
                    "ist_empfohlen_field",
                    "begruendung",
                    "begruendung_extern",
                ]
            },
        ),
        (
            "Scrape Referenz",
            {
                "fields": [
                    "rowo_2019",
                    "oekotest",
                    "ok_power",
                    "stromauskunft",
                    "verivox",
                ],
                "description": "Ändern der Scrape Referenzen",
                "classes": ["collapse"],
            },
        ),
        ("Status", {"fields": ["status"]}),
    ]

    def save_model(
        self, request: HttpRequest, obj: Anbieter, form: forms.Form, change: bool
    ) -> None:
        super().save_model(request, obj, form, change)
        # clean should take care that name isn't used already
        if obj.name not in obj.names.values_list("name", flat=True):
            AnbieterName.objects.update_or_create(name=obj.name, anbieter=obj)

    def has_delete_permission(self, request, obj=None):  # noqa ARG002
        return False


@admin.register(UmfrageVersendung2024)
class UmfrageVersendung2024Admin(AnbieterAdmin):
    actions = ["send_survey_email"]

    list_display = (
        "obj_id",
        "name",
        "umfrage",
        "filled",
        "revision",
        "german_wide",
        "has_mutter",
        "has_sells_from",
        "mail_status",
        "mail",
        "ee_only",
        "additional",
        "independent",
        "no_bad_money",
    )
    list_filter = [
        "german_wide",
        ("mutter", admin.EmptyFieldListFilter),
        ("sells_from", admin.EmptyFieldListFilter),
        "mail_status",
        "nur_oeko",
        "zusaetzlichkeit",
        "unabhaengigkeit",
        "money_for_ee_only",
    ]

    inlines = [AnbieterNameInline, SurveyAccessInline]

    @admin.action(description="Sende Mail")
    def send_survey_email(self, request: HttpRequest, queryset):
        obj: UmfrageVersendung2024
        queryset = queryset.select_related("anbieter__survey_access")
        already_sent = 0
        retried = 0
        sent = 0
        failed = 0

        try:
            subject_template = JinjaTemplate(
                Template.objects.get(name=TemplateNames.SURVEY2024_SUBJECT).template
            )
            text_template = JinjaTemplate(
                Template.objects.get(name=TemplateNames.SURVEY2024_TXT).template
            )
            html_template = JinjaTemplate(
                Template.objects.get(name=TemplateNames.SURVEY2024_HTML).template
            )
        except Exception as e:
            self.message_user(
                request,
                f"Error getting templates {type(e).__name__}: {e}.",
                level="error",
            )
            return

        for obj in queryset:
            if obj.mail_status is True:
                already_sent += 1
                continue

            try:
                subject = subject_template.render(obj=obj)
                message = text_template.render(obj=obj)
                html = html_template.render(obj=obj)
                send_mail(
                    subject,
                    message,
                    None,  # Uses DEFAULT_FROM_EMAIL
                    [obj.mail],
                    fail_silently=False,
                    html_message=html,
                )
            except Exception as e:
                failed += 1
                obj.mail_status = False
                obj.mail_details = (
                    f"{type(e).__name__}: {e}\n\n{traceback.format_exc()}"
                )
            else:
                if obj.mail_status is None:
                    sent += 1
                else:
                    retried += 1
                obj.mail_status = True
                obj.sent_date = timezone.now()
                obj.mail_details = ""
            obj.save()

        self.message_user(
            request,
            f"Finished sending: {already_sent=} {sent=} {retried=} {failed=}",
            level="info",
        )

    @admin.display(ordering="survey_access__survey___fill_status")
    def filled(self, obj: UmfrageVersendung2024) -> str:
        return f"{obj.survey_access.survey._fill_status} %"

    @admin.display(description="Rev", ordering="survey_access__current_revision")
    def revision(self, obj: UmfrageVersendung2024) -> str:
        return str(obj.survey_access.current_revision)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        qs = super().get_queryset(request)
        return qs.select_related("survey_access").select_related(
            "survey_access__survey"
        )

    def umfrage(self, obj: UmfrageVersendung2024) -> str:
        url = obj.survey_access.get_absolute_url()
        return format_html("<a href='{url}'>Umfrage</a>", url=url)

    def get_readonly_fields(
        self,
        request: HttpRequest,  # noqa: ARG002
        obj: UmfrageVersendung2024 = None,  # noqa: ARG002
    ) -> tuple[str, ...]:
        orig = list(AnbieterAdmin.readonly_fields)
        orig.extend(["filled", "revision"])
        return tuple(orig)

    def get_fieldsets(
        self,
        request: HttpRequest,  # noqa: ARG002
        obj: UmfrageVersendung2024 | None = None,  # noqa: ARG002
    ):
        fs = list(copy.deepcopy(AnbieterAdmin.fieldsets))
        fs.append(
            (
                "Umfrage Versand",
                {"fields": ("sent_date", "mail_status", "mail_details")},
            )
        )
        return fs
