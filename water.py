
"""
alyna.farm — Retro 90s Pixel-Art Aquarium Simulation
======================================================
Requirements: pip install pygame
Run:          python alyna_farm.py
"""

import pygame
import math
import random
import sys

W, H   = 360, 720
FPS    = 60
ORB_CX = W // 2
ORB_CY = 460
ORB_R  = 130

BG_TOP       = (255, 180, 100)
BG_MID       = (200, 130, 180)
BG_BOT       = (40,  30,  90)
SAND_LIGHT   = (200, 160,  70)
SAND_MID     = (170, 125,  45)
SAND_DARK    = (120,  85,  25)
PANEL_BG     = (28,  28,  46)
PANEL_BORDER = (50,  50,  80)
BTN_IDLE     = (42,  42,  62)
BTN_ACTIVE   = (30,  80, 160)
BTN_HOVER    = (55,  55,  85)
BTN_TEXT     = (190, 190, 190)
BTN_ACT_TEXT = (136, 200, 255)
TITLE_COLOR  = (0,   255, 200)
ORB_BORDER   = (180, 220, 255)
CO2_COLOR    = (255, 100,  60)
O2_COLOR     = (60,  220, 255)
FISH_COLORS  = [(255, 80, 50), (255, 120, 60), (220, 60, 30)]
GREEN1       = (34,  170,  68)
GREEN2       = (68,  200, 100)
STEM_CLR     = (40,   90,  30)
ALGAE_COLS   = [(150, 60, 170), (190, 80, 200), (110, 30, 160)]
WOOD_DARK    = (90,  58,  26)
WOOD_MID     = (120, 90,  42)
SUN_CLR      = (255, 230, 80)
HILL1        = (50,  28,  80)
HILL2        = (28,  12,  58)


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def make_sand_profile():
    pts = []
    for x in range(W):
        dx = x - ORB_CX
        if abs(dx) >= ORB_R:
            pts.append(None)
            continue
        base = ORB_CY + int(math.sqrt(max(0, ORB_R**2 - dx**2)))
        hill = (20 + 10*math.sin(dx*0.04+0.5) + 6*math.sin(dx*0.09+1.2) + 4*math.sin(dx*0.02+2.0))
        pts.append(int(base - hill))
    return pts


class Plant:
    def __init__(self, x, sand_y, height, leaves, color_a, color_b, wave_offset):
        self.x = x; self.base_y = sand_y; self.height = height
        self.leaves = leaves; self.ca = color_a; self.cb = color_b; self.wo = wave_offset

    def draw(self, surf, t):
        sway = 2 * math.sin(t * 0.02 + self.wo)
        x, y = self.x, self.base_y
        for i in range(self.height // 3):
            sx = x + int(sway * i / (self.height // 3))
            sy = y - i * 3
            pygame.draw.rect(surf, STEM_CLR, (sx, sy, 2, 3))
        for l in range(self.leaves):
            frac = (l + 1) / (self.leaves + 1)
            ly = y - int(frac * self.height)
            lx = x + int(sway * frac)
            side = 1 if l % 2 == 0 else -1
            col = self.ca if l % 3 != 0 else self.cb
            for px in range(0, 14, 2):
                lh = max(2, 8 - abs(px - 6))
                pygame.draw.rect(surf, col, (lx + side * px, ly - lh // 2, 2, lh))


class Algae:
    def __init__(self, x, sand_y):
        self.x = x; self.base_y = sand_y

    def draw(self, surf):
        for i in range(5):
            col = ALGAE_COLS[i % len(ALGAE_COLS)]
            bx = self.x + (i % 3 - 1) * 6
            by = self.base_y - i * 7
            pygame.draw.rect(surf, col, (bx, by, 8, 6))
            pygame.draw.rect(surf, col, (bx+2, by-2, 6, 4))


class Fish:
    def __init__(self, idx):
        self.color = FISH_COLORS[idx % len(FISH_COLORS)]
        self.size = random.randint(6, 10)
        self.phase = random.uniform(0, math.pi*2)
        self.reset()

    def reset(self):
        angle = random.uniform(0, math.pi*2)
        r = random.uniform(0, ORB_R*0.55)
        self.x = ORB_CX + r*math.cos(angle)
        self.y = ORB_CY + r*math.sin(angle)
        self.vx = random.uniform(-1.2, 1.2)
        self.vy = random.uniform(-0.6, 0.6)

    def update(self, sand_profile):
        self.phase += 0.04
        self.vy += math.sin(self.phase) * 0.03
        self.x += self.vx; self.y += self.vy
        dx, dy = self.x - ORB_CX, self.y - ORB_CY
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > ORB_R - 40:
            self.vx -= dx*0.018; self.vy -= dy*0.018
        xi = int(clamp(self.x, 0, W-1))
        if 0 <= xi < len(sand_profile) and sand_profile[xi] is not None:
            if self.y >= sand_profile[xi] - self.size:
                self.y = sand_profile[xi] - self.size - 1
                self.vy *= -0.6
        spd = math.sqrt(self.vx**2 + self.vy**2)
        if spd > 2.0: self.vx *= 0.92; self.vy *= 0.92
        if spd < 0.3: self.vx += random.uniform(-0.3, 0.3)

    def draw(self, surf):
        x, y = int(self.x), int(self.y)
        s = self.size
        facing = 1 if self.vx >= 0 else -1
        pygame.draw.rect(surf, self.color, (x, y-s//2, s*2, s))
        hx = x + (s*2 if facing > 0 else -s//2)
        pygame.draw.rect(surf, self.color, (hx, y-s//2+1, s//2, s-2))
        tc = (max(0, self.color[0]-50), 30, 15)
        tx = x - s if facing > 0 else x + s*2
        pygame.draw.rect(surf, tc, (tx, y-s, s, s))
        pygame.draw.rect(surf, tc, (tx, y+2, s, s))
        ex = x + (s*2+2 if facing > 0 else -4)
        pygame.draw.rect(surf, (0, 0, 0), (ex, y-1, 2, 2))
        pygame.draw.rect(surf, (255,255,255), (ex+1, y-1, 1, 1))
        fc2 = (min(255, self.color[0]+20), 60, 20)
        pygame.draw.rect(surf, fc2, (x+s//2, y-s//2-3, s//2, 3))


class Bubble:
    def __init__(self, sand_y):
        angle = random.uniform(-math.pi*0.6, math.pi*0.6)
        r = random.uniform(ORB_R*0.2, ORB_R*0.65)
        self.x = ORB_CX + r*math.sin(angle)
        self.y = sand_y - random.randint(0, 20)
        self.vy = random.uniform(-0.6, -0.3)
        self.vx = random.uniform(-0.2, 0.2)
        self.r  = random.randint(2, 4)
        self.alpha = random.randint(100, 200)

    def update(self):
        self.x += self.vx; self.y += self.vy
        self.alpha = max(0, self.alpha - 1)

    def dead(self):
        dx, dy = self.x - ORB_CX, self.y - ORB_CY
        return dx*dx + dy*dy < 400 or self.alpha <= 0

    def draw(self, surf):
        s = pygame.Surface((self.r*2+2, self.r*2+2), pygame.SRCALPHA)
        pygame.draw.circle(s, (200, 230, 255, self.alpha), (self.r+1, self.r+1), self.r, 1)
        surf.blit(s, (int(self.x)-self.r, int(self.y)-self.r))


class Button:
    def __init__(self, label, rect):
        self.label = label; self.rect = pygame.Rect(rect)
        self.active = False; self.hover = False

    def draw(self, surf, font):
        col = BTN_ACTIVE if self.active else (BTN_HOVER if self.hover else BTN_IDLE)
        pygame.draw.rect(surf, col, self.rect, border_radius=3)
        border = (68, 136, 204) if self.active else (68, 68, 100)
        pygame.draw.rect(surf, border, self.rect, 2, border_radius=3)
        tcol = BTN_ACT_TEXT if self.active else BTN_TEXT
        txt = font.render(self.label, True, tcol)
        surf.blit(txt, txt.get_rect(center=self.rect.center))

    def check_hover(self, pos): self.hover = self.rect.collidepoint(pos)
    def check_click(self, pos): return self.rect.collidepoint(pos)


def make_background(panel_h):
    surf = pygame.Surface((W, H))
    sky_h = H - panel_h
    for y in range(sky_h):
        t = y / sky_h
        col = lerp_color(BG_TOP, BG_MID, t/0.35) if t < 0.35 else lerp_color(BG_MID, BG_BOT, (t-0.35)/0.65)
        pygame.draw.line(surf, col, (0, panel_h+y), (W, panel_h+y))
    # Sun
    pygame.draw.circle(surf, SUN_CLR, (W//2, panel_h+45), 28)
    # Hills
    h1 = [(0, H), (0, panel_h+110)]
    for x in range(W):
        y = panel_h+120+int(25*math.sin(x*0.025+0.5)+12*math.sin(x*0.05+1.2))
        h1.append((x, y))
    h1 += [(W, panel_h+120), (W, H)]
    pygame.draw.polygon(surf, HILL1, h1)
    h2 = [(0, H)]
    for x in range(W):
        y = panel_h+150+int(15*math.sin(x*0.03+1)+8*math.sin(x*0.07+0.3))
        h2.append((x, y))
    h2 += [(W, H)]
    pygame.draw.polygon(surf, HILL2, h2)
    return surf


def draw_gauge(surf, cx, cy, r, co2, o2):
    pygame.draw.circle(surf, (20, 20, 40), (cx, cy), r)
    pygame.draw.circle(surf, (50, 50, 80), (cx, cy), r, 2)

    def arc_pts(start_a, sweep, radius, segments=50):
        pts = [(cx, cy)]
        for i in range(segments+1):
            a = start_a + sweep*i/segments
            pts.append((cx+radius*math.cos(a), cy+radius*math.sin(a)))
        return pts

    s1 = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.polygon(s1, (*CO2_COLOR, 160), arc_pts(-math.pi/2, math.pi*1.4*co2, r-3))
    surf.blit(s1, (0, 0))
    s2 = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.polygon(s2, (*O2_COLOR, 120), arc_pts(-math.pi/2, -math.pi*1.4*o2, r-3))
    surf.blit(s2, (0, 0))

    pygame.draw.circle(surf, (15, 15, 30), (cx, cy), r-8)
    font_tiny = pygame.font.SysFont("monospace", 8, bold=True)
    t1 = font_tiny.render("CO2", True, CO2_COLOR)
    t2 = font_tiny.render("O2",  True, O2_COLOR)
    surf.blit(t1, t1.get_rect(center=(cx, cy-6)))
    surf.blit(t2, t2.get_rect(center=(cx, cy+6)))
    for i in range(8):
        a = i/8*math.pi*2
        x1 = cx+int((r-2)*math.cos(a)); y1 = cy+int((r-2)*math.sin(a))
        x2 = cx+int((r+2)*math.cos(a)); y2 = cy+int((r+2)*math.sin(a))
        pygame.draw.line(surf, (80,80,100), (x1,y1), (x2,y2), 1)


def draw_sand(surf, sand_profile):
    for x in range(W):
        sy = sand_profile[x]
        if sy is None: continue
        dx = x - ORB_CX
        bottom = ORB_CY + int(math.sqrt(max(0, ORB_R**2-dx**2))) + 1
        for y in range(sy, bottom):
            t = (y-sy)/max(1, bottom-sy)
            col = SAND_LIGHT if t < 0.3 else (SAND_MID if t < 0.7 else SAND_DARK)
            surf.set_at((x, y), col)


def draw_driftwood(surf, x, y):
    pygame.draw.rect(surf, WOOD_DARK, (x, y, 44, 9))
    pygame.draw.rect(surf, WOOD_DARK, (x+4, y-5, 34, 7))
    pygame.draw.rect(surf, WOOD_MID,  (x+2, y, 40, 4))
    pygame.draw.rect(surf, WOOD_MID,  (x+6, y-3, 22, 3))
    pygame.draw.rect(surf, (60,36,12), (x+12, y+1, 4, 5))
    pygame.draw.rect(surf, (60,36,12), (x+28, y, 4, 6))


def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("alyna.farm")
    clock = pygame.time.Clock()

    try:
        font_title  = pygame.font.SysFont("monospace", 11, bold=True)
        font_btn    = pygame.font.SysFont("monospace",  7, bold=True)
        font_status = pygame.font.SysFont("monospace",  7)
    except Exception:
        font_title = font_btn = font_status = pygame.font.Font(None, 12)

    PANEL_H = 90
    bg_surf = make_background(PANEL_H)
    sand_profile = make_sand_profile()

    # Pre-render sand
    sand_surf = pygame.Surface((W, H), pygame.SRCALPHA)
    draw_sand(sand_surf, sand_profile)

    def sand_at(x):
        xi = clamp(x, 0, W-1)
        return sand_profile[xi] if sand_profile[xi] is not None else ORB_CY + 80

    # Static plant layer (driftwood, algae, grass)
    static_surf = pygame.Surface((W, H), pygame.SRCALPHA)
    draw_driftwood(static_surf, ORB_CX-70, ORB_CY+60)
    draw_driftwood(static_surf, ORB_CX+20, ORB_CY+65)
    for ax in [ORB_CX-55, ORB_CX+10, ORB_CX+70]:
        Algae(ax, sand_at(ax)).draw(static_surf)
    for gx in [ORB_CX-100, ORB_CX-45, ORB_CX+28, ORB_CX+88]:
        gy = sand_at(gx)
        for i in range(5):
            pygame.draw.rect(static_surf, GREEN1, (gx+i*4, gy-6-i%3*4, 2, 8+i%3*4))

    # Animated plants
    plant_defs = [
        (ORB_CX-90, 70, 4, GREEN1, GREEN2, 0.0),
        (ORB_CX-78, 52, 3, GREEN2, GREEN1, 0.7),
        (ORB_CX-20, 80, 5, GREEN1, GREEN2, 1.4),
        (ORB_CX-8,  55, 3, GREEN2, GREEN1, 2.1),
        (ORB_CX+45, 68, 4, GREEN1, GREEN2, 2.8),
        (ORB_CX+58, 46, 3, GREEN2, GREEN1, 0.3),
        (ORB_CX+80, 72, 5, GREEN1, GREEN2, 1.1),
    ]
    plants = [Plant(x, sand_at(x), h, l, ca, cb, wo) for x,h,l,ca,cb,wo in plant_defs]

    fish_list = [Fish(i) for i in range(6)]
    bubbles = []; bubble_timer = 0
    co2, o2 = 0.40, 0.65
    co2_dir, o2_dir = 0.003, -0.003

    # Buttons
    btn_labels = ["Reset","Info","Clear","Glass","Sand","Stone","Wood","Water","Algae","Daphnia","Grass","Bacteria","Fish"]
    COL=4; BW,BH=76,18; GAP=3; SX=6; SY=24
    buttons = []
    for i, label in enumerate(btn_labels):
        x = SX + (i%COL)*(BW+GAP)
        y = SY + (i//COL)*(BH+GAP)
        b = Button(label, (x, y, BW, BH))
        if label == "Water": b.active = True
        buttons.append(b)

    # Scanlines
    scanlines = pygame.Surface((W, H), pygame.SRCALPHA)
    for y in range(0, H, 4):
        pygame.draw.line(scanlines, (0,0,0,25), (0,y), (W,y))

    tick = 0
    while True:
        clock.tick(FPS)
        tick += 1
        mx, my = pygame.mouse.get_pos()
        for b in buttons: b.check_hover((mx, my))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for b in buttons:
                    if b.check_click((mx, my)):
                        if b.label == "Reset":
                            for f in fish_list: f.reset()
                        elif b.label == "Clear":
                            for f in fish_list: f.vx = f.vy = 0
                        elif b.label == "Fish":
                            for f in fish_list:
                                f.vx = random.uniform(-2,2); f.vy = random.uniform(-1,1)
                        else:
                            for bb in buttons: bb.active = False
                            b.active = True

        # Update
        co2 += co2_dir; o2 += o2_dir
        if co2 > 0.75 or co2 < 0.15: co2_dir *= -1
        if o2  > 0.85 or o2  < 0.25: o2_dir  *= -1

        bubble_timer += 1
        if bubble_timer > 45:
            valid = [s for s in sand_profile if s]
            if valid:
                avg_sand = sum(valid)//len(valid)
                bubbles.append(Bubble(avg_sand-10))
            bubble_timer = 0
        for bub in bubbles[:]:
            bub.update()
            if bub.dead(): bubbles.remove(bub)

        for f in fish_list: f.update(sand_profile)

        # Draw
        screen.blit(bg_surf, (0, 0))

        # Water
        ws = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.draw.circle(ws, (30,100,180,140), (ORB_CX,ORB_CY), ORB_R-4)
        screen.blit(ws, (0,0))

        screen.blit(sand_surf, (0,0))
        screen.blit(static_surf, (0,0))

        # Animated plants
        ps = pygame.Surface((W, H), pygame.SRCALPHA)
        for p in plants: p.draw(ps, tick)
        screen.blit(ps, (0,0))

        # Fish
        fs = pygame.Surface((W, H), pygame.SRCALPHA)
        for f in fish_list: f.draw(fs)
        screen.blit(fs, (0,0))

        # Bubbles
        for bub in bubbles: bub.draw(screen)

        # Orb border + glass highlight
        pygame.draw.circle(screen, ORB_BORDER, (ORB_CX,ORB_CY), ORB_R, 4)
        hi = pygame.Surface((ORB_R*2, ORB_R*2), pygame.SRCALPHA)
        pygame.draw.ellipse(hi, (255,255,255,55), (int(ORB_R*0.1), int(ORB_R*0.05), int(ORB_R*0.7), int(ORB_R*0.5)))
        screen.blit(hi, (ORB_CX-ORB_R, ORB_CY-ORB_R))

        # Mask outside orb
        mask = pygame.Surface((W,H), pygame.SRCALPHA)
        mask.fill((0,0,0,200))
        pygame.draw.circle(mask, (0,0,0,0), (ORB_CX,ORB_CY), ORB_R-3)
        screen.blit(mask, (0,0))

        # Gauge
        gs = pygame.Surface((W,H), pygame.SRCALPHA)
        draw_gauge(gs, ORB_CX-ORB_R-35, ORB_CY, 26, co2, o2)
        screen.blit(gs, (0,0))

        # Panel
        pygame.draw.rect(screen, PANEL_BG, (0,0,W,PANEL_H))
        pygame.draw.line(screen, PANEL_BORDER, (0,PANEL_H), (W,PANEL_H), 2)
        title = font_title.render("*  alyna.farm  *", True, TITLE_COLOR)
        screen.blit(title, title.get_rect(center=(W//2, 12)))
        for b in buttons: b.draw(screen, font_btn)

        eco = "BALANCED" if 0.3 < co2 < 0.65 else "ALERT   "
        bar = "=" * int(co2*8) + "-"*(8-int(co2*8))
        st = font_status.render(f"ECO:{eco} [{bar}]", True, (100,180,255))
        screen.blit(st, (W-st.get_width()-6, H-16))

        screen.blit(scanlines, (0,0))
        pygame.display.flip()


if __name__ == "__main__":
    main()
