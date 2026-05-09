"""AdminService 组织架构 CRUD 行为测试（拆前验证）。"""

import pytest
from services.admin_service import AdminService


class TestCampusCRUD:
    """校区 CRUD。"""

    def test_create_campus(self, seed_basic_org):
        result = AdminService.save_campus(campus_id=None, name='新校区', address='新地址')
        assert result['success'] is True
        assert 'id' in result

    def test_create_campus_without_name_raises(self, seed_basic_org):
        from utils.exceptions import ServiceException
        with pytest.raises(ServiceException):
            AdminService.save_campus(campus_id=None, name='', address='')

    def test_list_campuses(self, seed_basic_org):
        result = AdminService.list_campuses(page=1, size=20)
        assert result['total'] >= 1
        assert len(result['items']) >= 1
        assert result['items'][0]['name'] == '测试校区'

    def test_update_campus(self, seed_basic_org):
        result = AdminService.save_campus(campus_id=1, name='更新校区', address='更新地址')
        assert result['success'] is True

    def test_delete_campus(self, seed_basic_org):
        result = AdminService.delete_campus(1)
        assert result['success'] is True

    def test_delete_nonexistent_campus_raises(self, seed_basic_org):
        from utils.exceptions import ServiceException
        with pytest.raises(ServiceException):
            AdminService.delete_campus(999)


class TestDepartmentCRUD:
    """院系 CRUD。"""

    def test_create_department(self, seed_basic_org):
        result = AdminService.save_department(department_id=None, campus_id=1, name='新学院', code='NC')
        assert result['success'] is True

    def test_create_department_without_campus_raises(self, seed_basic_org):
        from utils.exceptions import ServiceException
        with pytest.raises(ServiceException):
            AdminService.save_department(department_id=None, campus_id=None, name='学院', code='C')

    def test_list_departments(self, seed_basic_org):
        result = AdminService.list_departments(campus_id=1, page=1, size=20)
        assert result['total'] >= 1

    def test_delete_department(self, seed_basic_org):
        result = AdminService.delete_department(1)
        assert result['success'] is True


class TestMajorCRUD:
    """专业 CRUD。"""

    def test_create_major(self, seed_basic_org):
        result = AdminService.save_major(major_id=None, department_id=1, name='新专业', code='NP')
        assert result['success'] is True

    def test_list_majors(self, seed_basic_org):
        result = AdminService.list_majors(department_id=1, page=1, size=20)
        assert result['total'] >= 1

    def test_delete_major(self, seed_basic_org):
        result = AdminService.delete_major(1)
        assert result['success'] is True


class TestGradeCRUD:
    """年级 CRUD。"""

    def test_create_grade(self, seed_basic_org):
        result = AdminService.save_grade(grade_id=None, major_id=1, year=2025, name='2025级')
        assert result['success'] is True

    def test_create_grade_without_major_raises(self, seed_basic_org):
        from utils.exceptions import ServiceException
        with pytest.raises(ServiceException):
            AdminService.save_grade(grade_id=None, major_id=None, year=None, name='')

    def test_list_grades(self, seed_basic_org):
        result = AdminService.list_grades(major_id=1, page=1, size=20)
        assert result['total'] >= 1

    def test_delete_grade(self, seed_basic_org):
        result = AdminService.delete_grade(1)
        assert result['success'] is True


class TestClassCRUD:
    """班级 CRUD。"""

    def test_create_class(self, seed_basic_org):
        result = AdminService.save_class(target_class_name=None, class_name='软件2401', grade_id=1)
        assert result['success'] is True

    def test_create_class_without_grade_raises(self, seed_basic_org):
        from utils.exceptions import ServiceException
        with pytest.raises(ServiceException):
            AdminService.save_class(target_class_name=None, class_name='软件2401', grade_id=None)

    def test_list_classes(self, seed_basic_org):
        result = AdminService.list_classes(page=1, size=20)
        assert result['total'] >= 1
        assert result['items'][0]['class_name'] == '计算机2401'

    def test_update_class(self, seed_basic_org):
        result = AdminService.save_class(target_class_name='计算机2401', class_name='计算机2401-新', grade_id=1)
        assert result['success'] is True

    def test_delete_class(self, seed_basic_org):
        result = AdminService.delete_class('计算机2401')
        assert result['success'] is True

    def test_delete_nonexistent_class_raises(self, seed_basic_org):
        from utils.exceptions import ServiceException
        with pytest.raises(ServiceException):
            AdminService.delete_class('不存在班级')
