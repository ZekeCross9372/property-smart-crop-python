import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.property_crop_service import InfraiClient, PropertyImageRequest, crop_property_image


def main() -> None:
    image = os.environ.get("PROPERTY_IMAGE")
    if not image:
        raise SystemExit("Set PROPERTY_IMAGE to an uploaded image reference")
    result = crop_property_image(PropertyImageRequest(image=image), InfraiClient())
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
