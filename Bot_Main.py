from asyncio import BaseEventLoop
from balethon import Client
from balethon.conditions import private, at_state, equals, successful_payment
from balethon.objects import Message, CallbackQuery, InlineKeyboard, InlineKeyboardButton, LabeledPrice
from Validations import *
from balethon.states.state_machine import StateMachine  
import pandas 
import os
from dotenv import load_dotenv
import json
import jdatetime

#Variables

user_has_joined = {}
setting_payment_message_id = 0
signup_payment_message_id = 0
CHANNEL_ID = 4858274378
excel_file_path = 'لیست مسافران کاروان.xlsx'
signup_json_file_path = os.path.abspath("JsonFiles/signup_datas.json")
payment_settings_json_file_path = os.path.abspath("JsonFiles/payment_settings_datas.json")
startpanel_informations_json_file_path = os.path.abspath("JsonFiles/startpanel_informations_datas.json")

load_dotenv()

bot = Client(os.environ["TOKEN"])


# Json Files Structures

if os.path.exists(signup_json_file_path):
    with open(signup_json_file_path, "r", encoding="utf-8") as f:
        SignUp_Datas = json.load(f)
else:
    SignUp_Datas = {
        "Name": [],
        "Phone_Number": [],
        "Code_Meli": [],
        "Age": []
    }

SignUp_Keys = ["Name", "Phone_Number", "Code_Meli", "Age"]


if os.path.exists(payment_settings_json_file_path):
    with open(payment_settings_json_file_path, "r", encoding="utf-8") as f:
        Payment_Settings_Datas = json.load(f)
else:
    Payment_Settings_Datas = {
        "title": "",
        "description": "",
        "price": "",
        "credit_card": ""
    }

Payment_Settings_Keys = ["title", "description", "price", "credit_card"]


if os.path.exists(startpanel_informations_json_file_path):
    with open(startpanel_informations_json_file_path, "r", encoding="utf-8") as f:
        StartPanel_Informations_Datas = json.load(f)
else:
    StartPanel_Informations_Datas = {
        "description": "",
        "signup_capacity": 0,
        "signup_count": 0,
        "trip_is_start": False
    }


#Creating or Updating json files functions


def save_signup_data_to_json():
    with open(signup_json_file_path, "w", encoding="utf-8") as f:
        json.dump(SignUp_Datas, f, ensure_ascii=False, indent=2)

save_signup_data_to_json()


def save_payment_settings_data_to_json():
    with open(payment_settings_json_file_path, "w", encoding="utf-8") as f:
        json.dump(Payment_Settings_Datas, f, ensure_ascii=False, indent=2)

save_payment_settings_data_to_json()


def save_startpanel_informations_data_to_json():
    with open(startpanel_informations_json_file_path, "w", encoding="utf-8") as f:
        json.dump(StartPanel_Informations_Datas, f, ensure_ascii=False, indent=2)

save_startpanel_informations_data_to_json()

#Checking for Payment Settings


def payment_settings_check():    
    if ("" in (Payment_Settings_Datas["title"], Payment_Settings_Datas["description"], Payment_Settings_Datas["credit_card"], Payment_Settings_Datas["price"])):
        return False
    else:
        return True


#Checking admin and membership of chanel

def is_admin(user_id):
    # لیست ID ادمین ها را در اینجا وارد کنید
    admin_ids = [403949029, 1828929996]
    return user_id in admin_ids

async def check_membership(chat_id, user_id):
    chat_member = await bot.get_chat_member(chat_id, user_id)
    if chat_member.status in ("administrator", "member", "creator"):
        join_chek = True
        return True
    else:
        return False


#Commands

@bot.on_command(private)
async def admin_panel(*, message):
    global StartPanel_Informations_Datas

    if is_admin(user_id= message.author.id) == True:
        if StartPanel_Informations_Datas["trip_is_start"] == True:
            await message.reply(
                "پنل مدیریت",
                InlineKeyboard(
                    [("اتمام ثبت نام.", "stop_signup")],
                    [("دریافت اسامی مسافران.", "passengers_list")],
                    [("تعداد نفرات باقی مانده.", "remaining_capacity")],
                    [("حذف مسافر.", "remove_passenger")],
                    [("تنظیمات پرداخت.", "payment_settings")]
                )
            )
        else:
            await message.reply(
                "پنل مدیریت",
                InlineKeyboard(
                    [("شروع ثبت نام.", "start_signup")],
                    [("تنظیمات پرداخت.", "payment_settings")],
                    [("دریافت اسامی مسافران.", "passengers_list")],
                    [("حذف مسافر.", "remove_passenger")]
                )
            )
    else:
        await message.reply("شما دسترسی به این دستور را ندارید.")


@bot.on_command(private)
async def start(*, message):
    await start_core(message, message.author.id)


async def start_core(message, user_id):
    global SignUp_Data
    #user_id = message.from_user.id
    if user_has_joined.get(user_id, False):
        await message.reply(
            "...",
            InlineKeyboard(
                [("ثبت نام.", "SignUp")]
            )
        )    
    else:
        await message.reply(
            '''سلام به بات ثبت نام در کاروان زیارتی 313 خوش امدید
            برای ادامه  ثبت نام اول عضو چنل شید و بعد روی دکمه(عضو شدم)کلیک کنید.''',       
            InlineKeyboard(
                [InlineKeyboardButton('چنل کاروان313', url='https://ble.ir/karevan_ziarati')],
                [('عضو شد.', 'join')],
            )
        )

    message.author.set_state("")
    SignUp_Data.clear()


#CallBack Queryes

@bot.on_callback_query()
async def admin_panel_callback_handler(callback_query):
    global StartPanel_Informations_Datas, SignUp_Datas
    user_id = callback_query.author.id

    callback_query.author.set_state("")

    #Admin Panel CallBacks

    if callback_query.data == "passengers_list":
        with open(signup_json_file_path, "r", encoding="utf-8") as f:
            json_SignUp_Datas = json.load(f)

        data_table = pandas.DataFrame(json_SignUp_Datas)
        data_table.index += 1 

        data_table.to_excel(excel_file_path, index_label="ردیف")

        await bot.send_document(chat_id= callback_query.message.chat.id, document= open(excel_file_path, 'rb'))
        await callback_query.answer("لیست مسافران در قالب فایل اکسل فرستاده شد.")

    elif callback_query.data == "remove_passenger":        
        passenger_list = ""

        if StartPanel_Informations_Datas["signup_count"] > 0:
            for i, name in enumerate(SignUp_Datas["Name"]):
                passenger_list += f"{i + 1}. {name}\n"

            await callback_query.answer(f"لیست مسافران:\n\n{passenger_list}\n\nشماره مسافری که می‌خواهید حذف کنید را وارد کنید:")
            callback_query.author.set_state("REMOVE_PASSENGER_SELECT")

        else:
            await callback_query.answer("هنوز مسافری ثبت نام نکرده است")

    elif callback_query.data == "remaining_capacity":
        remaining_capacity = StartPanel_Informations_Datas["signup_capacity"] - StartPanel_Informations_Datas["signup_count"]

        await callback_query.answer(f"ظریفت باقی مانده: {remaining_capacity} نفر هست.")

    elif callback_query.data == "payment_settings":

        await bot.send_message(chat_id= callback_query.message.chat.id, text= "موضوع پرداخت را وارد کنید.")
        callback_query.author.set_state("TITLE")

    elif callback_query.data == "start_signup":

        SignUp_Datas = {
            "Name": [],
            "Phone_Number": [],
            "Code_Meli": [],
            "Age": []
        }

        save_signup_data_to_json()

        if (payment_settings_check()):
            await bot.send_message(chat_id= callback_query.message.chat.id ,text= "توضیحات سفر را وارد کنید.")
            callback_query.author.set_state("TRIP_DESCRIPTION")

        else:
            await callback_query.answer("تنظیمات پرداخت روی هیچ مقداری تنظیم نشده است")

    elif callback_query.data == "stop_signup":
        StartPanel_Informations_Datas["trip_is_start"] = False

        await callback_query.answer("ثبت نام پایان یافت سفر خوبی داشته باشید.")


    #Start Panel CallBacks


    elif callback_query.data == "join":
        is_member = await check_membership(CHANNEL_ID, callback_query.author.id)
        if is_member == True:
            await bot.delete_message(callback_query.message.chat.id , callback_query.message.id)
            await callback_query.answer('شما عضو کانال هستید. حالا میتوانید برای ثبت نام اقدام کنید.')
            user_has_joined[user_id]= True  
            await start_core(callback_query.message)
            callback_query.author.set_state("")

        else:
            await callback_query.answer('شما عضو کانال نیستید. لطفاً ابتدا عضو کانال شوید.')
            callback_query.author.set_state("")

    elif callback_query.data == "SignUp":

        if (StartPanel_Informations_Datas["trip_is_start"]):
            await bot.send_message(chat_id= callback_query.message.chat.id, text= "اسم و فامیلتون رو وارد کنید.")
            callback_query.author.set_state("NAME")

        else:
            await callback_query.answer("ثبت نام به پایان رسیده لطفا تا سفر بعد صبر کنید.")


# remove passengers state 

@bot.on_message(at_state("REMOVE_PASSENGER_SELECT"))
async def remove_passenger_state(message):
    try:
        index = int(message.text) - 1
        if index < 0 or index >= len(SignUp_Datas["Name"]):
            raise IndexError

        for key in SignUp_Keys:
            SignUp_Datas[key].pop(index)

        StartPanel_Informations_Datas["signup_count"] -= 1
        save_signup_data_to_json()

        await message.reply("مسافر با موفقیت حذف شد.")

    except (ValueError, IndexError):
        await message.reply("شماره وارد شده معتبر نیست. لطفاً دوباره تلاش کنید.")

    message.author.set_state("")

# Start Trip Information

@bot.on_message(at_state("TRIP_DESCRIPTION"))
async def trip_description_state(message):
    StartPanel_Informations_Datas["description"] = message.text

    await bot.send_message(chat_id= message.chat.id, text= "ظرفیت ثبت نام چند نفر هست؟")
    message.author.set_state("SIGNUP_CAPACITY")

@bot.on_message(at_state("SIGNUP_CAPACITY"))
async def SignUp_capacity_state(message):
    if (validate_capacity(message.text)):

        StartPanel_Informations_Datas["signup_capacity"] = int(message.text)

        StartPanel_Informations_Datas["trip_is_start"] = True
        await bot.send_message(chat_id= message.chat.id, text= "ثبت نام با موفقیت اغاز شد.")

        save_startpanel_informations_data_to_json()
        message.author.set_state("")

    else:
        await message.reply("مقدار واد شده یک عدد معتبر نمی باشد لطفا دوباره تلاش کنید.")


# Payment Settings

Payment_Settings_Data = []

@bot.on_message(at_state("TITLE"))
async def title_state(message):
    Payment_Settings_Data.append(message.text)

    await bot.send_message(chat_id= message.chat.id, text= "توضیحات پرداخت را وارد کنید.")
    message.author.set_state("DESCRIPTION")


@bot.on_message(at_state("DESCRIPTION"))
async def description_state(message):
    Payment_Settings_Data.append(message.text)

    await bot.send_message(chat_id= message.chat.id, text= "مبلغ را به ریال وارد کنید.")
    message.author.set_state("PRICE")


@bot.on_message(at_state("PRICE"))
async def price_state(message):
    if(validate_price(message.text)):
        Payment_Settings_Data.append(message.text)

        await bot.send_message(chat_id= message.chat.id, text= "شماره کارت را وارد کنید.")
        message.author.set_state("CREDIT_CARD")
    else:
        await message.reply("مبلغ وارد شده معتبر نیست لطفا دوباره تلاش کنید.")


@bot.on_message(at_state("CREDIT_CARD"))
async def credit_card_state(message):
    global setting_payment_message_id

    if (validate_credit_card(message.text)):
        Payment_Settings_Data.append(message.text)

        payment_message = await bot.send_invoice(
                chat_id=message.chat.id,
                title= Payment_Settings_Data[0],
                description= Payment_Settings_Data[1],
                payload=str(message.author.id),
                provider_token= Payment_Settings_Data[3],
                prices= [LabeledPrice(label="قیمت", amount= int(Payment_Settings_Data[2]))]
            )

        setting_payment_message_id = payment_message.id

        await bot.send_message(chat_id= message.chat.id, text= "Do You confirm the payment settings (Yes/No)?")
        message.author.set_state("PAYMENT_CONFIRMATION")

    else:
        await message.reply("شماره کارت وارد شده معتبر نیسست لطفا دوباره تلاش کنید.")


@bot.on_message(at_state("PAYMENT_CONFIRMATION"))
async def payment_confirmation_state(message):
    global setting_payment_message_id

    if str(message.text).capitalize() in ("Yes", "No"):

        if validate_confirm(message.text):

            await bot.delete_message(message.chat.id, setting_payment_message_id)

            for i in range(len(Payment_Settings_Keys)):
                Payment_Settings_Datas[Payment_Settings_Keys[i]] = Payment_Settings_Data[i]

            Payment_Settings_Data.clear()
            save_payment_settings_data_to_json()

            await message.reply("تنظیمات پرداخت با موفقیت ثبت شد.")

            message.author.set_state("") #reset state after confirmation
        else:

            await message.reply("دوباره با دستور /admin_panel تلاش کن.")
            message.author.set_state("") #reset state after no confirmation
    else:
        await message.reply("لطفا دوباره تلاش کن.")


# SignUp Process

SignUp_Data = []

@bot.on_message(at_state("NAME"))
async def name_state(message):
    SignUp_Data.append(message.text)
    await bot.send_message(chat_id= message.chat.id, text= "شماره تماس رو وارد کنید.")
    message.author.set_state("PHONE_NUMBER")

@bot.on_message(at_state("PHONE_NUMBER"))
async def phone_number_state(message):
    if validate_phone_number(message.text):
        SignUp_Data.append(message.text)

        await bot.send_message(chat_id= message.chat.id, text= "کد ملیتون رو وارد کنید.")
        message.author.set_state("CODE_MELI")
    else:
        await message.reply("شماره تلفن معتبر نیست دوباره تلاش کنید")


@bot.on_message(at_state("CODE_MELI"))
async def code_meli_state(message):
    if validate_code_meli(message.text):
        SignUp_Data.append(message.text)
        await bot.send_message(chat_id= message.chat.id, text= "تاریخ تولدت رو با فرمت 01-06-1367 وارد کن.")
        message.author.set_state("AGE")
    else:
        await message.reply("کد ملیت معتبر نیست دوباره تلاش کن.")


@bot.on_message(at_state("AGE"))
async def age_state(message):
    text = message.text
    data_str = text.replace("/", "-")
    try:
        year, month, day = map(int, data_str.split("-"))
        shamsi_data = jdatetime.date(year, month, day)
        SignUp_Data.append(shamsi_data)
        await bot.send_message(chat_id= message.chat.id, text=
        f"اسم و فامیلیتون: {SignUp_Data[0]}, شماره تماستون: {SignUp_Data[1]}, کد ملیتون: {SignUp_Data[2]}, تاریخ تولدتون: {SignUp_Data[3]} \n اطلاعاتتون درسته؟ (Yes/No)"
        )

        message.author.set_state("SIGNUP_CONFIRMATION")
    except ValueError:
        await message.reply("تاریخ تولدتون معتبر نیست دوباره تلاش کنید.")


@bot.on_message(at_state("SIGNUP_CONFIRMATION"))
async def SignUp_Confirmation_state(message):
    if str(message.text).capitalize() == "Yes" or str(message.text).capitalize() == "No":
        if validate_confirm(message.text):
            message.author.set_state("PAYMENT")
            await payment_state(message)
        else:
            await message.reply("میتوانید دوباره با دستور /start ثبت نام کنید.")
            message.author.set_state("")
            SignUp_Data.clear()
    else:
        await message.reply("لطفا دوباره تلاش کنید.")


#Payment System


async def payment_state(message):
    global signup_payment_message_id

    await message.reply("در حال پردازش پرداخت...")

    payment_message = await bot.send_invoice(
        chat_id=message.chat.id,
        title= Payment_Settings_Datas['title'],
        description= Payment_Settings_Datas['description'],
        payload=str(message.author.id),
        provider_token= Payment_Settings_Datas['credit_card'],  
        prices=[LabeledPrice(label="قیمت", amount= int(Payment_Settings_Datas['price']))]
    )

    signup_payment_message_id = payment_message.id


@bot.on_message(successful_payment)
async def show_payment(message):
    global signup_payment_message_id
    
    await bot.delete_message(message.chat.id, signup_payment_message_id)

    user = await bot.get_chat(message.successful_payment.invoice_payload)
    amount = message.successful_payment.total_amount
    print(f"{user.name}, paid {amount}")

    #adding client to the list
    for i in range(len(SignUp_Keys)):
        SignUp_Datas[SignUp_Keys[i]].append(SignUp_Data[i])

    StartPanel_Informations_Datas["signup_count"] += 1 
    SignUp_Data.clear()
    save_signup_data_to_json()

    await bot.send_message(chat_id= message.chat.id, text= "ثبت نام با موفقیت کامل شد.")
    await bot.send_message(chat_id= message.chat.id, text= "اگر میخواهید دوستان یا اشنایان خود را ثبت نام کنید میتوانید از دستور /start استفاده کنید.")
    message.author.set_state("") #reset state after payment



bot.run()
