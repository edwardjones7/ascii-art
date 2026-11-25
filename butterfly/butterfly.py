import math
import os
import sys
import time

print("art by @edjonesv", flush=True)
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import numpy as np
import pygame

W, H = 960, 760
FONT_SIZE = 10
FPS_RECORD = 30
DURATION = 10.0
MESSAGE = "become "
TYPED = "metamorphose()"
RAMP = ".:;=+*xo%#&@"
GLITCH = "01<>{}[]#$%&*+=?!ABXZ"
BG = (0, 0, 0)
SCALE = 265
CY = H * 0.50
CAM = 5.0
LIGHT = np.array([-0.5, 0.6, 0.75])
CRACK, HATCH, OPEN_END, FLY = 2.9, 3.3, 5.6, 7.7

RECORD = "--record" in sys.argv
OUT_DIR = "frames"
if RECORD:
    os.makedirs(OUT_DIR, exist_ok=True)

pygame.init()
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("butterfly.py")
font = pygame.font.SysFont("consolas,menlo,dejavusansmono,liberationmono,couriernew", FONT_SIZE, bold=True)
cw, ch = font.size("M")
COLS, ROWS = W // cw, H // ch

RAMP_ARR = np.array(list(RAMP))
LETTERS = np.array([c for c in MESSAGE if c != " "])
MSG_GRID = np.array([[MESSAGE[(r * COLS + c) % len(MESSAGE)] for c in range(COLS)]
                     for r in range(ROWS)])
rng = np.random.default_rng(11)
SETTLE = 0.12 + rng.random((ROWS, COLS)) * 0.5


def ss(a, b, x):
    k = np.clip((x - a) / (b - a), 0.0, 1.0)
    return k * k * (3 - 2 * k)


def smooth_curve(keys, x):
    xs, ys = np.array(keys, float).T
    i = np.clip(np.searchsorted(xs, x) - 1, 0, len(xs) - 2)
    m = np.gradient(ys, xs)
    h = xs[i + 1] - xs[i]
    s = (x - xs[i]) / h
    return ((2 * s**3 - 3 * s**2 + 1) * ys[i] + (s**3 - 2 * s**2 + s) * h * m[i]
            + (3 * s**2 - 2 * s**3) * ys[i + 1] + (s**3 - s**2) * h * m[i + 1])


FORE = [(-14, 0.82), (-4, 0.90), (10, 0.95), (24, 1.12), (36, 1.33),
        (43, 1.36), (50, 1.16), (58, 0.72), (66, 0.10)]
HIND = [(-88, 0.12), (-78, 0.62), (-66, 0.88), (-54, 0.97), (-42, 0.96),
        (-28, 0.90), (-12, 0.78), (4, 0.55), (14, 0.30)]
U, V = 84, 130
STOPS = np.array([[0.05, 0.05, 0.55], [0.04, 0.22, 1.00], [0.08, 0.52, 1.00], [0.45, 0.88, 1.00]])


def build_wing(keys, veins, spot_row):
    ang = np.linspace(keys[0][0], keys[-1][0], V)
    v = np.linspace(0, 1, V)[None, :]
    u = np.linspace(0, 1, U)[:, None]
    r = np.maximum(smooth_curve(keys, ang), 0.05)
    r = r * (1 + 0.022 * np.cos(v[0] * math.pi * 2 * veins))
    rad = u * r[None, :]
    a = np.radians(ang)[None, :]
    lat, fwd = rad * np.cos(a), rad * np.sin(a)
    cu = u * np.ones_like(v)
    s = np.clip(cu * 1.15, 0, 1) * (len(STOPS) - 1)
    i = np.minimum(s.astype(int), len(STOPS) - 2)
    f = (s - i)[..., None]
    col = STOPS[i] * (1 - f) + STOPS[i + 1] * f
    ao = 0.45 + 0.55 * cu ** 0.6
    edge = ss(0.80, 0.88, cu + 0.10 * ss(0.72, 1.0, v) + 0.015 * np.cos(v * math.pi * 2 * veins))
    cell = (v * veins) % 1
    phase = np.abs(cell - 0.5)
    gap = np.minimum(cell, 1 - cell)
    vein = ((gap * rad < 0.0035 * veins) & (cu > 0.22)).astype(float)
    dark = np.maximum(edge, vein * 0.72)
    col = col * (1 - dark[..., None]) + np.array([0.05, 0.10, 0.36]) * dark[..., None]
    ao = ao * (1 - 0.5 * dark)
    spot = (np.abs(cu - spot_row) < 0.026) & (phase < 0.20)
    col[spot] = [1.0, 0.97, 0.88]
    ao[spot] = 1.25
    return lat, fwd, cu, v * np.ones_like(cu), col, ao


WINGS = [build_wing(FORE, 8, 0.91), build_wing(HIND, 7, 0.91)]

BU, BV = 120, 60
by = np.linspace(-0.46, 0.36, BU)
br = np.interp(by, [-0.46, -0.40, -0.25, -0.08, -0.02, 0.10, 0.20, 0.235, 0.27, 0.32, 0.36],
               [0.005, 0.030, 0.050, 0.042, 0.050, 0.075, 0.058, 0.035, 0.052, 0.045, 0.005])
ba = np.linspace(0, 2 * math.pi, BV)
BODY = np.stack(np.broadcast_arrays(br[:, None] * np.cos(ba), by[:, None],
                                    br[:, None] * np.sin(ba)), -1)
BODY_COL = (np.array([0.75, 0.48, 0.16]) * (0.65 + 0.35 * np.sin(by * 80) ** 2)[:, None, None]
            * np.ones((BU, BV, 1)))

AN = 260
aq = np.linspace(0, 1, AN)
ANT = np.concatenate([np.stack([sd * (0.02 + 0.24 * aq ** 1.3), 0.33 + 0.42 * aq,
                                0.04 + 0.10 * aq - 0.07 * aq ** 3], -1) for sd in (-1, 1)])
ANT_COL = np.tile(np.array([1.0, 0.78, 0.35]) * (0.65 + 0.5 * (aq > 0.93))[:, None], (2, 1))

SU, SV = 150, 170
shy = np.linspace(-0.62, 0.62, SU)
shr = smooth_curve([(-0.62, 0.01), (-0.5, 0.11), (-0.25, 0.22), (0.05, 0.30), (0.25, 0.28),
                    (0.42, 0.17), (0.54, 0.06), (0.62, 0.015)], shy)
sha = np.linspace(-math.pi, math.pi, SV)
ridge = (1 + 0.07 * np.cos(sha * 6))[None, :] * (1 + 0.05 * np.sin(shy * 34) * (shy < 0.08))[:, None]
SHELL = np.stack(np.broadcast_arrays(shr[:, None] * ridge * np.sin(sha), shy[:, None],
                                     shr[:, None] * ridge * np.cos(sha)), -1).copy()
k01 = np.linspace(0, 1, SU)[:, None, None]
SHELL_COL = (np.array([0.06, 0.20, 0.75]) * (1 - k01) + np.array([0.30, 0.78, 1.0]) * k01) * np.ones((SU, SV, 1))
gold = (np.abs(shy - 0.27) < 0.02)[:, None] & (np.cos(sha * 12) > 0.1)[None, :]
SHELL_COL[gold] = [1.0, 0.75, 0.2]
zig = 0.16 * np.sign(np.sin(shy * 31)) * np.abs(np.sin(shy * 15.5))
SEAM = np.abs(sha[None, :] + zig[:, None]) / math.pi
SHELL_DELAY = (HATCH + 0.85 * SEAM + 0.25 * (0.62 - shy[:, None]) / 1.24).reshape(-1)
NS = SU * SV
S_JIT = rng.normal(size=(NS, 3)) * np.array([0.8, 0.8, 0.6])
S_PID = rng.integers(0, 10_000, NS)
S_OUT = SHELL.reshape(-1, 3) * np.array([1.0, 0.25, 1.0])

NB = 4 * U * V + BU * BV + 2 * AN
B_PID = rng.integers(0, 10_000, NB)
B_JIT = rng.normal(size=(NB, 3))


def normals(p):
    n = np.cross(np.gradient(p, axis=0), np.gradient(p, axis=1))
    return (n / (np.linalg.norm(n, axis=-1, keepdims=True) + 1e-9)).reshape(-1, 3)


SHELL_N = normals(SHELL)
SHELL_N = np.where(np.sum(SHELL_N * S_OUT, axis=1, keepdims=True) < 0, -SHELL_N, SHELL_N)


def flap_angle(t):
    a = 87 - 69 * ss(HATCH + 0.45, OPEN_END, t)
    a += 7 * math.sin(2 * math.pi * (t - OPEN_END) / 1.8) * ss(5.5, 6.2, t) * (1 - ss(FLY - 0.5, FLY - 0.2, t))
    beat = ss(FLY - 0.45, FLY, t)
    a += beat * (14 - 48 * math.cos(2 * math.pi * (t - FLY + 0.45) / 0.62))
    return math.radians(float(a))


def butterfly(t):
    grow = float(ss(HATCH + 0.1, OPEN_END - 0.2, t))
    size = 0.15 + 0.85 * grow
    crumple = (1 - grow) ** 1.4
    P, N, C, A = [], [], [], []
    for wi, (lat, fwd, cu, vv, col, ao) in enumerate(WINGS):
        f = flap_angle(t - 0.025 * wi)
        f_tip = flap_angle(t - 0.025 * wi - 0.09)
        ang = f + (f_tip - f) * cu ** 1.5
        x = lat * size
        wob = crumple * 0.10 * np.sin(vv * 21 + cu * 9) * cu
        bow = 0.10 * np.sin(cu * math.pi) * grow + 0.012 * np.cos(vv * 40) * cu + wob
        lift = 0.018 if wi == 0 else -0.018
        for sd in (-1, 1):
            px = sd * (0.045 + x * np.cos(ang) - bow * np.sin(ang))
            pz = 0.02 + lift + x * np.sin(ang) + bow * np.cos(ang)
            py = 0.08 - 0.06 * wi + fwd * size
            p = np.stack([px, py, pz], -1)
            P.append(p.reshape(-1, 3))
            N.append(normals(p))
            C.append(col.reshape(-1, 3))
            A.append(ao.reshape(-1))
    P += [BODY.reshape(-1, 3), ANT * (0.5 + 0.5 * grow) + np.array([0, 0.165 * (1 - grow), 0])]
    N += [normals(BODY), np.tile([0.0, 0.0, 1.0], (2 * AN, 1))]
    C += [BODY_COL.reshape(-1, 3), ANT_COL]
    A += [np.full(BU * BV, 0.9), np.full(2 * AN, 1.0)]
    return np.concatenate(P), np.concatenate(N), np.concatenate(C), np.concatenate(A)


def rot(yaw, pitch, roll):
    c, s = math.cos(yaw), math.sin(yaw)
    Ry = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    c, s = math.cos(pitch), math.sin(pitch)
    Rx = np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    c, s = math.cos(roll), math.sin(roll)
    Rz = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
    return Rz @ Rx @ Ry


LIGHT_N = LIGHT / np.linalg.norm(LIGHT)
VIEW = np.array([0.0, 0.0, 1.0])
HALF = (LIGHT_N + VIEW) / np.linalg.norm(LIGHT_N + VIEW)
WIND = np.array([0.9, 0.5, 0.35])


def scene(t):
    parts = []
    if 1.0 < t < HATCH + 3.0:
        s = float(ss(1.05, 2.5, t))
        shiver = 0.05 * math.sin(t * 46) * float(ss(2.5, HATCH, t)) * (1 - float(ss(HATCH, HATCH + 0.4, t)))
        R = rot(-0.9 + 0.95 * float(ss(1.0, HATCH + 0.2, t)), 0.08, shiver)
        tau = np.maximum(0.0, t - SHELL_DELAY)
        brk = np.maximum(0.0, tau - 0.12)
        pos = SHELL.reshape(-1, 3) * s + S_OUT * (tau * 1.5)[:, None]
        pos = pos @ R.T + WIND * (tau ** 2)[:, None] + S_JIT * (brk ** 1.4 * 0.45)[:, None]
        keep = (brk == 0) | (S_PID % 4 == 0)
        fade = np.clip(1 - tau / 1.0, 0, 1) * keep
        g = float(ss(CRACK - 0.3, HATCH + 0.1, t))
        glow = np.exp(-((SEAM.reshape(-1) / (0.02 + 0.13 * g)) ** 2)) * g
        col = SHELL_COL.reshape(-1, 3) * (1 - glow[:, None]) + np.array([0.85, 0.97, 1.0]) * glow[:, None]
        parts.append((pos, SHELL_N @ R.T, col, 0.9 + glow, fade, brk > 0, S_PID, glow))
    if HATCH < t < 9.45:
        p, n, c, a = butterfly(t)
        b = float(ss(OPEN_END, 6.3, t)) * (1 - float(ss(FLY - 0.4, FLY, t)))
        p = p * (1 + 0.015 * math.sin(2 * math.pi * (t - 6) / 2.4) * b)
        out = float(ss(HATCH, OPEN_END, t))
        fly = float(np.clip((t - FLY) / 1.25, 0, 1.6))
        yaw = 0.75 - 1.25 * float(ss(HATCH, 7.4, t)) + 0.45 * float(ss(7.3, 8.6, t))
        pitch = -0.08 - 0.42 * out + 0.62 * float(ss(FLY - 0.2, FLY + 1.0, t))
        R = rot(yaw, pitch, 0.10 * math.sin(t * 1.3) * out - 0.18 * float(ss(FLY, FLY + 0.8, t)))
        hover = 0.035 * math.sin(t * 2.4) * out
        pos = p @ R.T + np.array([0.05 * math.sin(fly * 4), hover - 0.12 * math.sin(min(fly, 1) * math.pi), 0])
        pos[:, 2] += 4.55 * fly ** 2.2
        tau = max(0.0, t - (FLY + 0.95))
        pos = pos + B_JIT * np.array([0.22, 0.22, 0.35]) * tau ** 1.2 * 1.5
        fade = np.full(NB, float(ss(HATCH, HATCH + 0.5, t)) * (1 - float(ss(8.95, 9.4, t))))
        fade *= (B_PID % 100) < 100 - 72 * float(ss(8.6, 9.1, t))
        flying = (B_PID % 1000) / 1000 < float(ss(FLY + 0.65, FLY + 1.05, t))
        parts.append((pos, n @ R.T, c, a, fade, flying, B_PID, np.zeros(NB)))
    return parts


def rasterize(t):
    parts = scene(t)
    if not parts:
        return None
    pos, nrm, col, ao, fade, flying, pid, glow = [np.concatenate(x) for x in zip(*parts)]
    depth = pos[:, 2]
    nd = nrm[:, 2]
    nrm = np.where((nd < 0)[:, None], -nrm, nrm)
    nd = np.abs(nd)
    diff = np.maximum(nrm @ LIGHT_N, 0)
    spec = np.maximum(nrm @ HALF, 0) ** 22
    lum = (0.25 + 0.95 * diff + 0.3 * (1 - nd) ** 2) * (0.25 + 0.75 * ao) + 0.6 * glow
    dof = 0.55 + 0.45 * np.clip((depth + 0.8) / 1.6, 0, 1)
    shift = (1 - nd)[:, None] ** 2 * np.array([0.22, -0.02, 0.10])
    sheen = (0.45 * spec * np.clip(ao, 0, 1))[:, None]
    rgb = ((col + shift * col[:, 2:3]) * lum[:, None] * 1.2 + sheen) * (dof * fade)[:, None]
    lumt = np.clip((lum * (0.35 + 0.65 * col.max(1)) + 0.45 * spec * ao) * dof * fade, 0, 1)

    near = depth < CAM - 0.12
    k = CAM / np.maximum(CAM - depth, 0.1)
    c = np.floor((W / 2 + pos[:, 0] * k * SCALE) / cw).astype(int)
    r = np.floor((CY - pos[:, 1] * k * SCALE) / ch).astype(int)
    ok = near & (c >= 0) & (c < COLS) & (r >= 0) & (r < ROWS) & (fade > 0)
    idx = np.nonzero(ok)[0]
    ids = r[idx] * COLS + c[idx]
    order = np.argsort(-depth[idx], kind="stable")
    uid, first = np.unique(ids[order], return_index=True)
    win = idx[order[first]]

    n = ROWS * COLS
    Lg, Cg, Dg = np.zeros(n), np.zeros((n, 3)), np.full(n, -3.0)
    Fg, Pg = np.zeros(n, bool), np.zeros(n, int)
    Lg[uid], Cg[uid], Dg[uid], Fg[uid], Pg[uid] = lumt[win], rgb[win], depth[win], flying[win], pid[win]
    sh = (ROWS, COLS)
    return Lg.reshape(sh), Cg.reshape(sh + (3,)), Dg.reshape(sh), Fg.reshape(sh), Pg.reshape(sh)


def edge_chars(filled, D):
    F = np.where(filled, D, -3.0)
    Fp = np.pad(F, 1, constant_values=-3.0)
    nbs = [Fp[1:-1, 2:], Fp[1:-1, :-2], Fp[2:, 1:-1], Fp[:-2, 1:-1]]
    jump = np.max([np.abs(F - nb) for nb in nbs], axis=0)
    edge = filled & (jump > 0.28) & ((jump > 1.8) | (F >= np.max(nbs, axis=0)))
    gx = (Fp[1:-1, 2:] - Fp[1:-1, :-2]) / cw
    gy = (Fp[2:, 1:-1] - Fp[:-2, 1:-1]) / ch
    a = np.degrees(np.arctan2(-gx, -gy)) % 180
    ech = np.select([(a < 22.5) | (a >= 157.5), a < 67.5, a < 112.5], ["-", "/", "|"], "\\")
    return edge, ech


def text_layer(t, gen):
    row = int(CY / ch)
    out = []
    blink = (t * 2.2) % 1 < 0.55
    c0 = COLS // 2 - len(TYPED) // 2
    if t < 0.3:
        if blink:
            out.append(("_", COLS // 2, row, (220, 230, 255)))
    elif t < 1.0:
        n = int((t - 0.3) / 0.6 * len(TYPED)) + 1
        for i, c in enumerate(TYPED[:n] + "_"):
            out.append((c, c0 + i, row, (220, 230, 255)))
    elif t < 1.4:
        f = 1 - (t - 1.0) / 0.4
        for i, c in enumerate(TYPED):
            if gen.random() < 0.6:
                c = GLITCH[gen.integers(len(GLITCH))]
            if gen.random() < f:
                v = int(255 * f)
                out.append((c, c0 + i, row, (int(v * 0.5), int(v * 0.8), v)))
    elif t > 9.4 and blink:
        out.append(("_", COLS // 2, row, (220, 230, 255)))
    return out


glyph_cache = {}


def glyph(c, rgb):
    key = (c, rgb)
    s = glyph_cache.get(key)
    if s is None:
        s = glyph_cache[key] = font.render(c, True, rgb)
    return s


def main():
    gen = np.random.default_rng(5)
    first_on = np.full((ROWS, COLS), np.inf)
    start = time.perf_counter()
    frame, last_t = 0, 0.0
    clock = pygame.time.Clock()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                pygame.quit()
                return
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                start = time.perf_counter()
        t = frame / FPS_RECORD if RECORD else (time.perf_counter() - start) % DURATION
        if t < last_t:
            first_on[:] = np.inf
        last_t = t

        screen.fill(BG)
        blits = []
        res = rasterize(t)
        if res is not None:
            Lg, Cg, Dg, Fg, Pg = res
            filled = Lg > 0.03
            edge, ech = edge_chars(filled, Dg)
            edge &= ~Fg
            chars = RAMP_ARR[np.clip((Lg * (len(RAMP) - 1)).astype(int), 0, len(RAMP) - 1)]
            chars = np.where(Lg > 0.80, MSG_GRID, chars)
            chars = np.where(edge, ech, chars)
            chars = np.where(Fg, LETTERS[Pg % len(LETTERS)], chars)
            colr = np.where(edge[..., None], Cg * 1.25 + np.array([0.06, 0.12, 0.22]), Cg)
            if t < OPEN_END:
                first_on[filled & np.isinf(first_on)] = t
                first_on[~filled] = np.inf
                glitching = filled & ~Fg & ((t - first_on) < SETTLE)
                colr = np.where(glitching[..., None], colr * 0.5 + 0.45, colr)
            else:
                glitching = np.zeros_like(filled)
            colr = (np.clip(colr, 0, 1) * 255 // 10 * 10).astype(int)
            for rr, cc in zip(*(a.tolist() for a in np.nonzero(filled))):
                c = GLITCH[gen.integers(len(GLITCH))] if glitching[rr, cc] else str(chars[rr, cc])
                rgb = tuple(colr[rr, cc].tolist())
                if c == " " or rgb == (0, 0, 0):
                    continue
                blits.append((glyph(c, rgb), (cc * cw, rr * ch)))
        for c, cc, rr, rgb in text_layer(t, gen):
            blits.append((glyph(c, rgb), (cc * cw, rr * ch)))
        screen.blits(blits, doreturn=False)

        for div in (5, 18):
            small = pygame.transform.smoothscale(screen, (W // div, H // div))
            screen.blit(pygame.transform.smoothscale(small, (W, H)), (0, 0),
                        special_flags=pygame.BLEND_ADD)
        pygame.display.flip()

        if RECORD:
            pygame.image.save(screen, f"{OUT_DIR}/f_{frame:04d}.png")
            if frame + 1 >= int(DURATION * FPS_RECORD):
                pygame.quit()
                return
        else:
            clock.tick(60)
        frame += 1


if __name__ == "__main__":
    main()
