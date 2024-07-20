# SuperFastPython.com
# example of a chat server using streams
import asyncio


# write a message to a stream writer
async def write_message(writer, msg_bytes):
    # write message to this user
    writer.write(msg_bytes)
    # wait for the buffer to empty
    await writer.drain()


# send a message to all connected users except the sender
async def broadcast_message(message, sender=None):
    # report locally
    print(f'Broadcast: {message.strip()}')
    # convert to bytes
    msg_bytes = message.encode()
    # enumerate all users and broadcast the message
    global ALL_USERS
    # create a task for each write to client except the sender
    tasks = [
        asyncio.create_task(write_message(w, msg_bytes))
        for name, (_, w) in ALL_USERS.items() if name != sender
    ]
    # wait for all writes to complete
    _ = await asyncio.wait(tasks)


# connect a user
async def connect_user(reader, writer):
    # get name message
    writer.write('Asycio Chat Server\n'.encode())
    writer.write('Enter your name:\n'.encode())
    await writer.drain()
    # ask the user for their name
    while True:
        name_bytes = await reader.readline()
        # convert name to string
        name = name_bytes.decode().strip()
        # check if name is already taken
        if name in ALL_USERS:
            writer.write('Name is already taken. Please enter a different name:\n'.encode())
            await writer.drain()
        else:
            break
    # store the user details
    global ALL_USERS
    ALL_USERS[name] = (reader, writer)
    # announce the user
    await broadcast_message(f'{name} has connected\n', sender=name)
    # welcome message
    welcome = f'Welcome {name}. Send QUIT to disconnect. Send ONLINE to see who is online.\n'
    writer.write(welcome.encode())
    await writer.drain()
    return name


# disconnect a user
async def disconnect_user(name, writer):
    # close the user's connection
    writer.close()
    await writer.wait_closed()
    # remove from the dict of all users
    global ALL_USERS
    del ALL_USERS[name]
    # broadcast the user has left
    await broadcast_message(f'{name} has disconnected\n')


# handle a chat client
async def handle_chat_client(reader, writer):
    print('Client connecting...')
    # connect the user
    name = await connect_user(reader, writer)
    try:
        # read messages from the user
        while True:
            # read a line of data
            line_bytes = await reader.readline()
            # convert to string
            line = line_bytes.decode().strip()
            # check for exit
            if line == 'QUIT':
                break
            # check for online command
            if line == 'ONLINE':
                online_users = ', '.join(ALL_USERS.keys())
                await write_message(writer, f'Online users: {online_users}\n'.encode())
                continue
            # broadcast message
            await broadcast_message(f'{name}: {line}\n', sender=name)
    finally:
        # disconnect the user
        await disconnect_user(name, writer)


# chat server
async def main():
    # define the local host
    host_address, host_port = '127.0.0.1', 8888
    # create the server
    server = await asyncio.start_server(handle_chat_client, host_address, host_port)
    # run the server
    async with server:
        # report message
        print('Chat Server Running\nWaiting for chat clients...')
        # accept connections
        await server.serve_forever()


# dict of all current users
ALL_USERS = {}
# start the event loop
asyncio.run(main())
