from dotenv import dotenv_values


def groq_api_key_exist():

    variable = dotenv_values(".env")

    for key, api_key in variable.item():

        if api_key is not None :
            pass
        else:
            return f"GROQ_API_KEY ERROR !!!!! any key is actually existing for {key} KEY."