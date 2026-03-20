from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = str(os.environ.get("SUPABASE_URL"))
SUPABASE_PUBLISHABLE_DEFAULT_KEY = str(os.environ.get("SUPABASE_PUBLISHABLE_DEFAULT_KEY"))
ORIGIN=str(os.environ.get("ORIGIN"))

supabase : Client= create_client(supabase_url=SUPABASE_URL, supabase_key=SUPABASE_PUBLISHABLE_DEFAULT_KEY)


async def login_magic_link(email: str):
    
    try:
        # send magic link
        response = supabase.auth.sign_in_with_otp({
            "email": email,
            "options":{
                "email_redirect_to": ORIGIN,
                "should_create_user": True
            }
        })
        if response:
            print(f"Magic link sent successfully to {email}!")

    except Exception as ex:
        print(f"Error when trying to send magic email: {ex}")    


async def validate_token(access_token: str) -> bool:
    try:
        # This method validates the token by checking with the Supabase Auth server
        user_data = supabase.auth.get_user(access_token)
        if user_data:
            print("User is valid:", user_data.user.email)
            return True
        return False
    except Exception as e:
        print("JWT validation failed:", e)
        return False