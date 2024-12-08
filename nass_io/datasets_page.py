import requests
import logging

from requests.exceptions import RequestException
logger = logging.getLogger(__name__)

NASS_DATASET_LINK_URL = "https://www.nass.usda.gov/datasets/"

class NassDownload:
    def __init__(self):
        pass

    def get_nass_dataset_links(self, num_retries:int = 3) -> requests.Response:
        """
        Sends a GET request to the USDA NASS dataset list page
        TODO : We should add exception handling to process multiple different cases (timeout, etc.). Right now it just prints exceptions to stdout with logging instead of waiting, checking network connection, etc.
        ---
        num_retries, int : number of times to retry fetching the links page

        returns the requests.Response output from the datasets list page
        """
        attempt_incr = 0
        while attempt_incr < num_retries:
            try:
                logging.debug("Attempting to retrieve USDA NASS dataset links from %s", NASS_DATASET_LINK_URL)
                resp = requests.get(NASS_DATASET_LINK_URL)
                logging.debug("Successfully retrieved USDA NASS dataset links from %s", NASS_DATASET_LINK_URL)
                return resp
            except requests.RequestException as e:
                attempt_incr += 1
                logging.error("Exception occurred during retrieval of USDA NASS dataset links : '%s'. Attempting again, %s retries remain.", e, num_retries - attempt_incr)
    
        raise NassDatasetLinkRetrievalError("Unable to retrieve USDA NASS dataset links.")
    
    def generate_dataset_download_link(self, file_name:str ):
        """
        Given a file name from the USDA NASS dataset list page, generate a link that can be used to download the file.
        """
        
    

class NassDatasetLinkRetrievalError(Exception):
    def __init__(self, message):            
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
            

def main():
    logging.basicConfig(level=logging.DEBUG)
    get_nass_dataset_links()

if __name__ == "__main__":
    main()

