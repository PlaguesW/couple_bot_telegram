from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    """Состояния для регистрации пользователя"""
    waiting_for_name = State()


class CoupleStates(StatesGroup):
    """Состояния для работы с парами"""
    waiting_for_invite_code = State()
    waiting_for_confirmation = State()


class DateProposalStates(StatesGroup):
    """Состояния для предложения свидания"""
    selecting_category = State()
    selecting_idea = State()
    confirming_proposal = State()
    waiting_for_custom_date = State()


class IdeaStates(StatesGroup):
    """Состояния для работы с идеями"""
    creating_title = State()
    creating_description = State()
    creating_category = State()
    browsing_ideas = State()


class ResponseStates(StatesGroup):
    """Состояния для ответов на предложения"""
    responding_to_proposal = State()
    adding_comment = State()