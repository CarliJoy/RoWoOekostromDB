"""
Example file for hosting productively.
Copy/Rename this file to local.py
The secret key will be added automatically in the first run.
Please change the settings accordingly to the Django Documentation
"""

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "MysqlDatabase",
        "USER": "MyqlUser",
        "PASSWORD": "MysqlPassword",
        "TEST": {"NAME": "MysqlDatabase",},
    }
}

ALLOWED_HOSTS = ["subdomain.example.com", "127.0.0.1", "localhost"]
STATIC_ROOT = "/var/www/static"
# MEDIA_ROOT = "/var/www/media"
# STATIC_URL = "/static/"
# MEDIA_URL = "/media/"
