# ASCII art

Animated 3D ASCII art, made with Python, numpy and pygame. All of it in one place,
with a folder for each piece.

| Art | What happens | Code | Video |
| --- | --- | --- | --- |
| **Bloom** | A flower blooms, then blows away | [bloom3d.py](bloom/bloom3d.py) | [Watch](bloom/bloom3d.mp4) |
| **Butterfly** | A chrysalis cracks open and a butterfly flies out | [butterfly.py](butterfly/butterfly.py) | [Watch](butterfly/butterfly.mp4) |

## Get all of them

    git clone https://github.com/edwardjones7/flower-ascii-art.git
    cd flower-ascii-art
    pip install -r requirements.txt

## Run

    python bloom/bloom3d.py
    python butterfly/butterfly.py

Space restarts, Esc quits. Uses the Consolas font (included with Windows).
Other systems may fall back to another font, so the look can differ.

## Export a video (needs ffmpeg)

Add `--record` to save the frames, then turn them into a video:

    python bloom/bloom3d.py --record
    ffmpeg -framerate 30 -i frames3d/f_%04d.png -c:v libx264 -pix_fmt yuv420p bloom3d.mp4

    python butterfly/butterfly.py --record
    ffmpeg -framerate 30 -i frames/f_%04d.png -c:v libx264 -pix_fmt yuv420p butterfly.mp4

By @edjonesai
