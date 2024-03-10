import sys

from avaris.cli import entrypoint
from avaris.utils.logging import get_logger

logger = get_logger()


if __name__ == "__main__":
    args = sys.argv[1:]
    entrypoint(args)
