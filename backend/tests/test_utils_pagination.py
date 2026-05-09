"""测试 utils/pagination.py 分页工具。"""

import pytest


class TestPaginate:
    """测试 paginate() 函数。"""

    def test_basic_pagination(self):
        from utils.pagination import paginate
        items = [{'id': 1}, {'id': 2}, {'id': 3}]
        result = paginate(items, total=10, page=1, size=3)
        assert result == {
            'items': items,
            'total': 10,
            'page': 1,
            'size': 3,
            'total_pages': 4,
            'has_next': True,
        }

    def test_last_page_no_next(self):
        from utils.pagination import paginate
        result = paginate(items=[], total=9, page=3, size=3)
        assert result['has_next'] is False
        assert result['total_pages'] == 3

    def test_size_none_no_pagination(self):
        from utils.pagination import paginate
        items = [{'id': 1}, {'id': 2}]
        result = paginate(items, total=2, page=1, size=None)
        assert result == {
            'items': items,
            'total': 2,
            'page': 1,
            'size': 2,
            'total_pages': 1,
        }
        assert 'has_next' not in result

    def test_empty_items(self):
        from utils.pagination import paginate
        result = paginate(items=[], total=0, page=1, size=20)
        assert result == {
            'items': [],
            'total': 0,
            'page': 1,
            'size': 20,
            'total_pages': 0,
            'has_next': False,
        }

    def test_single_page(self):
        from utils.pagination import paginate
        result = paginate(items=[{'id': 1}], total=1, page=1, size=20)
        assert result['total_pages'] == 1
        assert result['has_next'] is False

    def test_exact_page_boundary(self):
        from utils.pagination import paginate
        # total=20, size=10 -> total_pages=2
        items_page1 = [{'id': i} for i in range(1, 11)]
        result = paginate(items_page1, total=20, page=1, size=10)
        assert result['total_pages'] == 2
        assert result['has_next'] is True


class TestNormalizePagination:
    """测试 normalize_pagination() 函数。"""

    def test_normal_valid(self):
        from utils.pagination import normalize_pagination
        page, size, offset = normalize_pagination(1, 20)
        assert page == 1
        assert size == 20
        assert offset == 0

    def test_page_2_offset_20(self):
        from utils.pagination import normalize_pagination
        page, size, offset = normalize_pagination(2, 20)
        assert page == 2
        assert size == 20
        assert offset == 20

    def test_size_none_returns_none_offset(self):
        from utils.pagination import normalize_pagination
        page, size, offset = normalize_pagination(1, None)
        assert page == 1
        assert size is None
        assert offset is None

    def test_page_less_than_1_raises(self):
        from utils.pagination import normalize_pagination
        from utils.exceptions import ServiceException
        with pytest.raises(ServiceException):
            normalize_pagination(0, 20)

    def test_size_less_than_1_raises(self):
        from utils.pagination import normalize_pagination
        from utils.exceptions import ServiceException
        with pytest.raises(ServiceException):
            normalize_pagination(1, 0)
