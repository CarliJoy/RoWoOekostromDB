import django.db.models as models
from django.core import validators
from django.utils.translation import gettext as _
from localflavor.de.forms import DEZipCodeField

PLZ_LENGTH = 5  # length of a German postal code


class PostleitzahlField(models.CharField):
    """
    A database field that represents a german postal code
    """

    def __init__(self, *args, **kwargs):
        if kwargs.get("max_length", PLZ_LENGTH) < PLZ_LENGTH:
            raise ValueError(
                f"Length for a german postal code needs to be at least "
                f"{PLZ_LENGTH} characters!"
            )
        kwargs.setdefault("max_length", 5)
        super().__init__(*args, **kwargs)
        self.validators.append(
            validators.RegexValidator(
                regex=DEZipCodeField().regex, message=_("Invalid German PLZ code.")
            )
        )

    def formfield(self, **kwargs):
        kwargs["form_class"] = DEZipCodeField
        return super().formfield(**kwargs)
