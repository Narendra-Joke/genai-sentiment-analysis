from pathlib import Path
import pandas as pd
import logging
# from app.utils.exceptions import CSVProcessingError
import sys
from app.core.exception import GenAIException

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = {
    "Product",
    "Content",
    "Author",
    "Country",
    "Rating",
    "Source",
    "isIngested"
}

# BASE_DIR = Path(__file__).resolve().parents[2]

# def load_csv(csv_path: str) -> pd.DataFrame:
#     try:
#         # csv_path = BASE_DIR/csv_path
#         # print("csv file path : ", csv_path)
#         df = pd.read_csv(csv_path)

#         missing = REQUIRED_COLUMNS - set(df.columns)
#         if missing:
#             raise CSVProcessingError(f"Missing columns in CSV: {missing}")

#         return df

#     except Exception as e:
#         logger.error(f"CSV loading failed: {e}")
#         raise CSVProcessingError(str(e))

def load_csv(csv_path: str) -> pd.DataFrame:
    """
    Load CSV with robust encoding handling.
    """

    try:
        try:
            # First attempt: UTF-8
            df = pd.read_csv(csv_path, encoding="utf-8")
        except UnicodeDecodeError:
            logger.warning(
                "UTF-8 decode failed, retrying with latin-1 encoding"
            )
            print("UTF-8 decode failed, retrying with latin-1 encoding")
            # Fallback: latin-1 (Windows-friendly)
            df = pd.read_csv(csv_path, encoding="latin-1")

        missing = REQUIRED_COLUMNS - set(df.columns)
        if missing:
            raise GenAIException(f"Missing columns in CSV: {missing}",sys)
        
        return df

    except Exception as e:
        logger.error(f"CSV loading failed: {e}")
        print(f"CSV loading failed: {e}")
        raise GenAIException(str(e),sys)

def get_pending_batch(df: pd.DataFrame, batch_size: int) -> pd.DataFrame:
    """
    Returns only reviews which are not ingested yet.
    """
    return df[df["isIngested"] == 0].head(batch_size)


def mark_as_ingested(
    df: pd.DataFrame,
    processed_indices: list,
    csv_path: str
):
    """
    Mark CSV rows as ingested ONLY after DB commit.
    """
    # csv_path = BASE_DIR/csv_path
    df.loc[processed_indices, "isIngested"] = 1
    df.to_csv(csv_path, index=False)
