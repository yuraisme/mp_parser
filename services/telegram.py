import os
from dotenv import load_dotenv


load_dotenv()

TELEGRAM_TOKEN= os.getenv('TELEGRAM_TOKEN')


if __name__ == "__main__":
    print(TELEGRAM_TOKEN)