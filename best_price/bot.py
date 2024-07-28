import asyncio
import json
import re
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters.command import Command
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from auth_data import bot_token

bot = Bot(token=bot_token)
dispatcher = Dispatcher()


# Load products from JSON file
def load_products():
    with open('prices.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data['products']


# Save products to JSON file
def save_products(products):
    with open('prices.json', 'w', encoding='utf-8') as file:
        json.dump(products, file, indent=4)


# Generate the command list message
def get_command_list():
    return (
        "/start - Start a conversation\n"
        "/location - Show all locations\n"
        "/lowprices - Find the 3 lowest prices\n"
        "/delete - Delete product by ID\n"
        "/keyword - Find products by keyword\n"
        "/products_by_location - Find products by location"
    )


# Command to start the conversation
@dispatcher.message(Command("start"))
async def handle_message(message: types.Message):
    welcome_message = (
        "Welcome! Click a command below to interact with the bot:\n\n"
        f"{get_command_list()}"
    )
    await message.answer(welcome_message)


# Command to add a new product
@dispatcher.message(Command("add"))
async def add_product_command(message: types.Message):
    await message.answer("Please send the product details in the format: title,price")
    await message.answer(get_command_list())


# Command to list all commands
@dispatcher.message(Command("commands"))
async def list_commands(message: types.Message):
    await message.answer(f"Available commands:\n{get_command_list()}")


# Handler to process the product input
@dispatcher.message(F.text.regexp(r'^.+,\d+(\.\d+)?$'))
async def add_product_handler(message: types.Message):
    title, price = message.text.split(',')
    price = float(price)

    # Load the existing products
    products = load_products()

    # Add the new product
    products.append({
        'id': len(products) + 1,
        'title': title,
        'price': price
    })

    # Save the updated products
    save_products(products)

    await message.answer(f'Product added: {title} with price {price}')
    await message.answer(get_command_list())


# Command to list all products
@dispatcher.message(Command("list"))
async def list_products(message: types.Message):
    products = load_products()
    if products:
        response = "\n".join(
            [f"{product['id']}. {product['title']} (Price: {product['price']})" for product in products]
        )
    else:
        response = "No products found."
    await message.answer(response)
    await message.answer(get_command_list())


def escape_markdown(text):
    return re.sub(r'([!#\$%&\'\(\)\*\+,\-\.\/:;<=>\?@\[\\\]\^_`\{\|\}~])', r'\\\1', text)


# Split long messages into smaller parts
def split_message(text, max_length=4096):
    chunks = []
    while len(text) > max_length:
        split_pos = text[:max_length].rfind('\n')
        if split_pos == -1:
            split_pos = max_length
        chunks.append(text[:split_pos])
        text = text[split_pos:].strip()
    chunks.append(text)
    return chunks


# Command to find the 3 lowest prices
@dispatcher.message(Command("lowprices"))
async def low_prices(message: types.Message):
    products = load_products()
    if not products:
        await message.answer("No products found.")
        await message.answer(get_command_list())
        return

    # Sort products by price (assuming price is in format like "21 200 грн.")
    sorted_products = sorted(products, key=lambda x: float(re.sub(r"[^\d.]", "", x["price"])))
    lowest_prices = sorted_products[:3]

    response = "3 Lowest Prices:\n"
    for product in lowest_prices:
        response += (
            f"Title: [{escape_markdown(product['title'])}]({escape_markdown(product['link'])})\n"
            f"Price: {escape_markdown(product['price'])}\n"
            f"Location: {escape_markdown(product['location'])}\n"
            f"Date of publication: {escape_markdown(product['date of publication'])}\n\n"
        )

    await message.answer(response, parse_mode=ParseMode.MARKDOWN_V2)
    await message.answer(get_command_list())


# Command to delete a product by its ID
@dispatcher.message(Command("delete"))
async def delete_product_command(message: types.Message):
    await message.answer("Please send the ID of the product to delete")
    await message.answer(get_command_list())


@dispatcher.message(F.text.regexp(r'^\d+$'))
async def delete_product_handler(message: types.Message):
    product_id = int(message.text)

    # Load existing products
    products = load_products()

    # Filter out the product with the given ID
    new_products = [product for product in products if product['id'] != product_id]

    if len(new_products) == len(products):
        await message.answer(f'No product with ID {product_id} found.')
    else:
        # Save the updated list of products
        save_products(new_products)
        await message.answer(f'Product with ID {product_id} deleted.')

    await message.answer(get_command_list())


# Command to show all locations
@dispatcher.message(Command("location"))
async def show_locations(message: types.Message):
    products = load_products()
    locations = sorted(set(product["location"] for product in products))
    response = "Locations:\n" + "\n".join(locations)
    await message.answer(response)
    await message.answer(get_command_list())


# Command to find products by location
@dispatcher.message(Command("products_by_location"))
async def products_by_location(message: types.Message):
    products = load_products()
    locations = set(product["location"] for product in products)

    # Create an inline keyboard with a button for each location
    buttons = [InlineKeyboardButton(text=location, callback_data=f"location_{location}") for location in locations]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button] for button in buttons])

    await message.answer("Select a location:", reply_markup=keyboard)
    await message.answer(get_command_list())


# Handler for the location callback
@dispatcher.callback_query(lambda c: c.data and c.data.startswith('location_'))
async def show_products_by_location(callback_query: types.CallbackQuery):
    location = callback_query.data.split("_")[1]
    products = load_products()

    response = f"Products in {escape_markdown(location)}:\n"
    for product in products:
        if product["location"] == location:
            response += (
                f"Title: [{escape_markdown(product['title'])}]({escape_markdown(product['link'])})\n"
                f"Price: {escape_markdown(product['price'])}\n"
                f"Date of publication: {escape_markdown(product['date of publication'])}\n\n"
            )

    if response == f"Products in {escape_markdown(location)}:\n":
        response = f"No products found in {escape_markdown(location)}."

    # Split the response into smaller parts and send each part separately
    messages = split_message(response)
    for msg in messages:
        await callback_query.message.answer(msg, parse_mode=ParseMode.MARKDOWN_V2)

    await callback_query.message.answer(get_command_list())


async def main():
    await dispatcher.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
