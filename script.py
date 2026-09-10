#importowanie bibliotek potrzebnych do stworzenia skryptu
import math #potrzebna do obliczeń
import pygame #w tej robimy gui
from pygame.locals import * #to dodatek do gui
import obd #ta odpowiada za połączenie do aua

pygame.init()

# tu łączymy do auta
try:
    connection = obd.Async(fast=False)
    if not connection.is_connected():
        print("Warning: OBD adapter not found or not connected")
        connection = None
except Exception as e:
    print(f"Warning: Failed to initialize OBD connection - {e}")
    connection = None

#tworzenie zmiennej przechowującej nasz obraz (w trybie fullscreen)
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

#update naszych rozmiarów ekranu i skalowanie obiektów
def update_screen_size():
    global screen_w, screen_h, gauge_y, gauge1_x, gauge2_x, gauge3_x, label_y, container_bottom_y
    screen_w = screen.get_width()
    screen_h = screen.get_height()
    gauge_y = screen_h / 2
    gauge1_x = screen_w * 0.15
    gauge2_x = screen_w * 0.5
    gauge3_x = screen_w * 0.85
    label_y = screen_h * 0.15
    container_bottom_y = screen_h * 0.70

update_screen_size()

#ustawianie rodzajów czcionek w zależności od tego gdzie będziemy używać tekst
headerFont = pygame.font.SysFont("sportpulsedemo", 36) #jedna z czcionek link: https://befonts.com/sport-pulse-font.html
digitFont = pygame.font.SysFont("crossover", 60, bold=False) #druga z czcionek: https://befonts.com/crossover.charmap
unitFont = pygame.font.SysFont("crossover", 32)
tickFont = pygame.font.SysFont("crossover", 16)

white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (50, 220, 100)
yellow = (255, 200, 50)
orange = (255, 140, 0)

#zmienne i zakresy w których będziemy przechowywać nasze dane (tu zainicjalizowane do testów)
speed = 120
oil_temp = 120
throttle = 40

SPEED_MIN, SPEED_MAX = 0, 240
OIL_TEMP_MIN, OIL_TEMP_MAX = 0, 140
THROTTLE_MIN, THROTTLE_MAX = 0, 100

TEMP_GOOD = 90
TEMP_WARNING = 105
TEMP_DANGER = 115

def clamp(value, low, high):
    return max(low, min(high, value))

#tu funkcja zwracająca kolory do temperatury w zależności od tego jaka jest temperatura
def get_temp_color(temp):
    if temp < TEMP_GOOD:
        return green
    elif temp < TEMP_WARNING:
        return green
    elif temp < TEMP_DANGER:
        return yellow
    else:
        return red

#to samo co wyżej ale z kolorem słupka pedału gazu
def get_throttle_color(throttle_percent):
    if throttle_percent < 50:
        return green
    elif throttle_percent < 80:
        return orange
    else:
        return red

#tutaj funkcja zmieniająca prędkość na kąt prędkościomierza
def value_to_angle(value, min_val, max_val, start_angle, sweep_angle):
    normalized = 0 if max_val == min_val else (clamp(value, min_val, max_val) - min_val) / (max_val - min_val)
    return math.radians(start_angle + sweep_angle * normalized)

#funkcja rysująca prędkościomierz i wypisująca prędkość
def draw_speed_gauge(center_x, radius, value):
    # Dynamiczne skalowanie w zależności od rozmiaru okna
    radius = radius * 1.3
    inner_scale = 1.3
    offset_y = radius * 0.66
    major_tick_len = radius * 0.15
    minor_tick_len = radius * 0.1
    label_offset = radius * 0.28
    number_offset = radius * 0.28
    center_circle_r = radius * 0.45
    needle_length = radius * 0.95
    tick_major_width = int(radius * 0.02)
    tick_minor_width = int(radius * 0.01)
    needle_width = int(radius * 0.025)
    ring_thickness = int(radius * 0.01)

    #poniżej już rysowanie ale kodu nie ogarniam do końca (spytaj chatagpt, żeby powiedział co i jak tu jest, dość skomplikowany kod :/ )
    label_text = headerFont.render("PRĘDKOŚĆ", True, white)
    label_rect = label_text.get_rect(center=(center_x, label_y))
    screen.blit(label_text, label_rect)

    center_y = container_bottom_y - offset_y
    center = (center_x, center_y)
    inner_radius = radius
    start_angle_deg = 150
    sweep_deg = 240

    tick_values = [i for i in range(0, 241, 20)]
    for tick_value in tick_values:
        angle = value_to_angle(tick_value, SPEED_MIN, SPEED_MAX, start_angle_deg, sweep_deg)

        outer_x = center[0] + inner_radius * math.cos(angle)
        outer_y = center[1] + inner_radius * math.sin(angle)
        inner_x = center[0] + (inner_radius - major_tick_len) * math.cos(angle)
        inner_y = center[1] + (inner_radius - major_tick_len) * math.sin(angle)

        width = tick_major_width
        pygame.draw.line(screen, white, (outer_x, outer_y), (inner_x, inner_y), width)

        tick_label_text = tickFont.render(str(tick_value), True, white)
        lx = center[0] + (inner_radius - number_offset) * math.cos(angle) - tick_label_text.get_width() / 2
        ly = center[1] + (inner_radius - number_offset) * math.sin(angle) - tick_label_text.get_height() / 2
        screen.blit(tick_label_text, (lx, ly))

    for tick_value in range(0, 241, 10):
        if tick_value % 20 == 0:
            continue
        angle = value_to_angle(tick_value, SPEED_MIN, SPEED_MAX, start_angle_deg, sweep_deg)

        outer_x = center[0] + inner_radius * math.cos(angle)
        outer_y = center[1] + inner_radius * math.sin(angle)
        inner_x = center[0] + (inner_radius - minor_tick_len) * math.cos(angle)
        inner_y = center[1] + (inner_radius - minor_tick_len) * math.sin(angle)

        pygame.draw.line(screen, white, (outer_x, outer_y), (inner_x, inner_y), tick_minor_width)

    inner_display_radius = radius * 0.58
    ring_rect = pygame.Rect(center[0] - inner_display_radius, center[1] - inner_display_radius,
                             inner_display_radius * 2, inner_display_radius * 2)

    needle_angle = value_to_angle(value, SPEED_MIN, SPEED_MAX, start_angle_deg, sweep_deg)
    needle_end_x = center[0] + needle_length * math.cos(needle_angle)
    needle_end_y = center[1] + needle_length * math.sin(needle_angle)
    pygame.draw.line(screen, red, center, (needle_end_x, needle_end_y), needle_width)

    pygame.draw.circle(screen, black, (int(center[0]), int(center[1])), int(inner_display_radius))

    inner_span = 0.5 * sweep_deg
    inner_start = start_angle_deg + (sweep_deg - inner_span) / 2
    inner_end = inner_start + inner_span
    pygame.draw.arc(screen, white, ring_rect,
                    math.radians(inner_end), math.radians(inner_start), ring_thickness)

    value_text = digitFont.render(str(int(value)), True, white)
    value_rect = value_text.get_rect(center=(center[0], center[1] - radius * 0.05))
    screen.blit(value_text, value_rect)

#funkcja rysująca ten srodkowy wskaźnik (z temp oleju)
def draw_oil_container(center_x, temp):
    #dynamiczne skalowanie
    scale = screen_w * 0.0009
    body_width = screen_w * 0.22
    body_height = screen_h * 0.25
    border_thickness = int(screen_w * 0.009)
    step_w = body_width * 0.10
    step_h = body_height * 0.15
    neck_w = body_width * 0.12
    neck_h = body_height * 0.26
    cap_w = neck_w * 1.7
    cap_h = neck_h * 0.75

    #tu sie zaczyna rysowanie
    base_y = container_bottom_y - body_height * 0.2
    body_left = int(center_x - body_width / 2)
    body_top = int(base_y - body_height)

    #wypisanie tekstu Temperatura nad wskaźnikiem)
    label_text = headerFont.render("TEMPERATURA", True, white)
    screen.blit(label_text, label_text.get_rect(center=(center_x, label_y)))

    #wybieranie koloru + rysowanie na ekranie pojemnika
    liquid_color = get_temp_color(temp)
    body_rect = pygame.Rect(body_left, body_top, body_width, body_height)
    pygame.draw.rect(screen, liquid_color, body_rect)

    #tu chyba wypełnienie(?)
    mid_y = body_top + int(body_height * 0.55)
    pygame.draw.rect(screen, liquid_color, (body_left - step_w, mid_y - step_h, step_w, step_h))
    pygame.draw.rect(screen, liquid_color, (body_left - step_w, mid_y, step_w, step_h))

    #rysowanie szyjki pojemnika
    neck_x = body_left + body_width * 0.75
    neck_y = body_top - neck_h + border_thickness
    pygame.draw.rect(screen, liquid_color, (neck_x, neck_y, neck_w, neck_h))

    #rysowanie czapki szyjki pojemnika
    cap_x = neck_x - (cap_w - neck_w) / 2
    cap_y = neck_y - cap_h + border_thickness
    pygame.draw.rect(screen, liquid_color, (cap_x, cap_y, cap_w, cap_h))

    #tu obstawiam, że rysowanie czarnego wypełnienia pojemnika
    inner_rect = pygame.Rect(
        body_left + border_thickness,
        body_top + border_thickness,
        body_width - 2 * border_thickness,
        body_height - 2 * border_thickness,
    )
    pygame.draw.rect(screen, black, inner_rect)

    #tu wartości na ile ma wypełniać pojemnik
    liquid_percentage = clamp(temp, OIL_TEMP_MIN, OIL_TEMP_MAX) / OIL_TEMP_MAX
    liquid_height = int(inner_rect.height * liquid_percentage)
    liquid_top = inner_rect.bottom - liquid_height

    #ustawianie wypełnienia w zaelżnosci od wypełnienia
    if liquid_height > 0:
        pygame.draw.rect(screen, liquid_color, (inner_rect.left, liquid_top, inner_rect.width, liquid_height))

    temp_text = digitFont.render(str(int(temp)), True, white)
    screen.blit(temp_text, temp_text.get_rect(center=inner_rect.center))

#funkcja rysująca ten słupek po prawej z pedałem gazu
def draw_throttle_bar(center_x, throttle_percent):
    #skalowanie
    bar_width = screen_w * 0.20
    bar_height = screen_h * 0.38
    border = int(screen_w * 0.006)

    #wypisanie tytułu Pedał gazu i umieszczenie go na ekranie
    label_text = headerFont.render("PEDAŁ GAZU", True, white)
    screen.blit(label_text, label_text.get_rect(center=(center_x, label_y)))

    #obliczenie gdzie ma być umieszczony ten słupek i umieszczenie go na ekranie
    bar_x = int(center_x - bar_width/2)
    bar_y = int(container_bottom_y - bar_height - screen_h * 0.01)

    pygame.draw.rect(screen, white, (bar_x, bar_y, bar_width, bar_height), border)

    #tu chyba zmienne i instrukcje które mają za zadanie poruszać wypełnieniem tego słupka
    fill_percentage = clamp(throttle_percent, THROTTLE_MIN, THROTTLE_MAX) / THROTTLE_MAX
    fill_height = int((bar_height - border*2) * fill_percentage)
    fill_y = bar_y + bar_height - fill_height - border

    fill_color = get_throttle_color(throttle_percent)
    if fill_height > 0:
        pygame.draw.rect(screen, fill_color, (bar_x + border, fill_y, bar_width - border*2, fill_height))

    #tutaj wpisanie wartości pobranej z auta
    percent_text = digitFont.render(str(int(throttle_percent))+ "%", True,white)
    screen.blit(percent_text, percent_text.get_rect(center=(center_x, bar_y + bar_height/2)))

#funkcja wywołująca wszystkie 3 powyżej - odpowiada ze stworzenie huda
def draw_hud():
    screen.fill(black)
    draw_speed_gauge(gauge1_x, screen_w * 0.12, speed)
    draw_oil_container(gauge2_x, oil_temp)
    draw_throttle_bar(gauge3_x, throttle)

#wpisanie prędkości do zmiennej
def get_speed(s):
    global speed
    if not s.is_null():
        speed = int(s.value.magnitude)

#wpisanie wartości temperatury do zmiennej
def get_oil_temp(r):
    global oil_temp
    if not r.is_null():
        oil_temp = int(r.value.magnitude)

#wpisanie wartości pedału gazu do zmiennej
def get_throttle(l):
    global throttle
    if not l.is_null():
        throttle = int(l.value.magnitude)

if connection and connection.is_connected():
    try:
        connection.watch(obd.commands.SPEED, callback=get_speed) #pobranie wartości prędkości z auta
        connection.watch(obd.commands.COOLANT_TEMP, callback=get_oil_temp) #pobranie wartości temperatury z auta
        connection.watch(obd.commands.THROTTLE_POS, callback=get_throttle) #pobranie wartości pedału gazu (w zasadzie przepustnicy) z auta
        connection.start()
        print("OBD connection established - displaying live data")
    except Exception as e:
        print(f"Warning: OBD command setup issue - {e}")
        connection = None
else:
    print("No OBD connection available - using default values")

running = True
clock = pygame.time.Clock()


while running:
    for event in pygame.event.get():
        # tutaj to tam do testów żeby wyjść z ekranu escapem
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            if connection:
                try:
                    connection.stop()
                    connection.close()
                except:
                    pass
            running = False
        elif event.type == QUIT:
            if connection:
                try:
                    connection.stop()
                    connection.close()
                except:
                    pass
            running = False

    #wywołanie funkcji rysującej hud
    draw_hud()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
