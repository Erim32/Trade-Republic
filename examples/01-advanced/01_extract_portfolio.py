import asyncio
import os
import sys

import pandas as pd

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
sys.path.append(ROOT_DIR)

from trade_republic.tr_client import TRClient  # noqa: E402


async def main():
    PROJECT_NAME = "01_extract_portfolio"
    OUTPUT_FOLDER = os.path.join("output", "examples", PROJECT_NAME)

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    tr_client = TRClient(phone="", pin="", output_folder=OUTPUT_FOLDER)

    portfolio_service = tr_client.portfolio_service
    portfolio_positions: list = await portfolio_service.fetch_portfolio_positions(tr_client, True, True)

    # convert to csv with valuation
    # remove structure, keep only item level 1 fields
    portfolio_positions_simple = []
    from datetime import datetime

    date_ddmmyyyy = datetime.now().strftime("%d/%m/%Y")
    for position in portfolio_positions:
        current_price = float(position.get("current_price", 0))
        current_quantity = float(position.get("netSize", 0))
        average_buy_in = float(position.get("averageBuyIn", 0))
        unrealized_pl = (current_price - average_buy_in) * current_quantity
        unrealized_percent = (current_price - average_buy_in) / average_buy_in
        simple_position = {
            "Broker": "Trade Republic",
            "Account": position.get("account_label"),
            "Type": position.get("instrumentType"),
            "isin": position.get("isin"),
            "ticker": position.get("ticker"),
            "name": position.get("name"),
            "quantity": current_quantity,
            "Avg Buy In": f"{average_buy_in:.2f}",
            "currentPrice": f"{current_price:.2f}",
            "Current Value": f"{position.get('current_valuation'):.0f}",
            "Unrealized P&L": f"{unrealized_pl:.0f}",
            "Unrealized %": f"{unrealized_percent:.2f}",
            "Refresh date": date_ddmmyyyy,
        }
        portfolio_positions_simple.append(simple_position)

    df = pd.DataFrame(portfolio_positions_simple)

    csv_path = os.path.join(OUTPUT_FOLDER, f"{PROJECT_NAME}.csv")
    df.to_csv(csv_path, index=False, sep=";")
    print(f"Portfolio with valuation saved to {csv_path}")

    tr_client.save_json(portfolio_positions, f"{PROJECT_NAME}.json")

    print(f"Portfolio with valuation saved to {OUTPUT_FOLDER}/{PROJECT_NAME}.json")


if __name__ == "__main__":
    asyncio.run(main())
