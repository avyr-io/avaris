import csv
import hashlib
import json
import os
import re

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union
import pytz
from flask import render_template_string
from pydantic import BaseModel



def parse_cron_schedule(schedule_str: str) -> Dict[str, str]:
    """
    Parses a cron schedule string or shortcut into a dictionary suitable for APScheduler.

    Args:
        schedule_str: A cron schedule string, e.g., "*/5 * * * *", or a shortcut like "@hourly".

    Returns:
        A dictionary with keys for second, minute, hour, day, month, day_of_week.
    """
    shortcuts = {
        "@yearly": "0 0 0 1 1 *",
        "@annually": "0 0 0 1 1 *",
        "@monthly": "0 0 0 1 * *",
        "@weekly": "0 0 0 * * 0",
        "@daily": "0 0 0 * * *",
        "@hourly": "0 0 * * * *",
    }

    schedule_str = shortcuts.get(schedule_str, schedule_str)
    parts = schedule_str.split()
    if len(parts) == 6:
        return {
            "second": parts[0],
            "minute": parts[1],
            "hour": parts[2],
            "day": parts[3],
            "month": parts[4],
            "day_of_week": parts[5],
        }
    elif len(parts) == 5:
        return {
            "second": "0",
            "minute": parts[0],
            "hour": parts[1],
            "day": parts[2],
            "month": parts[3],
            "day_of_week": parts[4],
        }
    else:
        raise ValueError(
            "Invalid cron schedule format. Expected 5 or 6 parts, or a recognized shortcut."
        )


def is_valid_cron_expression(expression: str) -> bool:
    """
    Validates a cron expression format.

    Args:
        expression: A string representing a cron expression.

    Returns:
        True if the expression is valid, False otherwise.
    """
    return bool(re.match(r"^(\d+|\*)( \d+|\*)( \d+|\*)( \d+|\*)( \d+|\*)$", expression))

# Your secret token

def generate_task_id(
    compendium_name: str, task_name: str, parameters: BaseModel
) -> str:
    """
    Generate a unique ID for a task based on its compendium name, task name, and parameters.

    :param compendium_name: The name of the compendium config.
    :param task_name: The name of the task config.
    :param parameters: A dictionary of task parameters.
    :return: A unique task ID.
    """
    params_string = str([compendium_name,task_name]+sorted(parameters.model_dump().items())) if parameters else ""

    # Create a hash of the parameters string
    params_hash = hashlib.sha256(params_string.encode()).hexdigest()[
        :16
    ]  # Take first 8 chars for brevity

    # Concatenate elements to form the ID
    task_id = f"{params_hash}"

    return task_id


def extract_data(
    log: Dict, keys: List[str], default_values: Dict[str, str]
) -> List[str]:
    """
    Extracts specified keys from a log dict, substituting defaults where necessary.

    Args:
        log: The log data as a dictionary.
        keys: The keys to extract from the log.
        default_values: Default values for keys that are not present in the log.

    Returns:
        A list of extracted values.
    """
    return [log.get(key, default_values.get(key, "")) for key in keys]


def read_from_json(json_file_name: str) -> Dict:
    """
    Reads data from a JSON file.

    Args:
        json_file_name: The name of the JSON file.

    Returns:
        The JSON data as a dictionary.
    """
    json_file_path = os.path.join(os.getcwd(), json_file_name)
    with open(json_file_path, "r") as json_file:
        return json.load(json_file)


def convert_from_unix_time(timestamp_unix: Optional[int]) -> Union[str, None]:
    """
    Converts a Unix timestamp to a human-readable string.

    Args:
        timestamp_unix: The Unix timestamp in milliseconds.

    Returns:
        A string representing the formatted date and time, or None if input is None.
    """
    if timestamp_unix is None:
        return None
    timestamp_seconds = timestamp_unix / 1000
    dt_object = datetime.fromtimestamp(timestamp_seconds)
    return dt_object.strftime("%Y-%m-%d %H:%M:%S")


def ensure_directory(path):
    """Ensure the directory exists, create it if it doesn't, then return the path."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def find_first_existing_directory(*paths):
    """Return the first existing directory from a list of paths, or None if none exist."""
    for path in paths:
        if path:
            p = Path(path)
            if p.is_dir():
                return p
    return None


def utc_to_local_time(timestamp_str: Optional[str]) -> str:
    """
    Converts a UTC timestamp string to local time string based on the TIMEZONE environment variable.

    Args:
        timestamp_str: The UTC timestamp string.

    Returns:
        The local time as a string.
    """
    if timestamp_str is None or timestamp_str == "No activity":
        return timestamp_str
    try:
        timestamp_utc = datetime.strptime(timestamp_str.strip(), "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        try:
            timestamp_utc = datetime.strptime(
                timestamp_str.strip(), "%Y-%m-%dT%H:%M:%S.%f%z"
            )
        except ValueError:
            try:
                timestamp_utc = datetime.strptime(
                    timestamp_str.strip(), "%Y-%m-%d %H:%M:%S %Z"
                )
            except ValueError:
                return timestamp_str
    local_tz = pytz.timezone(os.getenv("TIMEZONE", "UTC"))
    timestamp_local = timestamp_utc.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return timestamp_local.strftime("%Y-%m-%d %H:%M:%S")


def find_first_existing_file(*paths):
    """Return the first existing file path from a list of paths."""
    for path in paths:
        if path:
            p = Path(path)
            if p.exists() and p.is_file():
                return p
    return None


def csv_to_json(csv_file: str, json_file: str) -> None:
    """
    Converts data from a CSV file to a JSON file format.

    Args:
        csv_file: The file path of the CSV file.
        json_file: The file path for the output JSON file.
    """
    with open(csv_file, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        csv_data = list(reader)

    with open(json_file, "w") as jsonfile:
        json.dump(csv_data, jsonfile, indent=4)


def get_current_time_in_timezone() -> datetime:
    """
    Returns the current time adjusted to the timezone specified by the 'TIMEZONE' environment variable.
    Defaults to UTC if 'TIMEZONE' is not set or if an unknown/problematic timezone is specified.

    Returns:
        A datetime object representing the current time in the specified (or default) timezone.
    """
    timezone_str: str = os.getenv("TIMEZONE", "UTC")
    try:
        timezone = pytz.timezone(timezone_str)
    except pytz.UnknownTimeZoneError:
        print(
            f"Warning: Unknown timezone specified: '{timezone_str}'. Defaulting to UTC."
        )
        timezone = pytz.timezone("UTC")

    current_time_utc: datetime = datetime.utcnow()
    current_time_utc = current_time_utc.replace(
        tzinfo=pytz.utc
    )  # Attach UTC timezone information
    current_time_in_timezone: datetime = current_time_utc.astimezone(timezone)
    return current_time_in_timezone
