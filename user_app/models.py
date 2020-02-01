from django.db import models
from improved_user.model_mixins import AbstractUser


# Create your models here.
class User(AbstractUser):
    """A User model that extends the Improved User"""

    is_rowo = models.BooleanField(
        default=False, help_text="Is the User a Robin Wood member?"
    )
