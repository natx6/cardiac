#!/usr/bin/env python3
"""Generate the Cardiac app icon (blue rounded square + bold white C) with stdlib only.

The C matches the in-app marks: bold, white, on primary blue #0060a8.
Rendered with 2x supersampling so edges stay smooth at small sizes.
"""
import math
import struct
import zlib

SIZE = 1024
SS = 2  # supersample factor
BG = (0, 96, 168, 255)      # primary blue #0060a8
FG = (255, 255, 255, 255)

# C geometry (in final pixels, scaled by SS internally)
CX = CY = SIZE // 2
R_OUT, R_IN = 330, 175          # bold ring
GAP_HALF = math.radians(40)     # opening centered on the east side
TAN_GAP = math.tan(GAP_HALF)
RM = (R_OUT + R_IN) / 2         # tip circle radius
TIP_X = RM * math.cos(GAP_HALF)
TIP_Y = RM * math.sin(GAP_HALF)
CAP_R = (R_OUT - R_IN) / 2      # rounded gap ends
CORNER = 120                    # background corner radius (bolder than before)

S = SS
cx, cy = CX * S, CY * S
r_out, r_in = R_OUT * S, R_IN * S
tip_x, tip_y = TIP_X * S, TIP_Y * S
cap_r = CAP_R * S
corner = CORNER * S
W = SIZE * S


def in_round_rect(x, y):
    m = corner
    if m <= x < W - m or m <= y < W - m:
        return x < W and y < W
    cx_ = m if x < m else W - m
    cy_ = m if y < m else W - m
    return (x - cx_) ** 2 + (y - cy_) ** 2 <= m * m


def white_cov(px, py):
    """Fraction (0..1) of the SSxSS block covered by the C."""
    n = 0
    for oy in range(SS):
        y = py * SS + oy
        dy = y - cy
        for ox in range(SS):
            x = px * SS + ox
            dx = x - cx
            d2 = dx * dx + dy * dy
            if not (r_in * r_in < d2 < r_out * r_out):
                continue
            # gap wedge on the east side?
            in_gap = dx > 0 and abs(dy) < dx * TAN_GAP
            if in_gap:
                # rounded ends: disks around both wedge tips stay white
                dtx = abs(dx) - tip_x
                dty1 = abs(dy) - tip_y
                if dtx * dtx + dty1 * dty1 > cap_r * cap_r:
                    continue
            n += 1
    return n / (SS * SS)


rows = []
for py in range(SIZE):
    row = bytearray()
    for px in range(SIZE):
        # supersampled background coverage for smooth outer corners
        bg = sum(
            1
            for oy in range(SS)
            for ox in range(SS)
            if in_round_rect(px * SS + ox, py * SS + oy)
        ) / (SS * SS)
        if bg <= 0:
            row += bytes((0, 0, 0, 0))
            continue
        w = white_cov(px, py)
        r = round(FG[0] * w + BG[0] * (1 - w))
        g = round(FG[1] * w + BG[1] * (1 - w))
        b = round(FG[2] * w + BG[2] * (1 - w))
        row += bytes((r, g, b, round(255 * bg)))
    rows.append(bytes(row))


def chunk(tag, data):
    c = struct.pack(">I", len(data)) + tag + data
    return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


raw = b"".join(b"\x00" + r for r in rows)
png = (
    b"\x89PNG\r\n\x1a\n"
    + chunk(b"IHDR", struct.pack(">IIBBBBB", SIZE, SIZE, 8, 6, 0, 0, 0))
    + chunk(b"IDAT", zlib.compress(raw, 9))
    + chunk(b"IEND", b"")
)

import os
out = os.path.join(os.path.dirname(__file__), "..", "src-tauri", "icons")
os.makedirs(out, exist_ok=True)
with open(os.path.join(out, "icon.png"), "wb") as f:
    f.write(png)
print("wrote", os.path.join(out, "icon.png"), len(png), "bytes")
