import asyncio
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.append(ROOT_DIR)

from trade_republic.tr_client import TRClient  # noqa: E402


async def main():
    tr_client = TRClient(phone="", pin="", output_folder="output")

    print("1. Connected to the Trade Republic API via AccountService.")
    account_service = tr_client.account_service

    print("2. AccountService instance created successfully.")
    accounts_list = []
    accounts_list = await account_service.fetch_accounts()
    print(f"Accounts retrieved: {accounts_list}")


if __name__ == "__main__":
    asyncio.run(main())
    print("Program finished.")
