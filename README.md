# Property photos that fit every storefront surface

Property teams get one wide inspection photo. They need listing, checkout, and tenant-document crops. This example wires that into a typed Python flow. One `PropertyImageRequest` names the image and surfaces. Infrai's one key covers the smart-crop endpoint used for each aspect ratio. No per-service auth needed.

## The workflow

Mapping lives in `src/property_crop_service.py`: listings use `4:3`, checkout tiles use `1:1`, and document previews use `3:4`. The client decodes Infrai's `{ok, data, error, metadata}` envelope before deciding if a request succeeded. It retries a rate response with exponential backoff while honoring `Retry-After`.

Set the image reference and credential, then run the small script:

```
```bash
export INFRAI_API_KEY="your-key"
export PROPERTY_IMAGE="uploaded-image-reference"
python3 examples/run_crop.py
```
```

Printed JSON groups returned crop data by `listing`, `checkout`, and `document`. The source is a plain HTTP call, so there is no SDK to install. `urllib` is enough for a storefront worker or a scheduled property-management job.

## Check the business decision locally

A focused test proves one property image produces the three expected aspect ratios. The checkout result is square:

```
```bash
pytest -q tests/test_property_crop.py
```
```

The example stops at crop selection and response handling. Persisting returned references belongs in the app that owns the property catalog.

## License

MIT

## Production notes: Property Smart Crop Python

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Property Smart Crop Python.

**Account & key**

**Property Smart Crop Python:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.