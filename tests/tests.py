from pathlib import Path
from pprint import pprint

from requests import get

from regdigest.retrieve_documents import (
    BASE_PARAMS, 
    retrieve_results_by_next_page, 
    retrieve_results_by_page_range, 
)

from regdigest.preprocessing import *


# TEST OBJECTS AND UTILS #

TESTS_PATH = Path(__file__).parent

ENDPOINT_URL = r"https://www.federalregister.gov/api/v1/documents.json?"

TEST_PARAMS_FULL = {
    "per_page": 1000, 
    "page": 0, 
    "order": "oldest", 
    "conditions[publication_date][gte]": "2023-11-01", 
    "conditions[publication_date][lte]": "2023-11-30"
    }
TEST_RESPONSE_FULL = get(ENDPOINT_URL, TEST_PARAMS_FULL).json()

TEST_PARAMS_PARTIAL = {
    "per_page": 1000, 
    "page": 0, 
    "order": "oldest", 
    "conditions[publication_date][gte]": "2023-01-01", 
    "conditions[publication_date][lte]": "2023-06-30"
    }
TEST_URL_PARTIAL = get(ENDPOINT_URL, TEST_PARAMS_PARTIAL).url
TEST_RESPONSE_PARTIAL = get(ENDPOINT_URL, TEST_PARAMS_PARTIAL).json()
TEST_COUNT_PARTIAL = TEST_RESPONSE_PARTIAL["count"]


# retrieve_documents #


def test_retrieve_results_by_next_page_full(endpoint_url: str = ENDPOINT_URL, 
                                       dict_params: dict = BASE_PARAMS, 
                                       test_response = TEST_RESPONSE_FULL):
    
    dict_params.update({
        "conditions[publication_date][gte]": "2023-11-01", 
        "conditions[publication_date][lte]": "2023-11-30"
        })
    
    results = retrieve_results_by_next_page(endpoint_url, dict_params)
    assert len(results) == test_response.get("count")


def test_retrieve_results_by_next_page_partial(endpoint_url: str = ENDPOINT_URL, 
                                               dict_params: dict = BASE_PARAMS):
    
    dict_params.update({
        "conditions[publication_date][gte]": "2023-01-01", 
        "conditions[publication_date][lte]": "2023-06-30"
        })
    
    results = retrieve_results_by_next_page(endpoint_url, dict_params)
    assert len(results) == 10000, f"Should return 10000; compare to API call: {TEST_URL_PARTIAL}"


# tuple of all tests #


ALL_TESTS = (
    test_retrieve_results_by_next_page_full, 
    test_retrieve_results_by_next_page_partial, 
    )


if __name__ == "__main__":
    
    for func in ALL_TESTS:
        func()
    
    print("Tests complete.")
