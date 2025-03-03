import requests
from telethon import TelegramClient, events
from datetime import datetime
import time
import pytz
# Initialize the bot
API_ID = '26075083'
API_HASH = '3021e8a65a7808eee45f9fc0bf55a157'
BOT_TOKEN = '7941778511:AAHnkLBtvhwZfyY1StribP-C0aqrzGtpkDU'

client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)


sgt_timezone = pytz.timezone('Asia/Singapore')
sgt_time = datetime.now(sgt_timezone)

# Replace with your actual server URL
POST_URL = 'http://127.0.0.1:5000/submit_tele'
LOGIN_URL = 'http://127.0.0.1:5000/login_tele'
CHANGES_URL = 'http://127.0.0.1:5000/changes_tele'
READ_URL = "http://127.0.0.1:5000/read_tele"
QUERY_URL = "http://127.0.0.1:5000/query_tele"
APPLY_DISPUTES_URL = "http://127.0.0.1:5000/apply_disputes_tele"

# In-memory user state management (per chat_id)
user_states = {}


@client.on(events.NewMessage(pattern='/reset'))
async def reset(event):
    chat_id = event.sender_id

    if chat_id in user_states:
        del user_states[chat_id]  # Completely remove the user's data
        await send_message(chat_id, "Your data has been reset. 😊 Please type /start to begin again.")
    else:
        await send_message(chat_id, "There's nothing to reset. Please type /start to begin.")


async def logout(chat_id):
    if chat_id in user_states:
        del user_states[chat_id]  # Completely remove the user's data
        await send_message(chat_id, "Your data has been reset. 😊 Please type /start to begin again.")
    else:
        await send_message(chat_id, "There's nothing to reset. Please type /start to begin.")


dashboard_add_new_cargo_container_index = 0
# Define the questions for each state
questions = {
    'login': [
        "Please enter your username:",
        "Please enter your password:"
    ],
    'initial': "Do you want to send Cargo or Containers? (Answer ‘cargo’ or ‘containers’)",
    'common': [
        "Name (This will be used to retrieve your request again)",
        "Business Name (Optional)",
        "Phone Number (in international format, no spaces, e.g. +6512345678)",
        "Password",
        "Business Email Address"
    ],
    'cargo': [
        "Dimensions of the package (LengthxWidthxHeight) in meters (e.g., 2x1.5x1)",
        "Weight of the package (in kg)"
    ],
    'container': [
        "Available Dimensions of the container (LengthxWidthxHeight) in meters (e.g., 12x2.4x2.6)",
        "Weight of the container (in kg)"
    ],
    'location': [
        "Origin Port/City/Country (Please enter in this format: City, Country)",
        "Destination Port/City/Country (Please enter in this format: City, Country)"
    ],
    'dates': [
        "Send-off date, arrival date ideally (Please enter dates in YYYY-MM-DD format)",
        "Arrival date (Please enter the date in YYYY-MM-DD format)",
        "Flexidate, tolerance to leave room for alternatives (Enter tolerance in days, 0 if none)"
    ],
    'comments': [
        "Tags for the comments (e.g., Perishables, Food, Temperature Sensitive, etc.)",
        "Additional comments (Put 'nil' if none)"
    ]
}

# Function to post the user's data to the server


def post_user_data(chat_id):
    user_data = {
        'chat_id': chat_id,
        'name': user_states[chat_id].get('name'),
        'business_name': user_states[chat_id].get('business_name'),
        'phone': user_states[chat_id].get('phone'),
        'email': user_states[chat_id].get('email'),
        'password': user_states[chat_id].get('password'),
        'mode': user_states[chat_id].get('mode'),
        'dimensions': user_states[chat_id].get(f"{user_states[chat_id]['mode']}_dimensions"),
        'weight': user_states[chat_id].get(f"{user_states[chat_id]['mode']}_weight"),
        'origin': user_states[chat_id].get('location_origin'),
        'destination': user_states[chat_id].get('location_destination'),
        'sendoff_date': user_states[chat_id].get('dates_sendoff'),
        'arrival_date': user_states[chat_id].get('dates_arrival'),
        'flexidate': user_states[chat_id].get('dates_flexidate'),
        'tags': user_states[chat_id].get('comments_tags'),
        'additional_comments': user_states[chat_id].get('comments_additional')
    }

    try:
        response = requests.post(POST_URL, json=user_data)
        if response.status_code == 200:
            print(f"Data for chat_id {chat_id} successfully posted to server.")
        else:
            print(
                f"Failed to post data for chat_id {chat_id}. Status code: {response.status_code}")
    except Exception as e:
        print(
            f"An error occurred while posting data for chat_id {chat_id}: {e}")


def post_changes(chat_id, changes={}):
    global user_states
    changes_json = {chat_id: chat_id, mode: user_states[chat_id]["mode"]}

    for key, value in changes.items():
        changes_json[key] = value

    try:
        response = requests.post(CHANGES_URL, json=changes_json)
        if response.status_code == 200:
            print(f"Data for chat_id {chat_id} successfully posted to server.")
        else:
            print(
                f"Failed to post data for chat_id {chat_id}. Status code: {response.status_code}")
    except Exception as e:
        print(
            f"An error occurred while posting data for chat_id {chat_id}: {e}")


def retrieve_data(chat_id, params={}):
    params_sent = {chat_id: chat_id}

    for key, value in params.items():
        params_sent[key] = value

    try:
        response = requests.get(QUERY_URL, params=params)

        if response.status_code == 200:
            data = response.json()
            print(data)
            return data
        else:
            print(
                f"Failed to retrieve data. Status Code: {response.status_code}")
    except Exception as e:
        print(
            f"An error occured while retrieving data for chat_id {chat_id}: {e}")

# Function to send a message to the user


async def send_message(chat_id, message):
    await client.send_message(chat_id, message)

# Function to handle login POST request


def post_login_data(username, password, chat_id):
    login_data = {
        'username': username,
        'password': password,
        'query': None
    }

    try:
        # First, POST the login data to check credentials
        response = requests.post(LOGIN_URL, json=login_data)

        # If login is successful (status code 200)
        if response.status_code == 200:
            # Perform a GET request to fetch user data (name, business_name)
            params = {
                'chat_id': chat_id,
                'username': username,
                'query': None
            }
            get_response = requests.get(READ_URL, params=params)

            # If the GET request is successful, return the user data
            if get_response.status_code == 200:
                user_data = get_response.json()
                return user_data  # Return the JSON response containing user details
            else:
                print(
                    f"Failed to retrieve user data. Status code: {get_response.status_code}")
                return False
        else:
            print("Invalid login credentials.")
            return False
    except Exception as e:
        print(f"An error occurred during login: {e}")
        return False


# Function to display the dashboard after login


async def display_dashboard(chat_id):
    name = user_states[chat_id].get('name')
    business = user_states[chat_id].get('business_name')
    time = str(sgt_time)
    mode = user_states[chat_id].get('mode')

    mode_str = "Cargo" if mode == "cargo" else "Container"
    dashboard_msg = f"""
Name: {name}
Business: {business}
Logged in as {mode_str} User

{time}

1 - Add New {mode_str}
2 - View Unmatched {mode_str}
3 - View Matched {mode_str}
4 - View Historical {mode_str}
5 - Make Changes to the {mode_str}
6 - Raise Dispute
7 - View Existing Disputes
8 - Reload

9 - Logout
"""
    await send_message(chat_id, dashboard_msg)

# Initialize user state for /start command


@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    chat_id = event.sender_id
    if chat_id not in user_states:
        user_states[chat_id] = {'state': 'menu'}
        await send_message(chat_id, """
        📦📦📦 Welcome to the PackTrack Bot! 📦📦📦

        Type "begin" to send cargo or post containers (for new users).
        Type "login" to manage existing cargo or containers (for returning users).
        """)
    else:
        await send_message(chat_id, "You've already started. Please choose 'begin' or 'login'.")

# Handle the user menu state


async def user_menu(chat_id, text):
    if text == 'begin':
        user_states[chat_id]['state'] = 'begin_common_name'
        await send_message(chat_id, questions['common'][0])  # Ask for Name
    elif text == 'login':
        user_states[chat_id]['state'] = 'login_username'
        await send_message(chat_id, questions['login'][0])  # Ask for username
    elif text == '/start':
        print('')
    else:
        await send_message(chat_id, "Invalid response. Please type 'begin' or 'login'.")

# Handle the login flow


async def handle_login(chat_id, text, state):
    if state == 'login_username':
        user_states[chat_id]['username'] = text
        user_states[chat_id]['state'] = 'login_password'
        await send_message(chat_id, questions['login'][1])  # Ask for password

    elif state == 'login_password':
        user_states[chat_id]['password'] = text
        username = user_states[chat_id]['username']
        password = user_states[chat_id]['password']

        # Call post_login_data to handle login and fetch user data
        user_data = post_login_data(username, password, chat_id)

        if user_data:
            # Update user state with the retrieved name and business name
            user_states[chat_id]['name'] = user_data.get('name')
            user_states[chat_id]['business_name'] = user_data.get(
                'business_name')

            # Notify the user and proceed to the mode selection
            await send_message(chat_id, f"Welcome back, {user_states[chat_id]['name']}!")
            user_states[chat_id]['state'] = 'login_choose_mode'
            await send_message(chat_id, "Do you want to log in as a 'cargo' or 'container' user?")
        else:
            await send_message(chat_id, "Invalid username or password. Please type /login to try again.")


# Handle the user dashboard after login


async def handle_dashboard(chat_id, text):
    if text == '1':
        user_states[chat_id]['state'] = 'dashboard_add_new_cargo_container'
        user_states[chat_id]['dashboard_add_new_cargo_container_index'] = 0
        await send_message(chat_id, "enter anything to continue")
    elif text == '2':
        user_states[chat_id]['state'] = 'dashboard_view_unmatched_cargo_container'
        await send_message(chat_id, "enter anything to continue")
    elif text == '3':
        user_states[chat_id]['state'] = 'dashboard_view_matched_cargo_container'
        await send_message(chat_id, "enter anything to continue")
    elif text == '4':
        user_states[chat_id]['state'] = 'dashboard_view_historical_cargo_container'
        await send_message(chat_id, "enter anything to continue")
    elif text == '5':
        user_states[chat_id]['state'] = 'dashboard_make_changes_cargo_container'
        user_states[chat_id]['dashboard_make_changes_cargo_container_index'] = 0
        await send_message(chat_id, "enter anything to continue")
    elif text == '6':
        user_states[chat_id]['state'] = 'dashboard_apply_disputes'
        user_states[chat_id]['apply_disputes_index'] = 0
        await send_message(chat_id, "enter anything to continue")
    elif text == '7':
        user_states[chat_id]['state'] = 'dashboard_view_existing_disputes'
        await send_message(chat_id, "enter anything to continue")
    elif text == '8':
        user_states[chat_id]['state'] = 'dashboard'
        display_dashboard(chat_id)
        await send_message(chat_id, "enter anything to continue")
    elif text == '9':
        await send_message(chat_id, "enter anything to continue")
        await logout(chat_id)

# Handle common questions (Name, Business Name, Phone Number, Email)


async def handle_view_unmatched_cargo_container(chat_id, text):
    mode = user_states[chat_id].get('mode')
    headers = {"mode": mode, "query": "unmatched"}

    try:
        data = retrieve_data(chat_id, headers)
        if mode == "cargo":
            data = data['cargo_table']['pending']
        elif mode == "container":
            data = data['container_table']['pending']
        else:
            print("glitchy glitchy")

        strings = []
        # send in a COOR ID Key, linked to a list that we just print all the details

        # please format the thing again in case I'm missing any data

        await send_message(chat_id,
                           """
        COOR ID | Name | Depart Date | Arrival Date | Origin Port | Destination Port | Flexidates
        """
                           )
        for key, items in data.items():
            key = str(key)
            item_strings = []
            for item in items:
                item = str(item)
                item_strings.append(item)
            items_combined = " | ".join(item_strings)
            strings.append(f"{key} | {items_combined}")

        message_sent = '\n'.join(strings)

        await send_message(chat_id, message_sent)

    except Exception as e:
        print(e)
        await send_message(chat_id, f"No data found OR Error in Communication: {e}")

    time.sleep(5)

    user_states[chat_id]['state'] = 'dashboard'
    await display_dashboard(chat_id)


async def handle_view_matched_cargo_container(chat_id, text):
    mode = user_states[chat_id].get('mode')
    headers = {"mode": mode, "query": "matched"}

    try:
        data = retrieve_data(chat_id, headers)
        if mode == "cargo":
            data = data['cargo_table']['active']
        elif mode == "container":
            data = data['container_table']['active']
        else:
            print("glitchy glitchy")
        strings = []
        # send in a COOR ID Key, linked to a list that we just print all the details

        # please format the thing again in case I'm missing any data

        await send_message(chat_id,
                           """
        COOR ID | Name | Depart Date | Arrival Date | Origin Port | Destination Port | Flexidates
        """
                           )
        for key, items in data.items():
            key = str(key)
            item_strings = []
            for item in items:
                item = str(item)
                item_strings.append(item)
            items_combined = " | ".join(item_strings)
            strings.append(f"{key} | {items_combined}")

        message_sent = '\n'.join(strings)

        await send_message(chat_id, message_sent)

    except Exception as e:
        print(e)
        await send_message(chat_id, f"No data found OR Error in Communication: {e}")

    time.sleep(5)

    user_states[chat_id]['state'] = 'dashboard'
    await display_dashboard(chat_id)


async def handle_view_historical_cargo_container(chat_id, text):
    mode = user_states[chat_id].get('mode')
    headers = {"mode": mode, "query": "historical"}

    try:
        data = retrieve_data(chat_id, headers)
        if mode == "cargo":
            data = data['cargo_table']['delivered']
        elif mode == "container":
            data = data['container_table']['delivered']
        else:
            print("glitchy glitchy")
        strings = []
        # send in a COOR ID Key, linked to a list that we just print all the details

        # please format the thing again in case I'm missing any data

        await send_message(chat_id,
                           """
        COOR ID | Name | Depart Date | Arrival Date | Origin Port | Destination Port | Flexidates
        """
                           )
        for key, items in data.items():
            key = str(key)
            item_strings = []
            for item in items:
                item = str(item)
                item_strings.append(item)
            items_combined = " | ".join(item_strings)
            strings.append(f"{key} | {items_combined}")

        message_sent = '\n'.join(strings)

        await send_message(chat_id, message_sent)

    except Exception as e:
        print(e)
        await send_message(chat_id, f"No data found OR Error in Communication: {e}")

    time.sleep(5)

    user_states[chat_id]['state'] = 'dashboard'
    await display_dashboard(chat_id)


async def handle_view_disputes(chat_id, text):
    mode = "disputes"
    headers = {"mode": mode, "query": "dispute"}

    try:
        data = retrieve_data(chat_id, headers)
        strings = []
        # send in a COOR ID Key, linked to a list that we just print all the details

        # please format the thing again in case I'm missing any data

        await send_message(chat_id,
                           """
        COOR ID | Name | Depart Date | Arrival Date | Origin Port | Destination Port | Flexidates
        """
                           )
        for key, items in data.items():
            key = str(key)
            item_strings = []
            for item in items:
                item = str(item)
                item_strings.append(item)
            items_combined = " | ".join(item_strings)
            strings.append(f"{key} | {items_combined}")

        message_sent = '\n'.join(strings)

        await send_message(chat_id, message_sent)

    except Exception as e:
        print(e)
        await send_message(chat_id, f"No data found OR Error in Communication: {e}")

    time.sleep(5)

    user_states[chat_id]['state'] = 'dashboard'
    await display_dashboard(chat_id)


async def handle_add_new_cargo_container(chat_id, text):
    mode = user_states[chat_id].get('mode')
    global dashboard_add_new_cargo_container_index

    questions_set = []
    if mode == 'cargo':
        questions_set = questions['cargo'] + questions['location'] + \
            questions['dates'] + questions['comments']
        print(questions_set)

    elif mode == 'container':
        questions_set = questions['container'] + questions['location'] + \
            questions['dates'] + questions['comments']
        print(questions_set)

    else:
        print("oof glitch in the system")

    if dashboard_add_new_cargo_container_index+1 <= len(questions_set):
        await send_message(chat_id, questions_set[dashboard_add_new_cargo_container_index])

    if dashboard_add_new_cargo_container_index == 0:

        dashboard_add_new_cargo_container_index += 1

    elif dashboard_add_new_cargo_container_index == 1:
        user_states[chat_id][f"{mode}_dimensions"] = text

        dashboard_add_new_cargo_container_index += 1

    elif dashboard_add_new_cargo_container_index == 2:
        user_states[chat_id][f"{mode}_weight"] = text

        dashboard_add_new_cargo_container_index += 1

    elif dashboard_add_new_cargo_container_index == 3:
        user_states[chat_id]['location_origin'] = text

        dashboard_add_new_cargo_container_index += 1

    elif dashboard_add_new_cargo_container_index == 4:
        user_states[chat_id]['location_destination'] = text

        dashboard_add_new_cargo_container_index += 1

    elif dashboard_add_new_cargo_container_index == 5:
        user_states[chat_id]['dates_sendoff'] = text

        dashboard_add_new_cargo_container_index += 1

    elif dashboard_add_new_cargo_container_index == 6:
        user_states[chat_id]['dates_arrival'] = text

        dashboard_add_new_cargo_container_index += 1

    elif dashboard_add_new_cargo_container_index == 7:
        user_states[chat_id]['dates_flexidate'] = text

        dashboard_add_new_cargo_container_index += 1

    elif dashboard_add_new_cargo_container_index == 8:
        user_states[chat_id]['comments_tags'] = text

        dashboard_add_new_cargo_container_index += 1

    elif dashboard_add_new_cargo_container_index == 9:
        user_states[chat_id]['comments_additional'] = text
        user_states[chat_id]['state'] = 'dashboard'
        post_user_data(chat_id)
        await display_dashboard(chat_id)

    else:
        print("oof glitch in the system")


async def handle_common_questions(chat_id, text, state):
    common_index = {
        'begin_common_name': 1,
        'begin_common_business': 2,
        'begin_common_phone': 3,
        'begin_common_password': 4,
        'begin_common_email': None  # End of common questions
    }

    if 'begin_common_name' in state:
        user_states[chat_id]['name'] = text
        user_states[chat_id]['state'] = 'begin_common_business'
        await send_message(chat_id, questions['common'][1])
    elif 'begin_common_business' in state:
        user_states[chat_id]['business_name'] = text
        user_states[chat_id]['state'] = 'begin_common_phone'
        await send_message(chat_id, questions['common'][2])
    elif 'begin_common_phone' in state:
        user_states[chat_id]['phone'] = text
        user_states[chat_id]['state'] = 'begin_common_password'
        await send_message(chat_id, questions['common'][3])
    elif 'begin_common_password' in state:
        user_states[chat_id]['password'] = text
        user_states[chat_id]['state'] = 'begin_common_email'
        await send_message(chat_id, questions['common'][4])
    elif 'begin_common_email' in state:
        user_states[chat_id]['email'] = text
        user_states[chat_id]['state'] = 'begin'
        await send_message(chat_id, questions['initial'])


async def begin(chat_id, text):
    if text == 'cargo':
        user_states[chat_id]['state'] = 'begin_cargo_dimensions'
        user_states[chat_id]['mode'] = 'cargo'
        await send_message(chat_id, questions['cargo'][0])
    elif text == 'containers':
        user_states[chat_id]['state'] = 'begin_container_dimensions'
        user_states[chat_id]['mode'] = 'container'
        await send_message(chat_id, questions['container'][0])
    else:
        # Handle invalid input for "cargo" or "containers"
        await send_message(chat_id, 'Invalid response. Please reply with "cargo" or "containers".')
        return

# Handle cargo-specific questions


async def handle_cargo_dimensions(chat_id, text):
    # Store dimensions and move to the next cargo-specific question
    user_states[chat_id]['cargo_dimensions'] = text
    user_states[chat_id]['state'] = 'begin_cargo_weight'
    # Ask for the weight of the cargo
    await send_message(chat_id, questions['cargo'][1])


async def handle_cargo_weight(chat_id, text):
    # Store weight and move to the location questions
    user_states[chat_id]['cargo_weight'] = text
    user_states[chat_id]['state'] = 'begin_location_origin'
    await send_message(chat_id, questions['location'][0])  # Ask for the origin

# Handle container-specific questions


async def handle_container_dimensions(chat_id, text):
    # Store dimensions and move to the next container-specific question
    user_states[chat_id]['container_dimensions'] = text
    user_states[chat_id]['state'] = 'begin_container_weight'
    # Ask for the weight of the container
    await send_message(chat_id, questions['container'][1])


async def handle_container_weight(chat_id, text):
    # Store weight and move to the location questions
    user_states[chat_id]['container_weight'] = text
    user_states[chat_id]['state'] = 'begin_location_origin'
    await send_message(chat_id, questions['location'][0])  # Ask for the origin

# Handle location questions


async def handle_location_origin(chat_id, text):
    # Store origin and move to the destination
    user_states[chat_id]['location_origin'] = text
    user_states[chat_id]['state'] = 'begin_location_destination'
    # Ask for the destination
    await send_message(chat_id, questions['location'][1])


async def handle_location_destination(chat_id, text):
    # Store destination and move to send-off date
    user_states[chat_id]['location_destination'] = text
    user_states[chat_id]['state'] = 'begin_dates_sendoff'
    # Ask for the send-off date
    await send_message(chat_id, questions['dates'][0])

# Handle dates questions


async def handle_dates_sendoff(chat_id, text):
    # Store send-off date and move to arrival date
    user_states[chat_id]['dates_sendoff'] = text
    user_states[chat_id]['state'] = 'begin_dates_arrival'
    # Ask for the arrival date
    await send_message(chat_id, questions['dates'][1])


async def handle_dates_arrival(chat_id, text):
    # Store arrival date and move to flexidate
    user_states[chat_id]['dates_arrival'] = text
    user_states[chat_id]['state'] = 'begin_dates_flexidate'
    # Ask for the flexidate tolerance
    await send_message(chat_id, questions['dates'][2])


async def handle_dates_flexidate(chat_id, text):
    # Store flexidate and move to comments
    user_states[chat_id]['dates_flexidate'] = text
    user_states[chat_id]['state'] = 'begin_comments_tags'
    # Ask for tags for comments
    await send_message(chat_id, questions['comments'][0])

# Handle comments


async def handle_comments_tags(chat_id, text):
    # Store tags and move to additional comments
    user_states[chat_id]['comments_tags'] = text
    user_states[chat_id]['state'] = 'begin_comments_additional'
    # Ask for additional comments
    await send_message(chat_id, questions['comments'][1])


async def handle_comments_additional(chat_id, text):
    # Store additional comments and conclude the process
    user_states[chat_id]['comments_additional'] = text
    await send_message(chat_id, "Thank you! All information has been saved.")
    post_user_data(chat_id)  # Post data to the server after completion
    user_states[chat_id]['state'] = 'menu'  # Return to menu
    await send_message(chat_id, """
        📦📦📦 Welcome to the PackSmart Bot! 📦📦📦

        Type "begin" to send cargo or post containers (for new users).
        Type "login" to manage existing cargo or containers (for returning users).
        """)

# Generic message handler to manage the flow based on user states


async def handle_make_changes_cargo_container(chat_id, text):
    global user_states

    questions = ['Enter Container/Cargo ID that you want to change',
                 '''
        Options to Change
        ** ENTER JUST THE NUMBER **
        1) Change Name
        2) Change Dimensions
        3) Change Tags
        4) Change Description
        5) Change Origin Location
        6) Change Destination Location
        7) Change Date Of Departure
        8) Change Date Of Arrival
        9) Change Flexidate Tolerance
        10) Reshuffle Assigned Cargo/Container (if assigned already)


    ''',

                 'Change to what value?',

                 'If the ID and change are valid, it should be all good. You may go back to the dashboard and check the unmarked/marked cargo/containers if your desired change has gone through'

                 ]

    index = user_states[chat_id]['dashboard_make_changes_cargo_container_index']

    if index == 0:
        await send_message[questions[index]]
        index += 1
    elif index == 1:
        await send_message[questions[index]]
        user_states[chat_id]['make_changes_cid'] = text
        index += 1
    elif index == 2:
        await send_message[questions[index]]
        user_states[chat_id]['make_changes_para'] = text
        index += 1
    elif index == 3:
        await send_message[questions[index]]
        user_states[chat_id]['make_changes_change'] = text
        index += 1
    elif index == 4:
        await send_message[questions[index]]
        post_changes(chat_id, {
            "container_cargo_id": user_states[chat_id]['makes_changes_cid'],
            "parameter": user_states[chat_id]['make_changes_para'],
            "change": user_states[chat_id]['make_changes_change']
        })

        user_states[chat_id]['state'] = 'dashboard'
        post_user_data(chat_id)
        await display_dashboard(chat_id)

    else:
        print("WEEE")


async def handle_apply_disputes(chat_id, text):
    global user_states
    questions = [
        "Provide a description of the problem",
        "Provide all other usera' involved with their keyIDs (comma seperated) (if any)"
        "Is there a container/cargo involved?",
        "Put unique container/cargo id if applicable, if not put 'nil'"
    ]

    index = user_states[chat_id]["apply_disputes_index"]

    if index == 0:
        await send_message(chat_id, questions[index])
        index += 1
    elif index == 1:
        user_states[chat_id]["apply_dispute_prob_desc"] = text
        await send_message(chat_id, questions[index])
        index += 1
    elif index == 2:
        user_states[chat_id]["apply_dispute_other_users"] = text
        await send_message(chat_id, questions[index])
        index += 1
    elif index == 3:
        user_states[chat_id]["apply_dispute_container_cargo_yesno"] = text
        await send_message(chat_id, questions[index])
        index += 1
    elif index == 4:
        user_states[chat_id]['apply_dispute_container_cargo_id'] = text

        data = {
            "problem_description": user_states[chat_id]["apply_dispute_prob_desc"],
            "other_users": user_states[chat_id]["apply_dispute_other_users"],
            "container_cargo_yesno": user_states[chat_id]["apply_dispute_container_cargo_yesno"],
            "container_cargo_id": user_states[chat_id]['apply_dispute_container_cargo_id'],
            "mode": user_states[chat_id]["mode"],
            "chat_id": chat_id
        }
        try:
            response = requests.post(APPLY_DISPUTES_URL, jsonify(data))

            if response.status_code == 200:
                print(
                    f"Data for applying dispute, chat_id {chat_id} successfully posted to server.")

            else:
                print(
                    f"Failed to post data for applying dispute for chat_id {chat_id}. Status code: {response.status_code}")
        except Exception as e:
            print(
                f"An error occurred while posting data for chat_id {chat_id}: {e}")

        user_states[chat_id]['state'] = 'dashboard'
        post_user_data(chat_id)
        await display_dashboard(chat_id)
    else:
        print("glitchy glitchy")


@client.on(events.NewMessage)
async def handle_message(event):
    chat_id = event.sender_id
    text = event.raw_text.strip().lower()

    if chat_id not in user_states:
        await send_message(chat_id, "Please type /start to begin.")
        return

    user_state = user_states[chat_id]['state']
    print(f"Current User_state: {user_state}")
    if user_state == 'menu':
        await user_menu(chat_id, text)

    elif user_state == 'login_choose_mode':
        print("this 2")
        if text in ['cargo', 'container']:
            print("running...")
            user_states[chat_id]['mode'] = text
            user_states[chat_id]['state'] = 'dashboard'

            await display_dashboard(chat_id)
        else:
            await send_message(chat_id, "Invalid response. Please reply with 'cargo' or 'container'.")

    elif user_state.startswith('login'):
        print("This 1")
        await handle_login(chat_id, text, user_state)
    elif user_state == 'dashboard':
        print("this 3")
        await handle_dashboard(chat_id, text)

    elif user_state == 'dashboard_add_new_cargo_container':
        await handle_add_new_cargo_container(chat_id, text)
    elif user_state == 'dashboard_view_unmatched_cargo_container':
        await handle_view_unmatched_cargo_container(chat_id, text)
    elif user_state == 'dashboard_view_matched_cargo_container':
        await handle_view_matched_cargo_container(chat_id, text)
    elif user_state == 'dashboard_view_historical_cargo_container':
        await handle_view_historical_cargo_container(chat_id, text)
    elif user_state == 'dashboard_make_changes_cargo_container':
        await handle_make_changes_cargo_container(chat_id, text)
    elif user_state == 'dashboard_apply_disputes':
        await handle_apply_disputes(chat_id, text)
    elif user_state == 'dashboard_view_disputes':
        await handle_view_disputes(chat_id, text)
    elif user_state.startswith('begin_common'):
        await handle_common_questions(chat_id, text, user_state)
    elif user_state == 'begin':
        await begin(chat_id, text)
    elif user_state == 'begin_cargo_dimensions':
        await handle_cargo_dimensions(chat_id, text)
    elif user_state == 'begin_cargo_weight':
        await handle_cargo_weight(chat_id, text)
    elif user_state == 'begin_container_dimensions':
        await handle_container_dimensions(chat_id, text)
    elif user_state == 'begin_container_weight':
        await handle_container_weight(chat_id, text)
    elif user_state == 'begin_location_origin':
        await handle_location_origin(chat_id, text)
    elif user_state == 'begin_location_destination':
        await handle_location_destination(chat_id, text)
    elif user_state == 'begin_dates_sendoff':
        await handle_dates_sendoff(chat_id, text)
    elif user_state == 'begin_dates_arrival':
        await handle_dates_arrival(chat_id, text)
    elif user_state == 'begin_dates_flexidate':
        await handle_dates_flexidate(chat_id, text)
    elif user_state == 'begin_comments_tags':
        await handle_comments_tags(chat_id, text)
    elif user_state == 'begin_comments_additional':
        await handle_comments_additional(chat_id, text)

    else:
        print(f"the problematic state is {user_state}")
        await send_message(chat_id, "Invalid state. Please type /start to reset.")

# Start the bot
client.run_until_disconnected()
