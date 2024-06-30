import asyncio
import aiosqlite
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters.command import Command
from aiogram.enums import ParseMode

bot = Bot(token="token")
dispatcher = Dispatcher()


# Database initialization
async def init_db():
    async with aiosqlite.connect('todo.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY,
                description TEXT NOT NULL,
                priority INTEGER NOT NULL
            )
        ''')
        await db.commit()


# Command to start the conversation
@dispatcher.message(Command("start"))
async def handle_message(message: types.Message):
    await message.answer("Conversation started")


# Command to add a new to-do item
@dispatcher.message(Command("add"))
async def add_todo_command(message: types.Message):
    await message.answer("Please send the description and priority (1-10) in the format: description,priority")


# Handler to process the to-do item input
@dispatcher.message(F.text.regexp(r'^.+,\d{1,2}$'))
async def add_todo_handler(message: types.Message):
    description, priority = message.text.split(',')
    priority = int(priority)

    if 1 <= priority <= 10:
        async with aiosqlite.connect('todo.db') as db:
            await db.execute('INSERT INTO todos (description, priority) VALUES (?, ?)', (description, priority))
            await db.commit()
        await message.answer(f'To-do item added: {description} with priority {priority}')
    else:
        await message.answer('Priority must be an integer between 1 and 10')


# Command to list all to-do items
@dispatcher.message(Command("list"))
async def list_todos(message: types.Message):
    async with aiosqlite.connect('todo.db') as db:
        async with db.execute('SELECT description, priority FROM todos ORDER BY priority ASC') as cursor:
            todos = await cursor.fetchall()

    if todos:
        response = "\n".join(
            [f"{idx + 1}. {description} (Priority: {priority})" for idx, (description, priority) in enumerate(todos)])
    else:
        response = "No to-do items found."

    await message.answer(response)


# Command to delete a to-do item by its ID
@dispatcher.message(Command("delete"))
async def delete_todo_command(message: types.Message):
    await message.answer("Please send the ID of the to-do item to delete")


@dispatcher.message(F.text.regexp(r'^\d+$'))
async def delete_todo_handler(message: types.Message):
    todo_id = int(message.text)

    async with aiosqlite.connect('todo.db') as db:
        cursor = await db.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
        await db.commit()
        if cursor.rowcount == 0:
            await message.answer(f'No to-do item with ID {todo_id} found.')
        else:
            await message.answer(f'To-do item with ID {todo_id} deleted.')


# Handlers for specific text messages
@dispatcher.message(F.text == "HELLO!!!")
async def handle_expressive(message: types.Message):
    await message.answer(
        f"Hello, <i>{message.from_user.first_name}!</i>",
        parse_mode=ParseMode.HTML
    )


@dispatcher.message(F.text == "hello")
async def handle_unknow(message: types.Message):
    await message.answer("Hello!")


@dispatcher.message(F.text)
async def handle_unknow(message: types.Message):
    await message.answer("Didn't get you")


async def main():
    await init_db()
    await dispatcher.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
