import requests
import logging
from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import shutil
import os

from nass_io.downloader import download

logger = logging.getLogger(__name__)


class NassDownload:
    """
    Manages process of fetching dataset links and files from USDA NASS website.
    Caveat : This class is a Band-Aid for retrieving the data and maintaining an on-premise or managed copy of the data. It's a hacky way of scraping dataset links for downloads that would work better if it was formalized into a managed ETL/database solution
    TODO's:
        - method I/O is coupled to scraping the dataset page's HTML; this isn't a huge deal currently but it'd lead to problems in the future if a package like this was supposed to be used in a pipeline.
    """
    resp_content: requests.Response | None
    dataset_links: list[str] | None

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

    def download_nass_dataset_file(self, urls: list[str]):
        """
        public method to download a USDA NASS file given the url. Checks whether the URL is "valid" (lazy, checks if it's in the links from the dataset page)
        url, str : A download url from the USDA NASS data set page.
        """
        if self.dataset_links is None:
            logging.debug("self.dataset_links was None; retrieving.")
            self.get_nass_datasets_page()
            self.get_list_of_available_dataset_urls()
        for u in urls:
            if self.dataset_links is not None and u not in self.dataset_links:
                logging.debug("self.dataset_links specified; url passed was not in self.dataset_links. Output of self.dataset_links below\n%s", self.dataset_links)
                raise ValueError("URL provided (`{}`) does not exist as a dataset on the USDA NASS datasets page.".format(u))
        download(urls, dest_dir="./")
    
        # local_file_names = self._download_file(url)
        # return local_file_name
        
    # def _download_file(self, url: str):
    #     """
    #     Internal helper that handles writing the file to disk.
    #     For a given dataset url, attempt to download it to the local working directory.
    #     - Since this will be placed in '/app' on the docker image, we don't pass a file path. An easy addition would be to enable passing a desired file path and downloading the file to that location.
    #     - Taken from : https://stackoverflow.com/a/39217788
    #     ---
    #     url, str : download url passed from download_nass_dataset_file
    #
    #     returns the file path where the downloaded dataset (.txt.gz) file was placed
    #     """
    #     local_file_name = url.split('/')[-1]
    #     with requests.get(url, stream=True) as r:
    #         with open(local_file_name, 'wb') as f:
    #             shutil.copyfileobj(r.raw, f)
    #
    #     return local_file_name

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
    # NOTE : This is a sloppy hack to get around actually testing file download behavior.
    n.download_nass_dataset_file(["https://www.nass.usda.gov/datasets/qs.census2002.txt.gz", "https://www.nass.usda.gov/datasets/qs.census2007.txt.gz"])

if __name__ == "__main__":
    main()
