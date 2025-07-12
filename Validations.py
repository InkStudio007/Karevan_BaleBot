import phonenumbers


def validate_phone_number(number):
    try:
        parsed_number = phonenumbers.parse(number, "IR") 
        return phonenumbers.is_valid_number(parsed_number)
    except phonenumbers.NumberParseException:
        return False


def validate_code_meli(code_meli):
    if str(code_meli).isdigit() and len(str(code_meli)) == 10:
        return True
    else:
        return False


#def validate_age(age):
    #if str(age).isdigit() and 0 <= int(age) <= 120:
        #return True
    #else:
        #return False


def validate_confirm(Confirmation):
    if (str(Confirmation).capitalize() in ["Yes", "بله"]):
        return True
    elif (str(Confirmation).capitalize() in ["No", "خیر"]):
        return False


def validate_price(price):
    if (str(price).isdigit() and int(price) > 0):
        return True
    else:
        return False

def validate_credit_card(card):
    if (str(card).isdigit() and len(str(card)) == 16):
        return True
    else:
        return False 

def validate_capacity(price):
    if (str(price).isdigit() and int(price) > 0):
        return True
    else:
        return False
