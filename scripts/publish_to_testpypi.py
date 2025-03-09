#!/usr/bin/env python3
"""
Script to publish the package to Test PyPI.
"""

import os
import subprocess
import sys


def main():
    """
    Build and publish the package to Test PyPI.
    """
    print("Building the package...")
    subprocess.run(["poetry", "build"], check=True)

    print("Publishing to Test PyPI...")
    subprocess.run(["poetry", "config", "repositories.testpypi", "https://test.pypi.org/legacy/"], check=True)

    # Check if the user provided a token
    token = os.environ.get("TESTPYPI_TOKEN", "test")
    if not token:
        print("Error: TESTPYPI_TOKEN environment variable not set.")
        print("Please set it with: export TESTPYPI_TOKEN=your-token")
        return 1

    # Publish to Test PyPI
    try:
        subprocess.run([
            "poetry", "publish",
            "--repository", "testpypi",
            "--username", "__token__",
            "--password", token
        ], check=True)
        print("Successfully published to Test PyPI!")
    except subprocess.CalledProcessError as e:
        print(f"Error publishing to Test PyPI: {e}")
        return 1

    print("\nTo install the package from Test PyPI:")
    print("pip install -i https://test.pypi.org/simple/ pharma-papers")

    return 0


if __name__ == "__main__":
    sys.exit(main())