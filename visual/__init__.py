"""Screenshot comparison against committed baselines.

DOM assertions prove an element exists; they can't tell that a product shows
the wrong image or that a stylesheet stopped loading. Comparing screenshots
catches that class of bug.

Exact pixel equality is too brittle: glyph hinting and anti-aliasing differ
between machines, so every line of text shifts by a sub-pixel. Both images are
softened with a small blur first, which removes that edge noise but keeps real
changes such as a swapped image, a moved block or a colour change. After that a
pixel only counts as changed when a channel moves by more than
`PIXEL_TOLERANCE`, and a page fails only when more than `MAX_DIFF_RATIO` of its
pixels changed. Baselines are stored per browser,
because Chromium and Firefox render text differently. They are recorded on
Linux to match CI, so a local run on macOS or Windows may differ.

Run `pytest -m visual --update-snapshots` to record new baselines after an
intended UI change, then review the PNGs in the diff before committing.
"""

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter

BASELINE_DIR = Path(__file__).parent / "baselines"
OUTPUT_DIR = Path("test-results") / "visual"

# Enough to wash out sub-pixel text differences between CI and a local run.
BLUR_RADIUS = 1.5
# 0-255 per channel. Absorbs anti-aliasing noise, not a real colour change.
PIXEL_TOLERANCE = 40
# Share of pixels allowed to change before the page counts as different.
MAX_DIFF_RATIO = 0.01

# A fixed viewport keeps screenshots the same size on every machine.
VIEWPORT = {"width": 1280, "height": 720}


@dataclass(frozen=True)
class Comparison:
    diff_ratio: float
    size_matches: bool
    diff_image: Image.Image | None

    @property
    def passed(self) -> bool:
        return self.size_matches and self.diff_ratio <= MAX_DIFF_RATIO


def baseline_path(browser: str, name: str) -> Path:
    return BASELINE_DIR / browser / f"{name}.png"


def compare(actual: Image.Image, expected: Image.Image) -> Comparison:
    """Compare two screenshots and return the share of pixels that changed."""
    actual, expected = actual.convert("RGB"), expected.convert("RGB")
    if actual.size != expected.size:
        return Comparison(diff_ratio=1.0, size_matches=False, diff_image=None)

    # Largest channel difference per pixel, then a 0/255 mask of changed pixels.
    blur = ImageFilter.GaussianBlur(BLUR_RADIUS)
    delta = ImageChops.difference(actual.filter(blur), expected.filter(blur))
    per_pixel = ImageChops.lighter(ImageChops.lighter(*delta.split()[:2]), delta.split()[2])
    mask = per_pixel.point(lambda v: 255 if v > PIXEL_TOLERANCE else 0)

    changed = mask.histogram()[255]
    ratio = changed / (actual.width * actual.height)

    # Changed pixels in red over a faded copy of the baseline.
    faded = Image.blend(expected, Image.new("RGB", expected.size, "white"), 0.7)
    diff_image = Image.composite(Image.new("RGB", expected.size, "red"), faded, mask)
    return Comparison(diff_ratio=ratio, size_matches=True, diff_image=diff_image)


def load(png: bytes | Path) -> Image.Image:
    data = png.read_bytes() if isinstance(png, Path) else png
    return Image.open(BytesIO(data))


def save_failure_artifacts(browser: str, name: str, actual: Image.Image, result: Comparison) -> Path:
    """Write actual and diff images next to the other CI artifacts."""
    out = OUTPUT_DIR / browser
    out.mkdir(parents=True, exist_ok=True)
    actual.save(out / f"{name}-actual.png")
    if result.diff_image is not None:
        result.diff_image.save(out / f"{name}-diff.png")
    return out
