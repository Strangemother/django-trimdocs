from django.conf import settings
import os

def pytest_configure():
    settings.configure(DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join("db.sqlite3"),
    }
})