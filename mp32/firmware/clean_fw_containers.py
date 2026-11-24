#!/usr/bin/env python3
"""Remove stale containers used by the firmware development image."""

import subprocess
import sys

FW_IMAGE = "mp32-esp-idf"
FW_CONTAINER = "mp32-dev-fw"


def docker_output(*args: str) -> list[str]:
    result = subprocess.run(
        ["docker", *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.splitlines()


def remove_named_container() -> None:
    container_ids = docker_output(
        "ps", "-aq", "--filter", f"name={FW_CONTAINER}"
    )

    for container_id in container_ids:
        names = docker_output(
            "inspect", "--format", "{{.Name}}", container_id
        )
        if names == [f"/{FW_CONTAINER}"]:
            print(f"Removing previous firmware container {FW_CONTAINER}...")
            subprocess.run(["docker", "rm", "-f", container_id], check=True)


def remove_image_containers() -> None:
    container_ids = docker_output(
        "ps", "-aq", "--filter", f"ancestor={FW_IMAGE}"
    )
    if container_ids:
        print("Removing previous firmware containers...")
        subprocess.run(["docker", "rm", "-f", *container_ids], check=True)


def main() -> int:
    try:
        remove_named_container()
        remove_image_containers()
    except subprocess.CalledProcessError as error:
        print(f"docker command failed: {error}", file=sys.stderr)
        return error.returncode or 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
