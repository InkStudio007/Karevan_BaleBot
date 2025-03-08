from balethon import Client
from balethon.conditions import private, at_state, equals
from docx import Document
from docx.table import Table
from balethon.objects import Message, CallbackQuery, InlineKeyboard
from SignUp_validation import *

Bot = Client("815801327:OVUQjc5GFeURaJYgsP7VzMQYKmHdYngXMs4SXbsx")

SignUp_Datas = {
    "name" : [],
    "Phone_Number" : [],
    "Code_Meli" : [],
    "Age" : []
}

def is_admin(user_id):
    # لیست ID ادمین ها را در اینجا وارد کنید
    admin_ids = [1828929996]
    return user_id in admin_ids


#Commands
@Bot.on_command(private)
async def start(*, message):
    await message.reply(
        "Hello, I'm the commands bot Use /Help to see my commands"
    )


@Bot.on_command(private)
async def Help(*, message):
    await message.reply("/SignUp")


@Bot.on_command(private)
async def admin_panel(*, message):
    if is_admin(user_id= message.author.id) == True:
       await message.reply(
           "پنل مدیریت",
           InlineKeyboard(
               [("دریافت اسامی مسافران.", "name_text")],
               [("تعداد نفرات باقی مانده.", "remaining_capacity")],
               [("پاک کردن تمام داده ها.", "clear_data")]
            )
        )
       
    else:
        await message.reply("شما دسترسی به این دستور را ندارید.")


# SignUp Process
SignUp_Data = []

@Bot.on_message(at_state(None))
@Bot.on_command(private)
async def SignUp(*, message):
    await message.reply("What is your Name?")
    message.author.set_state("NAME")

@Bot.on_message(at_state("NAME"))
async def name_state(message):
    SignUp_Data.append(message.text)
    await message.reply("phone number?")
    message.author.set_state("PHONE NUMBER")

@Bot.on_message(at_state("PHONE NUMBER"))
async def phone_number_state(message):
    if validate_phone_number(message.text):
        SignUp_Data.append(message.text)
        await message.reply("code meli?")
        message.author.set_state("CODE MELI")    
    else:
        await message.reply("the phone number isnt correct try again:")
    
@Bot.on_message(at_state("CODE MELI"))
async def code_meli_state(message):
    if validate_code_meli(message.text):
        SignUp_Data.append(message.text)
        await message.reply("Age?")
        message.author.set_state("AGE")
    else:
        await message.reply("the Code Meli isnt correct try again:")

    
@Bot.on_message(at_state("AGE"))
async def age_state(message):
    if (validate_age(message.text)):
        SignUp_Data.append(message.text)
        await message.reply("SignUp Complete")
        await message.reply(f"name: {SignUp_Data[0]}, phone number: {SignUp_Data[1]}, code meli: {SignUp_Data[2]}, Age: {SignUp_Data[3]} Do You Comfirm? (Yes/No)")
        await message.author.set_state("SIGNUP_CONFIRMATION")
    else:
        await message.reply("the Age isnt correct try again:")

@Bot.on_message(at_state("SIGNUP_CONFIRMATION"))
async def SignUp_Confirmation_state(message):
    if (str(message.text).capitalize() == "Yes" or str(message.text).capitalize() == "No"):
        if (validate_SignUp(message.text)):
            for x in SignUp_Data:
                index = 0

                SignUp_Keys = SignUp_Datas.keys()
                SignUp_Datas[SignUp_Keys[index]].append(x)
                index += 1
        else:
            await message.reply("You Can /SignUp Again")
    else:
        await message.reply("I Didnt Understand Try Again:")


Bot.run()
