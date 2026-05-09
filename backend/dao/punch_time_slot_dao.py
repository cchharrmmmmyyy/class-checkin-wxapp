from models.punch_time_slot import PunchTimeSlot
from .base_dao import BaseDAO


class PunchTimeSlotDAO(BaseDAO[PunchTimeSlot]):
    def __init__(self):
        super().__init__(PunchTimeSlot, 'punch_time_slots', 'id')
