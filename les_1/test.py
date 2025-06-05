import asyncio
import logging
import sys

from os import getenv
from sqlite3 import IntegrityError

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from sqlalchemy import create_engine, Column, Integer, BigInteger, String
from sqlalchemy.orm import declarative_base, Session
from dotenv import load_dotenv

load_dotenv()
TOKEN = getenv("BOT_TOKEN")

# SQLAlchemy sozlamalari
db_url = 'postgresql://postgres:1234@localhost:5432/users_db'
engine = create_engine(db_url)
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
        return (f'{self.__class__.__name__}({self.id}, {self.chat_id}, {self.first_name!r}, {self.last_name!r},'
                f' {self.username!r}, {self.phone!r}, {self.email}, {self.address})')

Base.metadata.create_all(bind=engine)


dp = Dispatcher(storage=MemoryStorage())


# Holatlar (Finite State Machine)
class RegisterForm(StatesGroup):
    first_name = State()
    last_name = State()
    username = State()
    phone = State()
    email = State()
    address = State()

# Start buyrug‘i
@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer("Salom! Ro‘yxatdan o‘tish uchun ismingizni kiriting:")
    await state.set_state(RegisterForm.first_name)

# Ism
@dp.message(RegisterForm.first_name)
async def process_first_name(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await message.answer("Familiyangizni kiriting:")
    await state.set_state(RegisterForm.last_name)

# Familiya
@dp.message(RegisterForm.last_name)
async def process_last_name(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await message.answer("Telegram username'ingizni kiriting (masalan, @username):")
    await state.set_state(RegisterForm.username)

# Username
@dp.message(RegisterForm.username)
async def process_username(message: Message, state: FSMContext):
    await state.update_data(username=message.text)
    await message.answer("Telefon raqamingizni kiriting (masalan, +998901234567):")
    await state.set_state(RegisterForm.phone)

# Telefon
@dp.message(RegisterForm.phone)
async def process_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Email manzilingizni kiriting:")
    await state.set_state(RegisterForm.email)

# Email
@dp.message(RegisterForm.email)
async def process_email(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.answer("Yashash manzilingizni kiriting:")
    await state.set_state(RegisterForm.address)

# Manzil va ma'lumotlarni saqlash
@dp.message(RegisterForm.address)
async def process_address(message: Message, state: FSMContext):
    data = await state.get_data()
    data['address'] = message.text
    data['chat_id'] = message.from_user.id

    # Ma'lumotlarni bazaga saqlash
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
        except IntegrityError as e:
            await message.answer("Xato: Bu chat ID allaqachon ro'yxatdan o'tgan!")
        except Exception as e:
            print(e)
            await message.answer(f"Xato yuz berdi: {str(e)}")

    # Holatni tozalash
    await state.clear()



async def main():
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())


