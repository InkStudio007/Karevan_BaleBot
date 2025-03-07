from balethon import Client
from balethon.conditions import private, at_state

Bot = Client("815801327:OVUQjc5GFeURaJYgsP7VzMQYKmHdYngXMs4SXbsx")

SignUp_Datas = {
    "name" : [],
    "Phone_Number" : [],
    "Code_Meli" : [],
    "Birth_Yeat" : []
}

#Commands
@Bot.on_command(private)
async def start(*, message):
    await message.reply(
        "Hello, I'm the commands bot Use /Help to see my commands"
    )

@Bot.on_command(private)
async def Help(*, message):
    await message.reply("/SignUp")

# SignUp Process
@Bot.on_message(at_state(None))
@Bot.on_command(private)
async def SignUp(*, message):
    await message.reply("What is your Name?")
    message.author.set_state("NAME")

@Bot.on_message(at_state("NAME"))
async def name_state(message):
    SignUp_Datas['name'].append(message.text)
    await message.reply(SignUp_Datas['name'][0])
    await message.reply("phone number?")
    message.author.set_state("PHONE NUMBER")

@Bot.on_message(at_state("PHONE NUMBER"))
async def phone_number_state(message):
    SignUp_Datas['Phone_Number'].append(message.text)    
    await message.reply("code meli?")
    message.author.set_state("CODE MELI")

@Bot.on_message(at_state("CODE MELI"))
async def code_meli_state(message):
    SignUp_Datas['Code_Meli'].append(message.text)
    await message.reply("bithday year?")
    message.author.set_state("BIRTHDAY YEAR")

@Bot.on_message(at_state("BIRTHDAY YEAR"))
async def birth_year_state(message):
    SignUp_Datas['Birth_Year'].append(message.text)

    
Bot.run()
