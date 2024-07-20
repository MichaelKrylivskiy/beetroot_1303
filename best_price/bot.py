import asyncio
import json
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters.command import Command
from aiogram.enums import ParseMode

bot = Bot(token="write_your_token")
dispatcher = Dispatcher()


# Load products from JSON file
def load_products():
    with open('prices.json', 'r', encoding='utf-8') as file:
        return json.load(file)


# Save products to JSON file
def save_products(products):
    with open('prices.json', 'w', encoding='utf-8') as file:
        json.dump(products, file, indent=4)


def load_products():
    with open('prices.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data['products']


def parse_price(price_str):
    # Remove non-numeric characters and convert to integer
    numeric_str = ''.join(filter(str.isdigit, price_str))
    return int(numeric_str) if numeric_str else float('inf')


# Command to start the conversation
@dispatcher.message(Command("start"))
async def handle_message(message: types.Message):
    commands = (
        "/start - Start the conversation\n"
        "/add - Add a new product\n"
        "/list - List all commands\n"
        "/lowprices - Find the 3 lowest prices\n"
        "/delete - Delete a product by ID\n"
        "/commands - List all commands"
    )
    welcome_message = (
        "Welcome! Click a command below to interact with the bot:\n\n"
        f"{commands}"
    )
    await message.answer(welcome_message)


# Command to add a new product
@dispatcher.message(Command("add"))
async def add_product_command(message: types.Message):
    await message.answer("Please send the product details in the format: title,price")


# Command to list all commands
@dispatcher.message(Command("commands"))
async def list_commands(message: types.Message):
    commands = (
        "/start - Start the conversation\n"
        "/add - Add a new product\n"
        "/list - List all commands\n"
        "/lowprices - Find the 3 lowest prices\n"
        "/delete - Delete a product by ID\n"
        "/commands - List all commands"
    )
    await message.answer(f"Available commands:\n{commands}")


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


# Command to find the 3 lowest prices
@dispatcher.message(Command("lowprices"))
async def find_low_prices(message: types.Message):
    products = load_products()

    # Ensure products is a list of dicts
    if not isinstance(products, list):
        await message.answer("No products found.")
        return

    try:
        # Sort products by price
        sorted_products = sorted(products, key=lambda x: parse_price(x['price']))

        # Get the 3 lowest priced products
        lowest_products = sorted_products[:3]

        # Prepare the response
        response = "3 Lowest Prices:\n"
        for product in lowest_products:
            response += (f"Title: {product['title']}\n"
                         f"Price: {product['price']}\n"
                         f"Link: {product['link']}\n\n")

        await message.answer(response)

    except Exception as e:
        await message.answer(f"An error occurred: {e}")


# Command to delete a product by its ID
@dispatcher.message(Command("delete"))
async def delete_product_command(message: types.Message):
    await message.answer("Please send the ID of the product to delete")


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


async def main():
    await dispatcher.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
