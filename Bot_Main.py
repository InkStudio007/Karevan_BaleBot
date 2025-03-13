from asyncio import BaseEventLoop
from balethon import Client
from balethon.conditions import private, at_state, equals, successful_payment
#from docx import Document
#from docx.table import Table
from balethon.objects import Message, CallbackQuery, InlineKeyboard, InlineKeyboardButton, LabeledPrice
from Validations import *
import os


#Variables

title, description, price, credit_card = "", "", "", ""
startpanel_description = ""
Start_SignUp = False
SignUp_capacity = "1"
SignUp_count = 0
setting_payment_message_id = 0
signup_payment_message_id = 0

bot = Client(token= "815801327:OVUQjc5GFeURaJYgsP7VzMQYKmHdYngXMs4SXbsx")


#Checking for Payment Settings
def payment_settings_check():
    if ("" in (title, description, price, credit_card)):
        return False
    else:
        return True


SignUp_Datas = {
    "Name" : [],
    "Phone_Number" : [],
    "Code_Meli" : [],
    "Age" : []
}

SignUp_Keys = ["Name", "Phone_Number", "Code_Meli", "Age"]

def is_admin(user_id):
    # لیست ID ادمین ها را در اینجا وارد کنید
    admin_ids = [403949029]
    return user_id in admin_ids


#Commands

@bot.on_command(private)
async def admin_panel(*, message):
    if is_admin(user_id= message.author.id) == True:
        if (Start_SignUp):
            await message.reply(
                "پنل مدیریت",
                InlineKeyboard(
                    [("اتمام ثبت نام.", "stop_signup")],
                    [("دریافت اسامی مسافران.", "passengers_list")],
                    [("تعداد نفرات باقی مانده.", "remaining_capacity")],
                    [("تنظیمات پرداخت.", "payment_settings")]
                )
            )
        else:
            await message.reply(
                "پنل مدیریت",
                InlineKeyboard(
                    [("شروع ثبت نام.", "start_signup")],
                    [("تنظیمات پرداخت.", "payment_settings")]
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
    

#Admin Panel CallBacks

@bot.on_callback_query()
async def admin_callback_handler(callback_query):
    print(callback_query.data)

    if callback_query.data == "passengers_list":

        await callback_query.answer("passengers_list code")

    elif callback_query.data == "remaining_capacity":

        global SignUp_capacity, SignUp_count
        remaining_capacity = int(SignUp_capacity) - SignUp_count

        await callback_query.answer(f"remaining capacity is: {remaining_capacity}")

    elif callback_query.data == "payment_settings":

        await callback_query.answer("Please send any message to continue to Payment Settings")
        callback_query.author.set_state("PAYMENT_SETTINGS")

    elif callback_query.data == "start_signup":

        if (payment_settings_check()):
            await callback_query.answer("Please send any message to continue to begining the SignUp process")
            callback_query.author.set_state("TRIP_INFORMATION")

        else:
            await callback_query.answer("Payment settings hasnt been set to any values")

    elif callback_query.data == "stop_signup":

        global Start_SignUp
        Start_SignUp = False

        await callback_query.answer("SignUp is finished have a good trip")


# Trip Information

@bot.on_message(at_state("TRIP_INFORMATION"))
async def trip_information(message):
    await bot.send_message(chat_id= message.chat.id ,text= "Trip Description?")
    message.author.set_state("TRIP_DESCRIPTION")


@bot.on_message(at_state("TRIP_DESCRIPTION"))
async def trip_description_state(message):
    global startpanel_description
    start_panel_description = message.text

    await bot.send_message(chat_id= message.chat.id, text= "how much is SignUp capacity?")
    message.author.set_state("SIGNUP_CAPACITY")

@bot.on_message(at_state("SIGNUP_CAPACITY"))
async def SignUp_capacity_state(message):
    global Start_SignUp
    global SignUp_capacity

    SignUp_capacity = message.text

    Start_SignUp = True
    await bot.send_message(chat_id= message.chat.id, text= "SignUp process has begun")

    message.author.set_state(None)


# Payment Settings

@bot.on_message(at_state("PAYMENT_SETTINGS"))
async def Payment_Settings(message):
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
    global setting_payment_message_id

    if (validate_credit_card(message.text)):
        credit_card = message.text

        payment_message = await bot.send_invoice(
                chat_id=message.chat.id,
                title= title,
                description= description,
                payload=str(message.author.id),
                provider_token= credit_card,
                prices= [LabeledPrice(label="Some label", amount= int(price))]
            )

        setting_payment_message_id = payment_message.id

        await bot.send_message(chat_id= message.chat.id, text= "Do You confirm the payment settings (Yes/No)?")
        message.author.set_state("PAYMENT_CONFIRMATION")

    else:
        await message.reply("the credit card isnt correct try again:")


@bot.on_message(at_state("PAYMENT_CONFIRMATION"))
async def payment_confirmation_state(message):
    global setting_payment_message_id

    if str(message.text).capitalize() in ("Yes", "No"):

        if validate_confirm(message.text):

            await message.reply("The Payment settings are set up successfuly")
            await bot.delete_message(message.chat.id, setting_payment_message_id)

            message.author.set_state("SIGNUP") #reset state after confirmation
        else:

            await message.reply("try again with /payment_settings")
            message.author.set_state(None) #reset state after no confirmation
    else:
        await message.reply("i didnt understand try again:")


# SignUp Process

SignUp_Data = []

if (Start_SignUp):

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
                await message.reply("Please send any message to continue to Payment.")
            else:
                await message.reply("You Can /SignUp Again")
                message.author.set_state(None)
                SignUp_Data.Clear()
        else:
            await message.reply("I Didn't Understand. Try Again:")


    #Payment System


    @bot.on_message(at_state("PAYMENT"))
    async def payment_state(message):
        global signup_payment_message_id

        await message.reply("Processing payment...")

        payment_message = await bot.send_invoice(
            chat_id=message.chat.id,
            title= title,
            description= description,
            payload=str(message.author.id),
            provider_token= credit_card,  
            prices=[LabeledPrice(label="Some label", amount= int(price))]
        )

        signup_payment_message_id = payment_message.id


    @bot.on_message(successful_payment)
    async def show_payment(message):
        global SignUp_count
        global signup_payment_message_id
    
        await bot.delete_message(message.chat.id, signup_payment_message_id)

        user = await client.get_chat(message.successful_payment.invoice_payload)
        amount = message.successful_payment.total_amount
        print(f"{user.name}, paid {amount}")

        #adding client to the list
        for x in SignUp_Data:
            index = 0

            SignUp_Datas[SignUp_Keys[index]].append(x)
            index += 1

        index = 0
        SignUp_count += 1 
        SignUp_Data.clear()

        await bot.send_message(chat_id= message.chat.id, text= "SignUp Completed")
        await bot.send_message(chat_id= message.chat.id, text= "You can SignUp others with /SignUp")
        message.author.set_state(None) #reset state after payment
else:

    @bot.on_command()
    async def SignUp(*, message):
        await bot.send_message(chat_id= message.chat.id, text= "SignUp has ended wait for the next trip")

bot.run()
