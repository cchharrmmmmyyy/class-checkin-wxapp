from typing import List, Optional
from models.class_model import Class
from .base_dao import BaseDAO


class ClassDAO(BaseDAO[Class]):
    def __init__(self):
        super().__init__(Class, 'classes', 'class_name')

    def create(self, data: dict) -> str:
        super().create(data)
        return data['class_name']

    def update(self, class_name: str, data: dict) -> bool:
        return super().update(class_name, data)
