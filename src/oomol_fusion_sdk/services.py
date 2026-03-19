from __future__ import annotations

from typing import Any, Callable, Dict

from .registry import ACTION_SHORTCUTS, TASK_SHORTCUTS


class ActionGroup:
    pass


def create_task_shortcuts(client: Any) -> Dict[str, Any]:
    shortcuts: Dict[str, Any] = {}
    for python_name, camel_name, service in TASK_SHORTCUTS:
        resource = client.task(service)
        shortcuts[python_name] = resource
        shortcuts[camel_name] = resource
    return shortcuts


def create_action_shortcuts(client: Any) -> Dict[str, Any]:
    shortcuts: Dict[str, Any] = {}
    for python_group_name, camel_group_name, actions in ACTION_SHORTCUTS:
        group = ActionGroup()
        for python_name, camel_name, key in actions:
            def invoker(request: Any = None, options: Any = None, action_key: str = key) -> Any:
                return client.action(action_key, request, options)

            setattr(group, python_name, invoker)
            setattr(group, camel_name, invoker)
        shortcuts[python_group_name] = group
        shortcuts[camel_group_name] = group
    return shortcuts

