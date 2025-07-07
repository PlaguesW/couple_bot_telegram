from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from services.api_client import get_ideas, add_idea, update_idea, delete_idea
from keyboards.inline import idea_actions_keyboard

router = Router()

class IdeaStates(StatesGroup):
    title = State()
    description = State()
    edit_title = State()
    edit_description = State()

@router.message(F.text == "/ideas")
async def show_ideas(message: Message):
    ideas = await get_ideas(message.from_user.id)
    if not ideas:
        return await message.answer("На данный момент нет идей 😔")
    for idea in ideas:
        await message.answer(
            f"📝 *{idea['title']}*\n{idea['description']}",
            parse_mode="Markdown",
            reply_markup=idea_actions_keyboard(idea_id=idea['id'])
        )

@router.callback_query(F.data.startswith("idea_"))
async def idea_action_handler(callback: CallbackQuery, state: FSMContext):
    action, idea_id = callback.data.split(':')
    await state.update_data(idea_id=int(idea_id))
    if action == "idea_edit":
        await state.set_state(IdeaStates.edit_title)
        await callback.message.answer("Введите новый заголовок:")
    elif action == "idea_delete":
        await delete_idea(callback.from_user.id, int(idea_id))
        await callback.message.answer("Идея удалена ✅")
    await callback.answer()

@router.message(F.text == "/idea_add")
async def idea_add_start(message: Message, state: FSMContext):
    await state.set_state(IdeaStates.title)
    await message.answer("Введите заголовок идеи:")

@router.message(IdeaStates.title)
async def idea_add_desc(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(IdeaStates.description)
    await message.answer("Введите описание идеи:")

@router.message(IdeaStates.description)
async def idea_add_send(message: Message, state: FSMContext):
    data = await state.get_data()
    await add_idea(message.from_user.id, data["title"], message.text)
    await message.answer("Идея добавлена ✅")
    await state.clear()

@router.message(IdeaStates.edit_title)
async def idea_edit_title(message: Message, state: FSMContext):
    await state.update_data(new_title=message.text)
    await state.set_state(IdeaStates.edit_description)
    await message.answer("Теперь введите новое описание:")

@router.message(IdeaStates.edit_description)
async def idea_edit_desc(message: Message, state: FSMContext):
    data = await state.get_data()
    await update_idea(message.from_user.id, data["new_title"], message.text, data["idea_id"])
    await message.answer("Идея обновлена ✅")
    await state.clear()