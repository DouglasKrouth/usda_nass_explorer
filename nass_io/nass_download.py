import requests
import logging
from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class NassDownload:
    """
    Manages process of fetching dataset links and files from USDA NASS website.
    """

    def __init__(self):
        self.nass_dataset_url = "https://www.nass.usda.gov/datasets/"
        self.resp_content = None
        self.dataset_links = None

    def display_nass_dataset_links(self):
        """
        Prints available USDA NASS datasets
        """
        if self.resp_content is None:
            self.get_nass_datasets_page()
        if self.dataset_links is None:
            self.get_list_of_available_dataset_urls()
        for i in self.dataset_links:
            print(i)

    # def download_dataset(self, url: str):
    #     """
    #     Downloads a USDA NASS dataset from the provided URL, unzips it, places it in 
    #     """

    def get_nass_datasets_page(self, num_retries:int = 3):
        """
        Sends a GET request to the USDA NASS dataset list page
        TODO : We should add exception handling to process multiple different cases (timeout, etc.). Right now it just prints exceptions to stdout with logging instead of waiting, checking network connection, etc.
        TODO : This is kinda gross to test, no coverage currently.
        ---
        num_retries, int : number of times to retry fetching the links page

        returns the requests.Response output from the datasets list page
        """
        attempt_incr = 0
        while attempt_incr < num_retries:
            try:
                logging.debug("Attempting to retrieve USDA NASS dataset page data from %s", self.nass_dataset_url)
                resp = requests.get(self.nass_dataset_url)
                resp.raise_for_status()  # raises exception when not a 2xx response
                if resp.status_code != 204:
                    self.resp_content = resp.content
                    logging.debug("Successfully retrieved USDA NASS dataset page data from %s", self.nass_dataset_url)
                    return
                else:
                    raise requests.RequestException("204 : Response had no body.")
            except requests.RequestException as e:
                attempt_incr += 1
                logging.error("Exception occurred during retrieval of USDA NASS dataset links : '%s'. Attempting again, %s retries remain.", e, num_retries - attempt_incr)
    
        raise NassDatasetPageRetrievalError("Unable to retrieve USDA NASS dataset links.")
    
    def get_list_of_available_dataset_urls(self):
        """
        Given a response from USDA NASS' dataset page response (class variable self.resp, HTML text output), create a list of the available datasets for download with BeautifulSoup.
        """
        if self.resp_content is None:
            raise ValueError("No value set for NassDownload.resp; call 'self.get_nass_datasets_page()' or set the resp (requests.Response) value manually.")

        def generate_full_download_links(shortened_file_path: str):
            """
            Files in href are in format "/downloads/<file_name>"; remove directory from path, join to url for full download url.
            """
            file_name = Path(shortened_file_path).parts[-1]
            return urljoin(self.nass_dataset_url, file_name)

        soup = BeautifulSoup(self.resp_content, 'html.parser')
        dataset_paths = []
        blocks = soup.find_all('div', 'block')
        for b in blocks:
            links = b.find_all("a", "gz", href=True)
            for l in links:
                dataset_download_link = generate_full_download_links(l["href"])
                dataset_paths.append(dataset_download_link)

        self.dataset_links = dataset_paths
        

class NassDatasetPageRetrievalError(Exception):
    def __init__(self, message):            
        # Call the base class constructor with the parameters it needs
        super().__init__(message)

def main():
    n = NassDownload()
    n.display_nass_dataset_links()

if __name__ == "__main__":
    main()
