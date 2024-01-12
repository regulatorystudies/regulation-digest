from datetime import datetime
import logging
from pathlib import Path
from .retrieve_documents import retrieve_documents

if __name__ == "__main__":
    
    try:
        #test()
        retrieve_documents()
    except Exception as err:
        logging.exception("Error occurred while running program. Logging the output.")
        p = Path(__file__).parents[1]
        dt = datetime.now()
        with open(p / "error_log.txt", "a", encoding="utf-8") as f:
            f.write(f"Error logged at {dt}:\n{err}")
