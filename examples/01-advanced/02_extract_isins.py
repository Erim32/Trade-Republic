import asyncio
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
sys.path.append(ROOT_DIR)

from trade_republic.tr_client import TRClient  # noqa: E402
from trade_republic.utils.tr_utils import TRUtils  # noqa: E402


async def main():
    PROJECT_NAME = "02_extract_isins"
    OUTPUT_FOLDER = os.path.join("output", "examples", PROJECT_NAME)

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # Initialize the TRClient, Works only with only 1 concurrent connection to avoid hitting rate limits when fetching instruments
    tr_client = TRClient(phone="", pin="", output_folder=OUTPUT_FOLDER, max_concurrent_connections=1)
    instrument_service = tr_client.instrument_service

    # Fetch all instruments
    # instruments = await instrument_service.fetch_instruments()

    # TRUtils.save_json(instruments, "02_all_instruments.json", output_folder=OUTPUT_FOLDER)
    # wait 60 seconds to avoid hitting rate limits when fetching instrument details
    print("Waiting 60 seconds to avoid hitting rate limits when fetching instrument details...")
    await asyncio.sleep(60)
    # Load instruments from file if already saved, otherwise fetch and save
    instruments = TRUtils.load_json_from_file("02_all_instruments.json", output_folder=OUTPUT_FOLDER)

    # Enrich instruments with instrument_info
    enriched_instruments = []
    for instrument in instruments:
        isin = instrument.get("isin")
        if isin:
            try:
                print(
                    f"Fetching instrument details for ISIN: {isin} ({len(enriched_instruments) + 1}/{len(instruments)})"
                )
                instrument_info = await instrument_service.fetch_instrument(isin)
                instrument["instrument_info"] = instrument_info
            except Exception as e:
                print(f"Error fetching instrument details for ISIN {isin}: {e}")
                instrument["instrument_info"] = {}
            enriched_instruments.append(instrument)

    TRUtils.save_json(
        enriched_instruments,
        "02_all_instruments_with_infos.json",
        output_folder=OUTPUT_FOLDER,
    )


if __name__ == "__main__":
    asyncio.run(main())
