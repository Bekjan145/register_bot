import asyncio
import logging
import sys

from os import getenv
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from sqlalchemy.exc import IntegrityError
from data.config import db_user, password, host, port, db_name
from sqlalchemy import create_engine, Column, Integer, BigInteger, String
from sqlalchemy.orm import declarative_base, Session
from dotenv import load_dotenv

load_dotenv()
TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher(storage=MemoryStorage())

pg_url = f"postgresql+psycopg2://{db_user}:{password}@{host}:{port}/{db_name}"
engine = create_engine(pg_url)
Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    username = Column(String)
    phone = Column(String)
    email = Column(String)
    address = Column(String)

    def __repr__(self):
        return (f"Foydalanuvchi ma'lumotlari:\n"
                        f"Ism: {self.first_name}\n"
                        f"Familiya: {self.last_name}\n"
                        f"Username: {self.username}\n"
                        f"Telefon: {self.phone}\n"
                        f"Email: {self.email}\n"
                        f"Manzil: {self.address}")



Base.metadata.create_all(bind=engine)

class RegisterFrom(StatesGroup):
    first_name = State()
    last_name = State()
    username = State()
    phone = State()
    email = State()
    address = State()

class EditForm(StatesGroup):
    field = State()
    value = State()

@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await message.answer("Salom! Ro`yxatdan o`tish uchun ismingizni kiriting:")
    await state.set_state(RegisterFrom.first_name)

@dp.message(RegisterFrom.first_name)
async def process_first_name(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await message.answer("Familiyangizni kiriting:")
    await state.set_state(RegisterFrom.last_name)

@dp.message(RegisterFrom.last_name)
async def process_last_name(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await message.answer("Telegram username'ingizni kiritng:")
    await state.set_state(RegisterFrom.username)

@dp.message(RegisterFrom.username)
async def process_username(message: Message, state: FSMContext):
    await state.update_data(username=message.text)
    await message.answer("Telefon raqamingizni kiritng:")
    await state.set_state(RegisterFrom.phone)

@dp.message(RegisterFrom.phone)
async def process_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Email manzilingizni kiritng:")
    await state.set_state(RegisterFrom.email)

@dp.message(F.text.regexp(r'[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+'), RegisterFrom.email)
async def process_email(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.answer("Yashash manzilingizni kiritng:")
    await state.set_state(RegisterFrom.address)


@dp.message(RegisterFrom.address)
async def process_address(message: Message, state: FSMContext):
     data = await state.get_data()
     data['address'] = message.text
     data['chat_id'] = message.from_user.id

     with Session(bind=engine) as session:
         try:
             user = Users(
                 chat_id=data['chat_id'],
                 first_name=data['first_name'],
                 last_name=data['last_name'],
                 username=data['username'],
                 phone=data['phone'],
                 email=data['email'],
                 address=data['address']
             )
             session.add(user)
             session.commit()
             await message.answer("Ro‘yxatdan o‘tish muvaffaqiyatli yakunlandi!")
         except IntegrityError:
             await message.answer("Xato: Bu chat ID allaqachon ro‘yxatdan o‘tgan!")
         except Exception as e:
             await message.answer(f"Xato yuz berdi: {str(e)}")

     await state.clear()

@dp.message(Command("view"))
async def cmd_view(message: Message):
    chat_id = message.from_user.id
    with Session(bind=engine) as session:
        user = session.query(Users).filter_by(chat_id=chat_id).first()
        if user:
            await message.answer(str(user))
        else:
            await message.answer("Siz hali ro‘yxatdan o‘tmagansiz!")

@dp.message(Command("edit"))
async def cmd_edit(message: Message, state: FSMContext):
    chat_id = message.from_user.id
    with Session(bind=engine) as session:
        user = session.query(Users).filter_by(chat_id=chat_id).first()
        if not user:
            await message.answer("Siz hali ro‘yxatdan o‘tmagansiz!")
            return

    await message.answer("Qaysi ma'lumotni o'zgartirmoqchisiz? (first_name, last_name, username, phone, email, address)")
    await state.set_state(EditForm.field)

@dp.message(EditForm.field)
async def process_edit_field(message: Message, state: FSMContext):
    field = message.text.lower()
    if field not in ["first_name", "last_name", "username", "phone", "email", "address"]:
        await message.answer("Noto‘g‘ri maydon! Iltimos, quyidagilardan birini tanlang: "
                            "first_name, last_name, username, phone, email, address")
        return
    await state.update_data(field=field)
    await message.answer(f"Yangi {field} qiymatni kiriting:")
    await state.set_state(EditForm.value)

@dp.message(EditForm.value)
async def process_edit_value(message: Message, state: FSMContext):
    data = await state.get_data()
    field = data['field']
    value = message.text
    chat_id = message.from_user.id

    with Session(bind=engine) as session:
        user = session.query(Users).filter_by(chat_id=chat_id).first()
        if user:
            try:
                setattr(user, field, value)
                session.commit()
                await message.answer(f"{field} muvaffaqiyatli o‘zgartirildi!")
            except Exception as e:
                await message.answer(f"Xato yuz berdi: {str(e)}")
        else:
            await message.answer("Foydalanuvchi topilmadi!")
    await state.clear()

@dp.message(Command("delete"))
async def cmd_delete(message: Message):
    chat_id = message.from_user.id
    with Session(bind=engine) as session:
        user = session.query(Users).filter_by(chat_id=chat_id).first()
        if user:
            session.delete(user)
            session.commit()
            await message.answer("Foydalanuvchi ma'lumotlari o‘chirildi!")
        else:
            await message.answer("Siz hali ro‘yxatdan o‘tmagansiz!")


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())


















