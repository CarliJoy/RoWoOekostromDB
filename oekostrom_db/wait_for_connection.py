import os
import socket
import sys
import time
from typing import Final, Literal

TIMEOUT: Final[int] = 60


def check_tcp_port(
    host: str, port: int, timeout: float = 1
) -> Literal[True, "E\b", "."]:
    """
    Check if a TCP port is connectable.

    Args:
        host (str): The hostname or IP address to connect to.
        port (int): The port number to connect to.
        timeout (int, optional): The timeout for the connection attempt in seconds.

    Returns:
        bool: True if the port is connectable, False otherwise.
    """
    try:
        with socket.create_connection((host, port), timeout):
            return True
    except TimeoutError:
        return "."
    except OSError:
        return "E\b"


def wait_for_connection_or_die() -> None:
    try:
        host = os.environ["DB_HOST"]
        port = int(os.environ["DB_PORT"])
    except (ValueError, KeyError) as e:
        print(e.__class__.__name__, e)
        print("Failed to get valid DB_HOST or DB_PORT from env")
        sys.exit(64)

    print(f"Waiting for a TCP connection to {host}:{port}", end=" ")

    for _ in range(TIMEOUT):
        check = check_tcp_port(host, port)
        if check is True:
            print(" OK")
            return
        print(check, end="", flush=True)
        if check != ".":
            # if not timeout but error wait a second before trying again
            time.sleep(1)

    sys.exit(1)


if __name__ == "__main__":
    wait_for_connection_or_die()
