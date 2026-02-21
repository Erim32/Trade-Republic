import json
import os

import pandas as pd
from dotenv import load_dotenv

from trade_republic.utils.logger import logger

load_dotenv()


class TRUtils:
    """
    Utility class for common operations.
    """

    ###############################################
    # Portfolio to CSV
    ###############################################

    @staticmethod
    def format_amount(amount: float) -> str:
        """
        Formats an amount by adding thousand separators and rounding to two decimal places.

        :param amount: Amount to format.
        :return: Formatted string representing the amount.
        """
        return f"{amount:,.2f}".replace(",", " ").replace(".", ",")

    @staticmethod
    def save_json(data: dict | list[dict], filepath: str, output_folder: str = ""):
        """
        Saves data in JSON format to a file.

        :param data: Data to save.
        :param filepath: Output file path.
        """
        if output_folder:
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            filepath = os.path.join(output_folder, filepath)

        logger.info(f"Saving data to '{filepath}'")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    @staticmethod
    def load_json_from_file(file_path: str, output_folder: str = "") -> dict:
        if output_folder:
            file_path = os.path.join(output_folder, file_path)

        logger.info(f"Loading data from '{file_path}'")
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def display_json(data: dict):
        """
        Displays JSON data in a formatted way.

        :param data: JSON data to display.
        """
        logger.debug(json.dumps(data, indent=4, ensure_ascii=False))

    ###################################################
    # Account
    ####################################################

    @staticmethod
    def create_empty_account(account_name: str) -> dict:
        """
        Creates an empty account dictionary according to product type.

        Args:
            account_name: Account name

        Returns:
            Initialized account dictionary
        """
        return {
            "name": account_name,
            "cash_account": None,
            "securities_account": None,
            "currency": None,
        }

    ###################################################
    # Serialization and Data Transformation
    ##################################################
    @staticmethod
    def transform_timestamp_columns(
        df: pd.DataFrame,
        columns: list[str] | None = None,
        date_format: str = "%d/%m/%Y",
    ) -> pd.DataFrame:
        """
        Transforms timestamp columns to readable date format.

        Args:
            df: DataFrame to transform
            columns: List of columns to transform
            date_format: Output date format

        Returns:
            DataFrame with transformed timestamp columns
        """

        DEFAULT_TIMESTAMP_COLUMNS = ["timestamp"]

        if columns is None:
            columns = DEFAULT_TIMESTAMP_COLUMNS

        df_copy = df.copy()
        for col in columns:
            if col in df_copy.columns:
                df_copy[col] = pd.to_datetime(df_copy[col], errors="coerce").dt.strftime(date_format)

        return df_copy

    @staticmethod
    def transform_amount_columns(df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
        """
        Transforms amount columns (converts dots to commas).

        Args:
            df: DataFrame to transform
            columns: List of columns to transform

        Returns:
            DataFrame with transformed amount columns
        """
        DEFAULT_AMOUNT_COLUMNS = [
            "amount.value",
            "amount.fractionDigits",
            "subAmount.value",
            "subAmount.fractionDigits",
        ]

        if columns is None:
            columns = DEFAULT_AMOUNT_COLUMNS

        df_copy = df.copy()
        for col in columns:
            if col in df_copy.columns:
                df_copy[col] = pd.to_numeric(df_copy[col], errors="coerce")
                df_copy[col] = df_copy[col].apply(lambda x: str(x).replace(".", ",") if pd.notna(x) else x)

        return df_copy

    @staticmethod
    def transform_all(df: pd.DataFrame) -> pd.DataFrame:
        """
        Applies all type transformations to a DataFrame.

        Args:
            df: DataFrame to transform

        Returns:
            Transformed DataFrame
        """
        df = TRUtils.transform_timestamp_columns(df)
        df = TRUtils.transform_amount_columns(df)
        return df

    ###################################################
    # Files Manager
    ###################################################

    @staticmethod
    def flatten_and_clean_json(all_data: list[dict], sep: str = ".") -> list[dict]:
        """
        Flattens nested JSON data and preserves column order.

        :param all_data: List of JSON dictionaries to flatten.
        :param sep: Separator used for flattened keys.
        :return: List of flattened and cleaned dictionaries.
        """
        all_keys = []
        flattened_data = []

        def flatten(nested_json: dict, parent_key: str = "") -> dict:
            """Recursively flattens nested JSON."""
            flat_dict = {}
            for key, value in nested_json.items():
                new_key = f"{parent_key}{sep}{key}" if parent_key else key
                if isinstance(value, dict):
                    flat_dict.update(flatten(value, new_key))
                else:
                    flat_dict[new_key] = value

                if new_key not in all_keys:
                    all_keys.append(new_key)

            return flat_dict

        for item in all_data:
            flat_item = flatten(item)
            flattened_data.append(flat_item)

        complete_data = [{key: item.get(key, None) for key in all_keys} for item in flattened_data]

        return complete_data

    @staticmethod
    def save_data(data: list | dict, filepath: str, output_folder: str = ""):
        """
        Saves data in the specified format.

        :param data: Data to save.
        :param filename: Base filename (without extension).
        """

        if not data:
            logger.warning(f"No data to save to '{filepath}'")
            return

        if output_folder:
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            filepath = os.path.join(output_folder, filepath)

        output_format = filepath.split(".")[-1].lower()
        if output_format == "json":
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            logger.info(f"Data saved in '{filepath}'")
        elif output_format == "csv":
            data_list = data if isinstance(data, list) else [data]
            flattened_data = TRUtils.flatten_and_clean_json(data_list)
            if flattened_data:
                df = pd.DataFrame(flattened_data)
                df = df.dropna(axis=1, how="all")
                df = TRUtils.transform_all(df)
                df.to_csv(f"{filepath}", index=False, sep=";", encoding="utf-8-sig")
                logger.info(f"Data saved in '{filepath}'")
        else:
            logger.warning(f"Unsupported file format for '{filepath}'")
