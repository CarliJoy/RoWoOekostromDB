import uuid


def generate_unique_code() -> str:
    return uuid.uuid4().hex[:32]
