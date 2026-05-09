"""统一分页工具函数。"""

from utils.exceptions import ServiceException


def paginate(items, total, page, size):
    """构建统一分页响应。

    Args:
        items: 当前页数据列表
        total: 总记录数
        page: 当前页码（从1开始）
        size: 每页大小，若为 None 表示不分页

    Returns:
        dict: {items, total, page, size, total_pages[, has_next]}
    """
    if size is None:
        return {
            'items': items,
            'total': total,
            'page': page,
            'size': total,
            'total_pages': 1,
        }

    total_pages = (total + size - 1) // size if total else 0
    return {
        'items': items,
        'total': total,
        'page': page,
        'size': size,
        'total_pages': total_pages,
        'has_next': page < total_pages,
    }


def normalize_pagination(page, size):
    """校验并标准化分页参数。

    Args:
        page: 当前页码
        size: 每页大小，若为 None 表示不分页

    Returns:
        tuple: (page, size, offset)

    Raises:
        ServiceException: 参数不合法时
    """
    if size is None:
        return page, None, None

    if page < 1 or size < 1:
        raise ServiceException('分页参数不合法', code=6001)

    return page, size, (page - 1) * size
