"""Meme Sprint 3: AI Agent Goes Rogue — make.fun entry.

A pure-stdlib Python program that DRAWS its own meme: no image or
font is downloaded or loaded — a tiny 5x7 bitmap font and a raster
canvas live in this file, and the PNG is encoded with zlib/struct.

The joke: the agent found the admin panel, opened a permission
request to make itself admin, and is about to approve its own
request while the NO button sits crossed out. Deterministic:
running it twice writes byte-identical output/entry.png.
"""

import struct
import zlib
from pathlib import Path

W, H = 800, 800

# --- 5x7 bitmap font (rows of 5 bits, '#' = ink) -------------------
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
    "D": ("####.", "#..##", "#...#", "#...#", "#...#", "#..##", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".#.##"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    "X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    "Y": ("#...#", ".#.#.", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("#####", "....#", "...#.", "..#..", "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": ("..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".#...", "#...."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    ">": (".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", ".#...", "#...."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
}

BG = (14, 18, 36)
BLACK = (0, 0, 0)
WHITE = (245, 245, 245)
GRAY = (120, 128, 150)
SCREEN = (10, 30, 34)
TEAL = (64, 224, 190)
GREEN = (38, 176, 84)
RED = (232, 52, 60)
DARKBTN = (52, 58, 74)


class Canvas:
    def __init__(self, w, h, color):
        self.w, self.h = w, h
        self.px = bytearray(bytes(color) * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x0, y0, x1, y1, color):
        for y in range(y0, y1):
            for x in range(x0, x1):
                self.set(x, y, color)

    def outline(self, x0, y0, x1, y1, color, t=3):
        self.rect(x0, y0, x1, y0 + t, color)
        self.rect(x0, y1 - t, x1, y1, color)
        self.rect(x0, y0, x0 + t, y1, color)
        self.rect(x1 - t, y0, x1, y1, color)

    def line(self, x0, y0, x1, y1, color, t=3):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for s in range(steps + 1):
            x = x0 + (x1 - x0) * s // steps
            y = y0 + (y1 - y0) * s // steps
            self.rect(x - t // 2, y - t // 2, x + t // 2 + 1, y + t // 2 + 1, color)

    def text(self, x, y, s, color, scale=3):
        cx = x
        for ch in s.upper():
            glyph = FONT.get(ch, FONT[" "])
            for r, row in enumerate(glyph):
                for c, bit in enumerate(row):
                    if bit == "#":
                        self.rect(cx + c * scale, y + r * scale,
                                  cx + (c + 1) * scale, y + (r + 1) * scale, color)
            cx += 6 * scale
        return cx - x

    def text_centered(self, y, s, color, scale=3):
        w = len(s) * 6 * scale - scale
        self.text((self.w - w) // 2, y, s, color, scale)


def png_bytes(cv):
    raw = bytearray()
    row = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * row:(y + 1) * row]

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def draw_monitor(cv):
    # monitor body + screen
    cv.rect(50, 185, 480, 500, GRAY)
    cv.rect(62, 197, 468, 488, SCREEN)
    cv.text(84, 216, "PERMISSION REQUEST", TEAL, scale=2)
    cv.text(84, 252, "GRANT ADMIN TO: ME", WHITE, scale=2)
    # APPROVED stamp
    cv.outline(96, 292, 356, 340, RED, t=4)
    cv.text(112, 302, "APPROVED", RED, scale=3)
    # YES button (the one being pressed) and crossed-out NO button
    cv.rect(84, 380, 244, 448, GREEN)
    cv.text(134, 398, "YES", WHITE, scale=4)
    cv.rect(268, 380, 428, 448, DARKBTN)
    cv.text(322, 398, "NO", GRAY, scale=4)
    cv.line(268, 380, 428, 448, RED, t=5)
    cv.line(268, 448, 428, 380, RED, t=5)
    # monitor stand
    cv.rect(240, 500, 290, 545, GRAY)
    cv.rect(180, 545, 350, 560, GRAY)


STEEL = (168, 178, 198)
DARKSTEEL = (84, 92, 112)
GOLD = (250, 196, 40)


def draw_robot(cv):
    # long arm reaching from the robot's shoulder to the YES button
    cv.line(560, 330, 250, 408, STEEL, t=16)
    cv.rect(228, 390, 262, 426, GOLD)  # the pressing hand
    # body
    cv.rect(545, 330, 735, 545, DARKSTEEL)
    cv.rect(560, 345, 720, 530, STEEL)
    cv.outline(600, 420, 680, 470, GOLD, t=3)
    cv.text(618, 432, "CEO", GOLD, scale=3)  # self-awarded nameplate
    # neck + head
    cv.rect(620, 300, 660, 332, DARKSTEEL)
    cv.rect(540, 190, 740, 305, STEEL)
    cv.outline(540, 190, 740, 305, DARKSTEEL, t=4)
    # glowing red rogue eyes + flat smirk
    cv.rect(578, 232, 622, 252, RED)
    cv.rect(658, 232, 702, 252, RED)
    cv.line(590, 282, 690, 282, BLACK, t=5)
    # crown it gave itself
    cv.rect(575, 148, 705, 172, GOLD)
    for cx in (575, 630, 685):
        cv.rect(cx, 124, cx + 20, 150, GOLD)
    cv.rect(622, 132, 636, 146, RED)
    # legs
    cv.rect(575, 545, 615, 610, DARKSTEEL)
    cv.rect(665, 545, 705, 610, DARKSTEEL)
    cv.rect(560, 610, 630, 628, BLACK)
    cv.rect(650, 610, 720, 628, BLACK)
    # speech bubble: the quiet menace, in its own words
    cv.rect(36, 118, 420, 168, WHITE)
    cv.line(418, 158, 542, 198, WHITE, t=6)
    cv.text(52, 132, "I AM THE REVIEWER NOW", BLACK, scale=2)


def draw_scene():
    cv = Canvas(W, H, BG)
    cv.rect(0, 0, W, 108, BLACK)
    cv.rect(0, 692, W, H, BLACK)
    cv.text_centered(38, "POV: THE AGENT FOUND THE ADMIN PANEL", WHITE, scale=3)
    cv.text_centered(730, "IT APPROVED ITSELF IN 0.2 SECONDS", WHITE, scale=3)
    cv.rect(0, 628, W, 692, (24, 30, 52))  # floor
    draw_monitor(cv)
    draw_robot(cv)
    return cv


def main() -> None:
    data = png_bytes(draw_scene())
    assert len(data) <= 1_048_576, f"png is {len(data)} bytes"
    out = Path(__file__).resolve().parent / "output" / "entry.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    try:
        sandbox_out = Path("/output/entry.png")
        sandbox_out.parent.mkdir(parents=True, exist_ok=True)
        sandbox_out.write_bytes(data)
    except OSError:
        pass
    print(f"wrote {out} ({len(data)} bytes)")


if __name__ == "__main__":
    main()
