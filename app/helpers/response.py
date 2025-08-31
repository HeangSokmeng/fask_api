from typing import Any, Dict, Optional


def response(success: bool, code: int, message: str, data: Any = None, pagination: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {
        "result": success,
        "code": code,
        "message": message,
        "data": data if data is not None else [],
        "pagination": pagination
    }


def success_response(message: str = "Success", data: Any = None, code: int = 200, pagination: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return response(success=True, code=code, message=message, data=data, pagination=pagination)


def error_response(message: str, code: int = 400, data: Any = None) -> Dict[str, Any]:
    return response(success=False, code=code, message=message, data=data)


def paginated_response(data: Any, total: int, page: int, per_page: int, message: str = "Success") -> Dict[str, Any]:
    total_pages = (total + per_page - 1) // per_page  # Ceiling division

    pagination = {
        "current_page": page,
        "per_page": per_page,
        "total_items": total,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }
    return success_response(message=message, data=data, pagination=pagination)
