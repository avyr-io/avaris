from typing import Type, Dict

task_registry = {}


def get_registry() -> Dict[str, Type['TaskExecutor']]:
    return task_registry
