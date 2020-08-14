from typing import Union, Dict, Any, List


def raise_(err: BaseException) -> BaseException:
    raise err


SanitizeObject = Union[Dict[Any, Any], List[Any]]


def sanitize_objects(source: SanitizeObject, affected: SanitizeObject) -> SanitizeObject:
    for key, value in list(affected.items()) if isinstance(affected, dict) else enumerate(affected):
        if not isinstance(affected, list) and key not in source:
            affected.pop(key)
        elif isinstance(value, (dict, list)):
            affected[key] = sanitize_objects(source[key], value)
    return affected
