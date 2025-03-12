from asyncio import BaseEventLoop
from balethon import Client
from balethon.conditions import private, at_state, equals, successful_payment
#from docx import Document
#from docx.table import Table
from balethon.objects import Message, CallbackQuery, InlineKeyboard, InlineKeyboardButton, LabeledPrice
from Validations import *
import os


#Variables

title, description, price, credit_card = "", "", "1", ""


bot = Client(token= "815801327:OVUQjc5GFeURaJYgsP7VzMQYKmHdYngXMs4SXbsx")

SignUp_Datas = {
    "Name" : [],
    "Phone_Number" : [],
    "Code_Meli" : [],
    "Age" : []
}

SignUp_Keys = ["Name", "Phone_Number", "Code_Meli", "Age"]

def is_admin(user_id):
    # لیست ID ادمین ها را در اینجا وارد کنید
    admin_ids = [1828929996]
    return user_id in admin_ids


#Commands

@bot.on_command(private)
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


@bot.on_command(private)
async def start(*, message):
    await message.reply(
         '''سلام به بات ثبت نام در کاروان زیارتی 315 خوش امدید
برای ادامه  ثبت نام اول عضو چنل شید و بعد روی دکمه(عضو شدم)کلیک کنید.''',
        InlineKeyboard(
            [InlineKeyboardButton('چنل کاروان315', url='https://ble.ir/karevan_ziarati')],
            [('عضو شد.', 'join')],
            [("ثبت نام.", "signup")]
        )
    )

    message.author.set_state(None)
    SignUp_Data.Clear()


@bot.on_command(private)
async def Help(*, message):
    await bot.send_message(chat_id= message.chat.id, text= "/SignUp")
    

# Payment Settings

@bot.on_command(private)
async def Payment_Settings(*, message):
    await bot.send_message(chat_id= message.chat.id, text= "Title?")
    message.author.set_state("TITLE")


@bot.on_message(at_state("TITLE"))
async def title_state(message):
    global title
    title = message.text

    await bot.send_message(chat_id= message.chat.id, text= "Description?")
    message.author.set_state("DESCRIPTION")


@bot.on_message(at_state("DESCRIPTION"))
async def description_state(message):
    global description
    description = message.text

    await bot.send_message(chat_id= message.chat.id, text= "Price?")
    message.author.set_state("PRICE")


@bot.on_message(at_state("PRICE"))
async def price_state(message):
    global price
    if(validate_price(message.text)):
        price = message.text

        await bot.send_message(chat_id= message.chat.id, text= "credit card?")
        message.author.set_state("CREDIT_CARD")
    else:
        await message.reply("the price isnt correct try again:")


@bot.on_message(at_state("CREDIT_CARD"))
async def credit_card_state(message):
    global credit_card
    if (validate_credit_card(message.text)):
        credit_card = message.text

        await bot.send_invoice(
                chat_id=message.chat.id,
                title= title,
                description= description,
                payload=str(message.author.id),
                provider_token= credit_card,
                prices= [LabeledPrice(label="Some label", amount= int(price))]
            )

        await bot.send_message(chat_id= message.chat.id, text= "Do You confirm the payment settings (Yes/No)?")
        message.author.set_state("PAYMENT_CONFIRMATION")

    else:
        await message.reply("the credit card isnt correct try again:")


@bot.on_message(at_state("PAYMENT_CONFIRMATION"))
async def payment_confirmation_state(message):
    if str(message.text).capitalize() in ("Yes", "No"):

        if validate_confirm(message.text):

            await message.reply("The Payment settings are set up successfuly")
            message.author.set_state("SIGNUP") #reset state after confirmation
        else:

            await message.reply("try again with /payment_settings")
            message.author.set_state(None) #reset state after no confirmation
    else:
        await message.reply("i didnt understand try again:")


# SignUp Process

SignUp_Data = []

@bot.on_message(at_state("SignUp"))
@bot.on_command(private)
async def SignUp(*, message):
    await bot.send_message(chat_id= message.chat.id, text= "What is your Name?")
    message.author.set_state("NAME")
            
@bot.on_message(at_state("NAME"))
async def name_state(message):
    SignUp_Data.append(message.text)
    await bot.send_message(chat_id= message.chat.id, text= "phone number?")
    message.author.set_state("PHONE_NUMBER")


@bot.on_message(at_state("PHONE_NUMBER"))
async def phone_number_state(message):
    if validate_phone_number(message.text):
        SignUp_Data.append(message.text)

        await bot.send_message(chat_id= message.chat.id, text= "code meli?")
        message.author.set_state("CODE_MELI")    
    else:
        await message.reply("the phone number isnt correct try again:")


@bot.on_message(at_state("CODE_MELI"))
async def code_meli_state(message):
    if validate_code_meli(message.text):
        SignUp_Data.append(message.text)
        await bot.send_message(chat_id= message.chat.id, text= "Age?")
        message.author.set_state("AGE")
    else:
        await message.reply("the Code Meli isnt correct try again:")


@bot.on_message(at_state("AGE"))
async def age_state(message):
    if (validate_age(message.text)):
        SignUp_Data.append(message.text)
                    
        await bot.send_message(chat_id= message.chat.id, text=
        f"name: {SignUp_Data[0]}, phone number: {SignUp_Data[1]}, code meli: {SignUp_Data[2]}, Age: {SignUp_Data[3]} Do You Comfirm? (Yes/No)"
        )

        message.author.set_state("SIGNUP_CONFIRMATION")
    else:
        await message.reply("the Age isnt correct try again:")


@bot.on_message(at_state("SIGNUP_CONFIRMATION"))
async def SignUp_Confirmation_state(message):
    if str(message.text).capitalize() == "Yes" or str(message.text).capitalize() == "No":
        if validate_confirm(message.text):
            message.author.set_state("PAYMENT")  
            await message.reply("Please send any message to continue to Payment.")  # 🚀 Ask user to send another message
        else:
            await message.reply("You Can /SignUp Again")
            message.author.set_state(None)
            SignUp_Data.Clear()
    else:
        await message.reply("I Didn't Understand. Try Again:")


#Payment System


@bot.on_message(at_state("PAYMENT"))
async def payment_state(message):
    await message.reply("Processing payment...")

    await bot.send_invoice(
        chat_id=message.chat.id,
        title= title,
        description= description,
        payload=str(message.author.id),
        provider_token= credit_card,  
        prices=[LabeledPrice(label="Some label", amount= int(price))]
    )


@bot.on_message(successful_payment)
async def show_payment(message):
    user = await client.get_chat(message.successful_payment.invoice_payload)
    amount = message.successful_payment.total_amount
    print(f"{user.name}, paid {amount}")

    #adding client to the list
    for x in SignUp_Data:
        index = 0

        SignUp_Datas[SignUp_Keys[index]].append(x)
        index += 1

    index = 0
    SignUp_Data.clear()

    await bot.send_message(chat_id= message.chat.id, text= "SignUp Completed")
    await bot.send_message(chat_id= message.chat.id, text= "You can SignUp others with /SignUp")
    message.author.set_state(None) #reset state after payment


bot.run()
