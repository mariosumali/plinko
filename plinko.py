import sys, io, random
import numpy as np

import pygame

# Initialize Pygame
pygame.init()

score_sound = pygame.mixer.Sound('sounds/score.wav')
score_sound.set_volume(0.3)
click_sound = pygame.mixer.Sound('sounds/click.wav')
click_sound.set_volume(0.4)
error_sound = pygame.mixer.Sound('sounds/error.wav')
error_sound.set_volume(0.2)
ping_sound = pygame.mixer.Sound('sounds/ping.wav')
ping_sound.set_volume(0.1)

# Set up display
# Set up display
#width, height = 1280, 720
width, height = 1920, 1080
ratio = width / 1280
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Plinko Game")

# UI Layout Settings
sidebar_width = int(300 * ratio)
game_width = width - 2 * sidebar_width
left_sidebar_rect = pygame.Rect(0, 0, sidebar_width, height)
right_sidebar_rect = pygame.Rect(width - sidebar_width, 0, sidebar_width, height)
game_area_rect = pygame.Rect(sidebar_width, 0, game_width, height)

# Frame counter
frame_counter = 0

# Pin settings
pins = []
# Pin settings
pins = []
pin_rows = 16
pin_spacing = int(40 * ratio)
pin_radius = int(5 * ratio) # Smaller pins (was 9)
ball_radius = int(7 * ratio) # Slightly smaller ball (was 9)

pin_start = int(20 * ratio) # Adjusted slightly but keeping it static/original-ish or 0? 
# Original was 0 but with sidebar layout maybe 0 is too high? 
# The user said "original spacing... that went off screen". 
# I'll stick to fixed large spacing.
pin_start = int(0 * ratio)

bin_font = pygame.font.SysFont('Arial', int(14 * ratio), bold=True)

def create_pins():
    """Creates pins based on current settings."""
    pins.clear()
    offset = pin_spacing // 2
    # Recalculate center based on game area
    center_x = sidebar_width + game_width // 2
    
    for row in range(1, pin_rows + 1):
        row_offset = offset if row % 2 == 0 else 0
        for col in range(-(row// 2) - 1, (row - 1) // 2 + 2):
            x = center_x + col * pin_spacing + row_offset
            y = row * pin_spacing + pin_start
            pins.append((x, y))
create_pins()

# Define colors
def convert_color(rgb_color):
    return tuple([x / 255 for x in rgb_color])

# Theme Colors
background = (15, 33, 46) # Deep Navy/Charcoal
sidebar_bg = (33, 55, 67) # Slightly lighter for sidebars
accent_green = (0, 231, 1) # Bright Stake-like green
hover_green = (0, 255, 120)
dark_green_btn = (0, 180, 0)
green = accent_green
dark_green = (0, 100, 0)

red = (255, 68, 93) # Softer red
yellow = (255, 196, 0)
dark_red = (150, 40, 50)
dark_yellow = (155, 120, 0)
dark_yellow = (155, 120, 0)
# plt colors removed
white = (255, 255, 255)
gray = (128, 128, 128)
opaque_white = (255, 255, 255, 150)
black = (0, 0, 0)
green = (32, 250, 32)
button_color_states = (accent_green, hover_green, dark_green_btn)

def create_rgb_gradient(start_color, end_color, steps):
    """Generate a list of RGB colors forming a gradient between two given RGB colors."""
    # Calculate the difference per step
    step_red = (end_color[0] - start_color[0]) / (steps - 1)
    step_green = (end_color[1] - start_color[1]) / (steps - 1)
    step_blue = (end_color[2] - start_color[2]) / (steps - 1)

    # Generate the gradient list
    gradient = [
        (
            int(start_color[0] + step_red * i),
            int(start_color[1] + step_green * i),
            int(start_color[2] + step_blue * i)
        )
        for i in range(steps)
    ]
    return gradient

# Fonts for the headers
font = 'Gill Sans'
header0 = pygame.font.SysFont(font, int(24 * ratio), True)
header1 = pygame.font.SysFont(font, int(22 * ratio), True)
header2 = pygame.font.SysFont(font, int(14 * ratio), True)
header_money = pygame.font.SysFont(font, int(36 * ratio), True)

# Bin settings
rgb_gradient = create_rgb_gradient(red, yellow, (pin_rows+2) // 2)
rgb_gradient_rev = rgb_gradient[::-1]
rgb_gradient.extend(rgb_gradient_rev[1:])
dark_rgb_gradient = create_rgb_gradient(dark_red, dark_yellow, (pin_rows+2) // 2)
dark_rgb_gradient_rev = dark_rgb_gradient[::-1]
dark_rgb_gradient.extend(dark_rgb_gradient_rev[1:])
bin_texts = ['1000', '130', '26x', '9x', '4x', '2x', '0.2x', '0.2x', '0.2x','0.2x','0.2x','2x','4x','9x','26x', '130', '1000']
low_bin_texts = ['1', '1', '1', '9x', '5x', '2x', '1x', '0.5x', '0.2x', '0.5x', '1x', '2x', '5x', '9x', '1', '1', '1']
bin_width = pin_spacing * 0.8
recent_bins = [bin_texts[7],bin_texts[8],bin_texts[9],bin_texts[10]]
recent_bin_colors = [rgb_gradient[7],rgb_gradient[8],rgb_gradient[9],rgb_gradient[10]]

def create_bin_text_surfaces():
    global pin_rows
    """Pre-render all bin texts."""
    bin_text_surfaces = []
    texts = bin_texts
    if pin_rows < 10: texts = low_bin_texts
    for index, x in enumerate(texts):
        # Use bin_font instead of header1
        color = black # if index in hit_bins else black
        surface = bin_font.render(x, True, color)
        bin_text_surfaces.append(surface)
    return bin_text_surfaces

# Pre-render bin texts
hit_bins=[7,8,9,10]

def render_bins():
    global hit_bins
    bin_text_surfaces = create_bin_text_surfaces()
    click_offset = 4 * ratio
    # Center bins in game area
    center_x = sidebar_width + game_width // 2
    bin_start_offset = center_x - (pin_rows // 2 + 0.5) * pin_spacing
    base_y = pin_rows * pin_spacing + pin_start + pin_spacing // 2
    for bin in range(pin_rows + 1):
        animate = True if bin in hit_bins else False # if hit

        offset_x = bin * pin_spacing + (not pin_rows % 2) * pin_spacing // 2
        index = bin + 8 - pin_rows//2
        if pin_rows % 2 and bin <= pin_rows//2: index -= 1

        bin_text_surface = bin_text_surfaces[index]

        base_x = bin_start_offset - bin_width // 2 + offset_x

        if animate:
            # Configure Rects for drawing  
            light_rect_right = pygame.Rect(base_x, base_y + click_offset, bin_width, bin_width)
            text_rect = bin_text_surface.get_rect(center=(base_x + bin_width // 2, base_y + bin_width // 2 + click_offset))

            # Remove animated bin
            hit_bins = list(filter(lambda x: x != bin, hit_bins))
        else:
            # Configure Rects for drawing  
            dark_rect_right = pygame.Rect(base_x, base_y + click_offset, bin_width, bin_width)       
            light_rect_right = pygame.Rect(base_x, base_y, bin_width, bin_width)
            text_rect = bin_text_surface.get_rect(center=(base_x + bin_width // 2, base_y + bin_width // 2))

            # Draw dark rectangle
            draw_rounded_rect(screen, dark_rect_right, dark_rgb_gradient[index], int(4 * ratio) + (ratio > 1))            
        
        # Draw light rectangle and text
        draw_rounded_rect(screen, light_rect_right, rgb_gradient[index], int(4 * ratio) + (ratio > 1))
        screen.blit(bin_text_surface, text_rect)


    
    # Do not display LAST bins in this function anymore, or move it?
    # Keeping it but updating position? Actually let's remove this legacy display or move it to sidebar?
    # The reference image has stats on right, but maybe just latest catches at bottom or something?
    # For now, let's comment out or effectively disable this "floating" display as it conflicts with sidebars.
    pass

# Ball settings
ball_radius = int(pin_spacing / 4.4)
balls = []
hit_bins = []
del_balls_x = []
fall_speed_increment = 0.6 * ratio
# balls_at_once removed (forcing 1)

# Set Plot defaults
# Set Plot defaults
# Set Plot defaults
# Right Sidebar Graphs
plot_margin = 20 * ratio
plot_width = sidebar_width - 2 * plot_margin
plot_height = 200 * ratio
plot_gap = 30 * ratio

# P/L Graph (Middle Right)
# Adjusted to be lower
plot_rect_pl = pygame.Rect(
    right_sidebar_rect.x + plot_margin,
    right_sidebar_rect.y + 200 * ratio, 
    plot_width,
    plot_height
)

# Histogram (Bottom Right)
plot_rect_hist = pygame.Rect(
    right_sidebar_rect.x + plot_margin,
    plot_rect_pl.bottom + plot_gap,
    plot_width,
    plot_height
)

# Rounded rect gen
def draw_rounded_rect(surface, rect, color, corner_radius, corners=[True, True, True, True]):
    """ Draw a rectangle with selectable rounded or square corners on the given surface. """
    top_left, top_right, bottom_left, bottom_right = corners
    # Central rectangle, always drawn to avoid complexity in vertical and horizontal bars
    central_rect = pygame.Rect(rect.x + corner_radius, rect.y + corner_radius, rect.width - 2 * corner_radius, rect.height - 2 * corner_radius)
    pygame.draw.rect(surface, color, central_rect)

    # Horizontal and vertical bars
    horizontal_rect = pygame.Rect(rect.x + corner_radius, rect.y, rect.width - 2 * corner_radius, rect.height)
    vertical_rect = pygame.Rect(rect.x, rect.y + corner_radius, rect.width, rect.height - 2 * corner_radius)
    pygame.draw.rect(surface, color, horizontal_rect)
    pygame.draw.rect(surface, color, vertical_rect)

    # Helper function to draw a circle for the rounded corners
    def draw_corner_circle(center, radius, color):
        pygame.draw.circle(surface, color, center, radius)

    # Draw rounded corners if specified, otherwise fill in square corners
    if top_left: draw_corner_circle((rect.left + corner_radius, rect.top + corner_radius), corner_radius, color)
    else: pygame.draw.rect(surface, color, (rect.left, rect.top, corner_radius, corner_radius))

    if top_right:  draw_corner_circle((rect.right - corner_radius, rect.top + corner_radius), corner_radius, color)
    else: pygame.draw.rect(surface, color, (rect.right - corner_radius, rect.top, corner_radius, corner_radius))

    if bottom_left: draw_corner_circle((rect.left + corner_radius, rect.bottom - corner_radius), corner_radius, color)
    else: pygame.draw.rect(surface, color, (rect.left, rect.bottom - corner_radius, corner_radius, corner_radius))

    if bottom_right: draw_corner_circle((rect.right - corner_radius, rect.bottom - corner_radius), corner_radius, color)
    else: pygame.draw.rect(surface, color, (rect.right - corner_radius, rect.bottom - corner_radius, corner_radius, corner_radius))

# Histogram plot updater
# Histogram plot updater
def draw_native_histogram(surface, rect, data, bins_count):
    """Draws a histogram using Pygame primitives."""
    if not data:
        return

    counts = [0] * (bins_count + 1)
    for x in data:
        if 0 <= x < len(counts):
            counts[int(x)] += 1
    
    max_count = max(counts) if counts else 1
    if max_count == 0: max_count = 1
    
    bar_width = rect.width / len(counts)
    
    # Gradient for bars
    grad_colors = rgb_gradient[:]
    if len(grad_colors) < len(counts):
        # Extend or interpolate if needed, but for now we have enough colors usually
        pass
        
    # Correct mapping of bin index to color index based on row count (which is fixed at 16 now)
    # The original logic for plt_gradient_new was complex, simplifying for 16 rows
    # 16 rows -> 17 bins. center is 8.
    
    for i, count in enumerate(counts):
        if count == 0: continue
        bar_height = (count / max_count) * rect.height
        bar_rect = pygame.Rect(
            rect.x + i * bar_width,
            rect.bottom - bar_height,
            bar_width,
            bar_height
        )
        
        # Determine color
        # index mapping from render_bins:
        # index = bin + 8 - pin_rows//2
        # pin_rows=16 -> index = bin + 8 - 8 = bin.
        # So we can just use rgb_gradient[i] if valid
        color = rgb_gradient[i] if 0 <= i < len(rgb_gradient) else white
        
        pygame.draw.rect(surface, color, bar_rect)
    
    # Draw axes lines
    pygame.draw.line(surface, gray, rect.bottomleft, rect.bottomright, 2)
    pygame.draw.line(surface, gray, rect.bottomright, rect.topright, 2)

# Slider settings
# Sliders removed
sliders = {}
for key, slider in sliders.items():
    slider['rect'] = pygame.Rect(slider['pos'][0], slider['pos'][1], 210 * ratio, 10 * ratio)
    slider['handle'] = pygame.Rect(slider['pos'][0], slider['pos'][1] - 5 * ratio, 10 * ratio, 20 * ratio)

dragging_slider = None

def handle_sliders(event):
    # No sliders to handle
    pass

def reset_sliders():
    pass

# Button settings
# Button settings (Left Sidebar)
button_width = sidebar_width - 40 * ratio
button_height = 60 * ratio
button_x = left_sidebar_rect.x + (sidebar_width - button_width) // 2
button_y = 300 * ratio 

button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
# Shadow underneath
button_under_rect = pygame.Rect(button_x, button_y + 6, button_width, button_height)
button_clicked = False

def render_button(button_clicked):
    """Handle button states and actions."""
    mouse = pygame.mouse.get_pos()
    # Only change color on hover; clicking is handled via event loop
    button_text = header1.render("Bet", True, black)
    if button_clicked:
        draw_rounded_rect(screen, button_under_rect, button_color_states[1], 10)
        text_rect = button_text.get_rect(center=(button_rect.centerx, button_rect.centery + 6))
    else:
        text_rect = button_text.get_rect(center=button_rect.center)
        draw_rounded_rect(screen, button_under_rect, button_color_states[2], int(10 * ratio))
        if button_rect.collidepoint(mouse):
            draw_rounded_rect(screen, button_rect, button_color_states[1], int(10 * ratio))
        else:
            draw_rounded_rect(screen, button_rect, button_color_states[0], int(10 * ratio))
    screen.blit(button_text, text_rect)
    return button_rect.collidepoint(mouse)

# Render and keep track of money
START_MONEY = 5000.0
money = START_MONEY
bet = 50.0
# Stats
wins_count = 0
losses_count = 0
wagered = 0.0

pl = 0
pl_idx = 0
pl_x_data = [pl_idx]
pl_y_data = [pl]

input_label_y = button_y - 80 * ratio
input_box_height = 50 * ratio
input_box_width = button_width
input_box = pygame.Rect(button_x, input_label_y + 30 * ratio, input_box_width, input_box_height)
# Using a simpler dark rect for input
inner_input_box = input_box.inflate(-4, -4)
text = f'${float(bet):.2f}' 
text_active = False  # State of the input box
started_typing = False
print_error = False
err_surface = header2.render("INVALID", True, red)

def render_text_box():
    global input_box, text, text_active
    text_box_color = white if text_active else gray
    txt_surface = header1.render(text, True, white)
    # corners = [True, False, True, False]
    draw_rounded_rect(screen, input_box, text_box_color, 5 * ratio)
    pygame.draw.rect(screen, (20, 30, 40), inner_input_box, border_radius=int(5*ratio)) # Darker inner
    
    screen.blit(txt_surface, (inner_input_box.x + 10 * ratio, inner_input_box.centery - txt_surface.get_height()//2))
    
    label_surface = header1.render('Bet Amount', True, gray)
    screen.blit(label_surface, (button_x, input_label_y))
    

def handle_text_input(event):
    global text, text_active, started_typing, bet
    if event.type == pygame.MOUSEBUTTONDOWN:
        if input_box.collidepoint(event.pos):
            text_active = True
            text = '' # Clear on click for easier editing
            started_typing = True
        else:
            text_active = False
            # Reset text to current bet if empty or invalid
            try:
                if not text:
                    text = f"${bet:.2f}"
            except:
                text = f"${bet:.2f}"
            started_typing = False
            
    elif event.type == pygame.KEYDOWN:
        if text_active:
            if event.key == pygame.K_RETURN:
                try:
                    # Remove $ if present
                    val_str = text.replace('$', '')
                    new_bet = float(val_str)
                    if new_bet > 0:
                        bet = new_bet
                    text = f"${bet:.2f}"
                except ValueError:
                    text = f"${bet:.2f}"
                text_active = False
                started_typing = False
            elif event.key == pygame.K_BACKSPACE:
                text = text[:-1]
            else:
                if len(text) < 10: # limit length
                     # Allow digits and one dot
                    if event.unicode.isdigit() or event.unicode == '.':
                         text += event.unicode  # Add the character typed
                started_typing = False

money_input_box = None
money_active = False

def handle_money_input(event):
    global money, money_active, started_typing
    if event.type == pygame.MOUSEBUTTONDOWN:
        if money_input_box and money_input_box.collidepoint(event.pos):
            money_active = not money_active
        else:
            money_active = False
            
    elif event.type == pygame.KEYDOWN and money_active:
        current_money_str = f"{money:.2f}"
        if event.key == pygame.K_RETURN:
            money_active = False
        elif event.key == pygame.K_BACKSPACE:
            current_money_str = current_money_str[:-1]
            try:
                money = float(current_money_str) if current_money_str else 0.0
            except ValueError:
                pass
        else:
            if event.unicode.isdigit() or event.unicode == '.':
                current_money_str += event.unicode
                try:
                    money = float(current_money_str)
                except ValueError:
                    pass

def render_money(money):
    global money_input_box
    # Render Money Top Bar (Left Sidebar or Top Sidebar?)
    # Reference usually has wallet top right or similar.
    # Let's put Money Input/Display at top of Left Sidebar
    
    money_y = 50 * ratio
    money_rect = pygame.Rect(button_x, money_y, button_width, 50 * ratio)
    
    money_display_color = white if money_active else white
    
    # Label
    label = header2.render("Wallet", True, gray)
    screen.blit(label, (button_x, money_y - 25 * ratio))
    
    # Box
    draw_rounded_rect(screen, money_rect, (33, 55, 67), 5 * ratio) # slightly lighter
    
    # Text
    money_str = f"${money:.2f}"
    money_text = header1.render(money_str, True, money_display_color)
    screen.blit(money_text, (money_rect.x + 10 * ratio, money_rect.centery - money_text.get_height()//2))
    
    money_input_box = money_rect
    
    if money_active:
        pygame.draw.rect(screen, accent_green, money_input_box, 2, border_radius=int(5*ratio))

def render_stats_cards():
    # Right sidebar stats
    # 2 Cards: Profit, Wagered (Wins/Losses removed per request)
    
    card_width = sidebar_width - 2 * plot_margin
    card_height = 60 * ratio
    start_y = 50 * ratio
    gap = 15 * ratio
    
    # 0: Profit (Top)
    profit_rect = pygame.Rect(right_sidebar_rect.x + plot_margin, start_y, card_width, card_height)
    # 1: Wagered (Below)
    wagered_rect = pygame.Rect(right_sidebar_rect.x + plot_margin, profit_rect.bottom + gap, card_width, card_height)

    cards = [
        ("Profit", f"${pl:.2f}", profit_rect, green if pl >= 0 else red),
        ("Wagered", f"${wagered:.2f}", wagered_rect, white),
    ]
    
    for title, val, rect, val_color in cards:
        draw_rounded_rect(screen, rect, (20, 30, 40), 5 * ratio)
        title_surf = header2.render(title, True, gray)
        screen.blit(title_surf, (rect.x + 10, rect.y + 8))
        val_surf = header1.render(val, True, val_color)
        screen.blit(val_surf, (rect.x + 10, rect.centery))


def draw_native_pl_graph(surface, rect, x_data, y_data):
    """Draws P/L graph using Pygame."""
    if not x_data or not y_data:
        return

    # Background for graph
    # pygame.draw.rect(surface, (30, 30, 30), rect) # Optional darker bg

    max_val = max(abs(min(y_data)), abs(max(y_data)), 10) # At least 10 range
    
    # Actually user wants to see P/L over time.
    # Let's simple normalize to fit rect inside min/max of current data
    min_y = min(min(y_data), 0)
    max_y = max(max(y_data), 0)
    
    if min_y == max_y:
        min_y -= 10
        max_y += 10
    
    y_range = max_y - min_y
    x_range = len(x_data)
    if x_range < 2: x_range = 2
    
    points = []
    zero_y = rect.bottom - ((0 - min_y) / y_range) * rect.height
    
    # Construct points for line
    for i, val in enumerate(y_data):
        px = rect.x + (i / (x_range - 1)) * rect.width
        py = rect.bottom - ((val - min_y) / y_range) * rect.height
        points.append((px, py))
        
    if len(points) >= 2:
        # Draw fill
        # Split into polygons above and below zero line?
        # Simpler approach: Create a polygon from points down to zero line.
        # But color needs to change.
        # We can draw segments.
        
        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i+1]
            val1 = y_data[i]
            val2 = y_data[i+1]
            
            # Determine color
            # If both positive: Green
            # If both negative: Red
            # If crossing: split
            
            if val1 >= 0 and val2 >= 0:
                pygame.draw.polygon(surface, dark_green, [p1, p2, (p2[0], zero_y), (p1[0], zero_y)])
                pygame.draw.line(surface, green, p1, p2, 2)
            elif val1 <= 0 and val2 <= 0:
                pygame.draw.polygon(surface, dark_red, [p1, p2, (p2[0], zero_y), (p1[0], zero_y)])
                pygame.draw.line(surface, red, p1, p2, 2)
            else:
                # Crossing zero
                # Find intersection x where y=zero_y
                # Slope m = (y2 - y1) / (x2 - x1)
                # y - y1 = m(x - x1) -> zero_y - y1 = m(x_cross - x1)
                # x_cross = x1 + (zero_y - y1) / m
                
                if p2[0] != p1[0]:
                    m = (p2[1] - p1[1]) / (p2[0] - p1[0])
                    x_cross = p1[0] + (zero_y - p1[1]) / m
                    p_cross = (x_cross, zero_y)
                    
                    if val1 >= 0: # Positive to Negative
                        pygame.draw.polygon(surface, dark_green, [p1, p_cross, (p1[0], zero_y)])
                        pygame.draw.line(surface, green, p1, p_cross, 2)
                        pygame.draw.polygon(surface, dark_red, [p_cross, p2, (p2[0], zero_y)])
                        pygame.draw.line(surface, red, p_cross, p2, 2)
                    else: # Negative to Positive
                        pygame.draw.polygon(surface, dark_red, [p1, p_cross, (p1[0], zero_y)])
                        pygame.draw.line(surface, red, p1, p_cross, 2)
                        pygame.draw.polygon(surface, dark_green, [p_cross, p2, (p2[0], zero_y)])
                        pygame.draw.line(surface, green, p_cross, p2, 2)

    # Draw zero line
    pygame.draw.line(surface, gray, (rect.x, zero_y), (rect.right, zero_y), 1)
    
    # Draw border
    pygame.draw.line(surface, gray, rect.bottomleft, rect.topleft, 2)


# Complete board reset
def reset_board():
    global ball_radius, balls, hit_bins, del_balls_x, money, pl, pl_idx, pl_x_data, pl_y_data, bet, text, wins_count, losses_count, wagered
    pin_rows = 16
    money = START_MONEY
    bet = 50.0
    text = f'${bet:.2f}'
    pl = 0
    pl_idx = 0
    pl_x_data = [pl_idx]
    pl_y_data = [pl]
    wagered = 0
    wins_count = 0
    losses_count = 0
    
    create_pins()
    ball_radius = int(7 * ratio)
    balls.clear()
    hit_bins.clear()
    del_balls_x.clear()
    del_balls_x.clear()
    # Mock data for initial graphs? Or just empty
    # For now let's leave them empty or basic
    pl_y_data = [0]
    pl_x_data = [0]
    reset_sliders()

# Game loop
running = True
while running:
    # Fill the screen with the background color
    screen.fill(background)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if render_button(button_clicked) and not button_clicked:
                button_clicked = True
                
                if money - bet < 0: 
                    error_sound.play()
                else:
                    # Drop a ball 
                    # 1 ball logic only
                    center_x = sidebar_width + game_width // 2
                    start_x = random.randint(center_x - pin_spacing + pin_radius, center_x + pin_spacing - pin_radius)
                    balls.append([start_x, random.randint(-2*ball_radius,-ball_radius), 0, 0])  # [x_position, y_position, x_speed, y_speed]
                money -= bet
                wagered += bet
                click_sound.play()
    
        elif event.type == pygame.MOUSEBUTTONUP:
            button_clicked = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.key == pygame.K_SPACE:
                if money - bet < 0: 
                    error_sound.play()
                else:
                    # Drop a ball 
                    center_x = sidebar_width + game_width // 2
                    start_x = random.randint(center_x - pin_spacing + pin_radius, center_x + pin_spacing - pin_radius)
                    balls.append([start_x, random.randint(-2*ball_radius,-ball_radius), 0, 0])
                    money -= bet
                    wagered += bet
                    click_sound.play()
            elif event.key == pygame.K_r:
                reset_board()
        handle_sliders(event)
        handle_text_input(event)
        handle_money_input(event)

    frame_counter += 1

    # Draw Sidebars
    pygame.draw.rect(screen, sidebar_bg, left_sidebar_rect)
    pygame.draw.rect(screen, sidebar_bg, right_sidebar_rect)

    # Render catch bins and display recent hit bins
    render_bins()
    # display_last_bins(recent_bins, recent_bin_colors) # Removed from loop to avoid clutter


    # Update the position of each ball
    for ball in balls:
        ball[0] += ball[2]  # Update x position by x speed
        ball[1] += ball[3]  # Update y position by y speed
        ball[3] += fall_speed_increment  # Apply gravity to y speed

        # Check for collisions with pins
        for pin_x, pin_y in pins:
            dist_sq = (ball[0] - pin_x) ** 2 + (ball[1] - pin_y) ** 2
            radius_sum = ball_radius + pin_radius
            if dist_sq < radius_sum ** 2:
                # Animation
                pygame.draw.circle(screen, opaque_white, (int(pin_x), int(pin_y)), pin_radius*1.5)
                ping_sound.play()
                
                # Calulate ball trajectory
                overlap = radius_sum - np.sqrt(dist_sq)
                angle = np.arctan2(ball[1] - pin_y, ball[0] - pin_x)

                # Move the ball away from the pin a bit further than the overlap
                displacement = overlap + 0.5  # Extra 0.5 pixels to ensure it moves out of collision
                ball[0] += np.cos(angle) * displacement
                ball[1] += np.sin(angle) * displacement

                # Reflect the velocity and add randomness
                normal_vector = np.array([np.cos(angle), np.sin(angle)])
                velocity_vector = np.array([ball[2], ball[3]])
                reflected_velocity = velocity_vector - 2 * np.dot(velocity_vector, normal_vector) * normal_vector
                
                # Less damping to prevent sticking
                random_factor = 0.5  # Reverted to original 0.5 (was 0.7)

                # Apply randomness and dampening
                ball[2], ball[3] = reflected_velocity * random_factor
                ball[2] *= 0.5 # Reverted to original 0.5 (was 0.6)
                
                # Add minimum horizontal noise to prevent vertical stacking
                if abs(ball[2]) < 0.5:
                     ball[2] += random.choice([-1, 1]) * 1.5

                # After calculating the reflected velocity

                # Bias removed
                # Randomness reduced slightly
                # bias ball toward center - REMOVED

        # Remove the ball at the bottom
        if ball[1] > (pin_rows+0.5) * pin_spacing + pin_start:
            ball[1] = height - ball_radius
            center_x = sidebar_width + game_width // 2
            bin = int(((ball[0] - (center_x) + (not pin_rows%2) * pin_spacing//2) + (pin_spacing * ((pin_rows + 1) // 2))) // pin_spacing)
            del_balls_x.append(bin)
            hit_bins.append(bin)
            balls.remove(ball)
            pl_x_data.append(pl_idx)
            plot_update = True
            score_sound.play()
            if bin < len(bin_texts) and bin >= 0:
                index = bin + 8 - pin_rows//2
                if pin_rows % 2 and bin <= pin_rows//2: index -= 1
                texts = bin_texts
                if pin_rows < 10: texts = low_bin_texts
                recent_bins.append(texts[index])
                recent_bins = recent_bins[-4:]
                recent_bin_colors.append(rgb_gradient[index])
                recent_bin_colors = recent_bin_colors[-4:]
                return_money = bet * float(texts[index].replace('x',''))
                money += return_money
                if return_money > bet:
                    wins_count += 1
                else:
                    losses_count += 1
                
                pl_idx += 1
                pl = pl_y_data[-1] + return_money - bet
                pl_y_data.append(pl)

    # Draw pins
    for pin_x, pin_y in pins:
        pygame.draw.circle(screen, white, (int(pin_x), int(pin_y)), pin_radius)

    # Draw all the balls
    for ball in balls:
        pygame.draw.circle(screen, red, (int(ball[0]), int(ball[1])), ball_radius)


    # Sliders Removed
    # for key, slider in sliders.items():
    #     header_text = header0.render(f"{key.replace('_', ' ').title()}", True, white)
    #     header_rect = header_text.get_rect(topleft=(slider['pos'][0], slider['pos'][1] - 32 * ratio))
    #     screen.blit(header_text, header_rect)
    #     draw_rounded_rect(screen, slider['rect'], gray, 2 * ratio)
    #     slider['handle'].x = slider['pos'][0] + int((slider['value'] - sliders[key]['min']) / (sliders[key]['max'] - sliders[key]['min']) * 200 * ratio)
    #     draw_rounded_rect(screen, slider['handle'], white, 2 * ratio)

    # Render the button
    render_button(button_clicked)

    # Display Plot
    # Display Plot
    draw_native_histogram(screen, plot_rect_hist, del_balls_x, pin_rows + 1)
    draw_native_pl_graph(screen, plot_rect_pl, pl_x_data, pl_y_data)

    render_money(money)
    render_text_box()
    render_stats_cards()

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(60)