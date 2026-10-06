import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.property_crop_service import PropertyImageRequest, crop_property_image


class FakeClient:
    def __init__(self):
        self.calls = []

    def smart_crop(self, image, aspect):
        self.calls.append((image, aspect))
        return {"image": image, "aspect": aspect, "url": f"https://cdn.example/{aspect}"}


def test_property_surfaces_get_storefront_aspects():
    client = FakeClient()
    result = crop_property_image(PropertyImageRequest("img_123"), client)
    assert [call[1] for call in client.calls] == ["4:3", "1:1", "3:4"]
    assert result["checkout"]["aspect"] == "1:1"
