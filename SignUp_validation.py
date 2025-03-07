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

def validate_age(age):
    if str(age).isdigit() and 0 <= int(age) <= 120:
        return True
    else:
        return False

def validate_SignUp(Confirmation):
    if (str(Confirmation).capitalize() == "Yes"):
        return True
    elif (str(Confirmation).capitalize() == "No"):
        return False

