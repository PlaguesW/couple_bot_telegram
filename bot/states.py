from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_gender = State()


class PairStates(StatesGroup):
    waiting_for_partner_username = State()
    waiting_for_invitation_response = State()


class EventStates(StatesGroup):
    waiting_for_event_title = State()
    waiting_for_event_description = State()
    waiting_for_event_date = State()
    waiting_for_partner_response = State()