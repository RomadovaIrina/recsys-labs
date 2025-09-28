from interface.apiDetector import logo_detect_gui
from service.api_1 import Api1
from service.api_2 import Api2
from dotenv import load_dotenv
import os

load_dotenv()


def main():
    api_key_1 = os.getenv("API_1_TOKEN")
    api_key_2 = os.getenv("API_2_TOKEN")

    api1 = Api1(api_key_1)
    api2 = Api2(api_key_2)

    logo_detect_gui(api1, api2)


if __name__ == "__main__":
    main()
