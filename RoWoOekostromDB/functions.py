from os.path import join, dirname, abspath

from django.core.management.utils import get_random_secret_key


def generate_secret_key_and_write_to_local_py() -> None:
    key = get_random_secret_key()
    local_py_path = join(dirname(abspath(__file__)), "local.py")
    try:
        with open(local_py_path, "a") as f:
            f.write(
                f"\n# SECURITY WARNING: keep the secret key used in production secret!"
                f"\n# This secret key was automatically generated and should not be"
                f"\n# a part of the git."
                f'\nSECRET_KEY = "{key}"\n'
            )
    except OSError as e:
        raise EnvironmentError(
            f"Could could not write SECRET_KEY to '{local_py_path}': " f"{type(e)}: {e}"
        )
