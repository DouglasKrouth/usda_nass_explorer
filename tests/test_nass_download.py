from nass_io.nass_download import NassDownload
import pytest
from bs4 import BeautifulSoup
import os


@pytest.fixture
def get_test_resp_content_nass_data_page():
    """
    Allows us to bs4 parsing without needing to run a request every time.
    - May lead to regression if the page format changes drastically; unlikely as this is federal data
    """
    with open("tests/assets/test_resp_content_nass_data_page.txt", 'r') as f:
        test_resp_content = f.read()
    return test_resp_content

class TestClass:
    def test_get_list_of_available_datasets_error(self):
        n = NassDownload()
        with pytest.raises(ValueError):
            # no response data loaded
            n.get_list_of_available_dataset_urls()

    def test_get_list_of_available_datasets(self, get_test_resp_content_nass_data_page):
        n = NassDownload()
        n.resp_content = get_test_resp_content_nass_data_page
        n.get_list_of_available_dataset_urls()
        assert len(n.dataset_links) == 12
        assert 'https://www.nass.usda.gov/datasets/qs.animals_products_20241207.txt.gz' in n.dataset_links
        assert 'https://www.nass.usda.gov/datasets/qs.census2002.txt.gz' in n.dataset_links

    def test_display_nass_datasets(self, get_test_resp_content_nass_data_page, capsys):
        """
        Check that the statement prints twelve lines. Bit of a silly test.
        """
        n = NassDownload()
        n.resp_content = get_test_resp_content_nass_data_page
        n.display_nass_dataset_links()
        out, err = capsys.readouterr()
        assert len(out.splitlines()) == 12
