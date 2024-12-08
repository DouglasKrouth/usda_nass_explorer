from nass_io.nass_download import NassDownload
import pytest

class TestClass:

    def test_get_list_of_available_datasets_error(self):
        r = NassDownload()
        with pytest.raises(ValueError):
            # no data loaded
            r.get_list_of_available_datasets()
