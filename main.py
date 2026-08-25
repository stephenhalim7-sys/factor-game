import pygame
import sys
import random
import os

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS 
else:
    base_path = os.path.dirname(__file__)

# Initialize Pygame
pygame.init()

# Display
display_info = pygame.display.Info()
SCREEN_WIDTH = display_info.current_w
SCREEN_HEIGHT = display_info.current_h
FPS = 60

# Colors
CREAM = (245, 222, 179)
DARK_BLUE = (91, 127, 166)
LIGHT_BLUE = (173, 216, 230)
SKY_BLUE = (135, 206, 235)
BLUE = (65, 105, 225)
DEEP_BLUE = (25, 25, 112)
RED = (220, 20, 60)
DEEP_RED = (139, 0, 0)
PINK = (255, 182, 193)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (144, 238, 144)
DARK_GREEN = (34, 139, 34)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
YELLOW = (255, 215, 0)
GOLD = (218, 165, 32)
ORANGE = (255, 140, 0)
PURPLE = (147, 112, 219)
CYAN = (0, 255, 255)

class Slider:
    def __init__(self, x, y, width, min_val, max_val, initial_val, label):
        self.rect = pygame.Rect(x, y, width, 10)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.label = label
        self.dragging = False
        self.handle_radius = 12
       
    def get_handle_pos(self):
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        x = self.rect.x + ratio * self.rect.width
        return (int(x), self.rect.centery)
   
    def handle_event(self, event, mouse_pos):
        handle_pos = self.get_handle_pos()
        handle_rect = pygame.Rect(handle_pos[0] - self.handle_radius,
                                   handle_pos[1] - self.handle_radius,
                                   self.handle_radius * 2,
                                   self.handle_radius * 2)
       
        if event.type == pygame.MOUSEBUTTONDOWN:
            if handle_rect.collidepoint(mouse_pos):
                self.dragging = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            x = max(self.rect.x, min(mouse_pos[0], self.rect.x + self.rect.width))
            ratio = (x - self.rect.x) / self.rect.width
            self.value = int(self.min_val + ratio * (self.max_val - self.min_val))
            return True
        return False
   
    def draw(self, screen, font_small, font_medium):
        # Label
        label_text = font_small.render(self.label, True, BLACK)
        screen.blit(label_text, (self.rect.x, self.rect.y - 30))
       
        # Track
        pygame.draw.rect(screen, GRAY, self.rect, border_radius=5)
        pygame.draw.rect(screen, DARK_BLUE, (self.rect.x, self.rect.y,
                                              (self.value - self.min_val) / (self.max_val - self.min_val) * self.rect.width,
                                              self.rect.height), border_radius=5)
       
        # Tick marks
        for i in range(self.min_val, self.max_val + 1):
            ratio = (i - self.min_val) / (self.max_val - self.min_val)
            x = self.rect.x + ratio * self.rect.width
            pygame.draw.line(screen, BLACK, (x, self.rect.y + 12), (x, self.rect.y + 20), 2)
            tick_text = font_small.render(str(i), True, BLACK)
            tick_rect = tick_text.get_rect(center=(x, self.rect.y + 30))
            screen.blit(tick_text, tick_rect)
       
        # Handle
        handle_pos = self.get_handle_pos()
        pygame.draw.circle(screen, DEEP_BLUE, handle_pos, self.handle_radius)
        pygame.draw.circle(screen, WHITE, handle_pos, self.handle_radius - 3)
       
        # Value display
        value_text = font_medium.render(str(self.value), True, DEEP_BLUE)
        value_rect = value_text.get_rect(center=(self.rect.x + self.rect.width + 50, self.rect.centery))
        screen.blit(value_text, value_rect)

class Button:
    def __init__(self, x, y, width, height, text, color, text_color=BLACK):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.original_color = color
        self.text_color = text_color
        self.hover = False
        self.enabled = True
        self.selected = False


    def draw(self, screen, font):
        color = self.color
        rect_to_draw = self.rect
        border_width = 1
        text_color = self.text_color
       
        if self.selected:
            expanded_rect = self.rect.inflate(12, 12)
            expanded_rect.center = self.rect.center
            rect_to_draw = expanded_rect
            border_width = 4
        elif self.hover and self.enabled:
            color = tuple(min(c + 30, 255) for c in self.color)
            border_width = 2

        pygame.draw.rect(screen, color, rect_to_draw, border_radius=5)
        pygame.draw.rect(screen, BLACK, rect_to_draw, border_width, border_radius=5)


        text_surf = font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=rect_to_draw.center)
        screen.blit(text_surf, text_rect)


    def is_clicked(self, pos):
        return self.enabled and self.rect.collidepoint(pos)


    def update_hover(self, pos):
        self.hover = self.enabled and self.rect.collidepoint(pos)

class FactorGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Factor Game - Permainan Faktor Seru!")
        self.clock = pygame.time.Clock()

        # Fonts
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 22)
        self.font_tiny = pygame.font.Font(None, 18)
        self.font_xlarge = pygame.font.Font(None, 60)

        # Load sounds
        self.click_sound = None
        sound_files = [os.path.join(base_path, 'assets', 'sounds', 'click_sound.mp3')]
        
        # Mixer
        try:
            pygame.mixer.quit()
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        except:
            pass
        
        for sound_file in sound_files:
            try:
                self.click_sound = pygame.mixer.Sound(sound_file)
                self.click_sound.set_volume(1.0)  # Volume maksimal
                print(f"✓ Sound loaded: {sound_file}")
                break
            except Exception as e:
                print(f"✗ Gagal load {sound_file}: {e}")
                continue
        
        if self.click_sound is None:
            print("⚠ Tidak ada sound file yang berhasil dimuat. Game akan berjalan tanpa sound.")

        # Load background music
        self.bg_music_loaded = False
        music_files = [os.path.join(base_path, 'assets', 'music', 'background_music.mp3')]
        
        for music_file in music_files:
            try:
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.set_volume(0.5)
                self.bg_music_loaded = True
                print(f"✓ Background music loaded: {music_file}")
                break
            except Exception as e:
                print(f"✗ Gagal load {music_file}: {e}")
                continue
        
        if self.bg_music_loaded:
            pygame.mixer.music.play(-1)
            print("♪ Background music playing...")
        else:
            print("⚠ Tidak ada background music yang berhasil dimuat.")
        
        # Sound settings
        self.sound_enabled = True
        self.music_enabled = True

        # Player names
        self.player1_name = "Pemain 1"
        self.player2_name = "Pemain 2"
       
        # Name editing
        self.editing_name = None
        self.temp_name = ""
        self.name_cursor_visible = True
        self.name_cursor_timer = 0

        # Game state
        self.screen_state = "home"  
        self.game_mode = None
       
        # Level settings
        self.row_slider = Slider(280, 220, 400, 4, 10, 10, "Rows:")
        self.col_slider = Slider(280, 340, 400, 4, 10, 10, "Columns:")
       
        self.reset_game()

    def reset_game(self):
        self.grid_size = max(self.row_slider.value, self.col_slider.value)
        self.max_number = self.row_slider.value * self.col_slider.value
       
        self.player_score = 0
        self.computer_score = 0
        self.player_last_move = 0
        self.computer_last_move = 0
        self.player_last_move_confirmed = 0
        self.computer_last_move_confirmed = 0
        self.player_factors = []
        self.computer_factors = []
        self.player_last_turn_factors = []
        self.computer_last_turn_factors = []
        self.available_numbers = set(range(1, self.max_number + 1))
        self.current_player = "player"
        self.game_over = False
       
        self.phase = "choose_number"
        self.last_chosen_number = None
        self.factor_selector = None
        self.required_factors = []
        self.selected_factors = []
        self.number_chosen_by = None

        self.new_game_button = Button(SCREEN_WIDTH - 160, 15, 130, 40, "New Game", DARK_GREEN, WHITE)
        self.confirm_button = Button(SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT - 55, 160, 50, "Confirm", DARK_GREEN, WHITE)
    
        # Sound control buttons
        self.music_button = Button(SCREEN_WIDTH - 300, 15, 55, 40, "BGM", PURPLE, WHITE)
        self.sound_button = Button(SCREEN_WIDTH - 235, 15, 55, 40, "SFX", ORANGE, WHITE)
       
        self.create_buttons()

        self.computer_thinking = False
        self.thinking_timer = 0
        self.message = ""
        self.message_color = BLACK
        self.message_timer = 0
       
        self.blink_timer = 0
        self.blink_visible = True

    def play_click_sound(self):
        """Memutar sound effect saat click"""
        if self.click_sound and self.sound_enabled:
            self.click_sound.play()
    
    def toggle_music(self):
        """Toggle background music on/off"""
        if self.bg_music_loaded:
            self.music_enabled = not self.music_enabled
            if self.music_enabled:
                pygame.mixer.music.unpause()
                print("♪ Music ON")
            else:
                pygame.mixer.music.pause()
                print("♪ Music OFF")
    
    def toggle_sound(self):
        """Toggle sound effects on/off"""
        self.sound_enabled = not self.sound_enabled
        status = "ON" if self.sound_enabled else "OFF"
        print(f"🔊 Sound effects {status}")

    def create_buttons(self):
        self.number_buttons = {}
       
        rows = self.row_slider.value
        cols = self.col_slider.value
       
        board_start_x = 340 
        board_width = SCREEN_WIDTH - board_start_x - 20
        board_height = SCREEN_HEIGHT - 160
        
        available_width = board_width - 40
        available_height = board_height - 100
        
        max_button_width = (available_width - (cols + 1) * 2) // cols
        max_button_height = (available_height - (rows + 1) * 2) // rows
        
        button_size = min(max_button_width, max_button_height, 60)
        spacing = 2
        
        total_width = (button_size + spacing) * cols - spacing
        total_height = (button_size + spacing) * rows - spacing
        
        start_x = board_start_x + (board_width - total_width) // 2
        start_y = 155 + (board_height - 100 - total_height) // 2

        for i in range(rows):
            for j in range(cols):
                num = i * cols + j + 1
                if num <= self.max_number:
                    x = start_x + j * (button_size + spacing)
                    y = start_y + i * (button_size + spacing)
                    btn = Button(x, y, button_size, button_size, str(num), WHITE, BLACK)
                    self.number_buttons[num] = btn

    def get_proper_factors(self, n):
        factors = []
        for i in range(1, int(n**0.5) + 1):
            if n % i == 0:
                factors.append(i)
                if i != n // i and n // i != n:
                    factors.append(n // i)
       
        if n in factors:
            factors.remove(n)
       
        if n > 1 and 1 not in factors:
             factors.insert(0, 1)

        return sorted(list(set(factors)))

    def choose_number(self, number):
        if number not in self.available_numbers or self.phase != "choose_number":
            return

        factors = self.get_proper_factors(number)
        self.required_factors = [f for f in factors if f in self.available_numbers]

        if len(self.required_factors) == 0:
            self.message = f"Angka {number} tidak punya faktor lagi! Giliran terskip."
            self.message_color = ORANGE
            self.message_timer = pygame.time.get_ticks()
            self.switch_player(skip_phase=True)
            return

        if self.current_player == "player":
            self.player_score += number
            self.player_last_move = number
            button_color = RED
        else:
            self.computer_score += number
            self.computer_last_move = number
            button_color = BLUE

        self.available_numbers.remove(number)
        self.number_buttons[number].color = button_color
        self.number_buttons[number].text_color = WHITE
        self.number_buttons[number].enabled = False

        self.last_chosen_number = number
        self.number_chosen_by = self.current_player

        self.phase = "select_factors"
        self.factor_selector = "computer" if self.current_player == "player" else "player"
        self.selected_factors = []
       
        if self.factor_selector == "player":
            self.message = f"{self.player1_name}: Pilih faktor dari {number}"
            self.message_color = RED
        elif self.game_mode == "two_player":
            self.message = f"{self.player2_name}: Pilih faktor dari {number}"
            self.message_color = BLUE
        else:
            self.message = f"Komputer memilih faktor dari {number}..."
            self.message_color = RED
            self.computer_thinking = True
            self.thinking_timer = pygame.time.get_ticks()

    def toggle_factor_selection(self, number):
        if self.phase != "select_factors":
            return
       
        if self.factor_selector == "player":
            current_selector = "player"
            selector_color = RED
        elif self.factor_selector == "computer" and self.game_mode == "two_player":
            current_selector = "computer"
            selector_color = BLUE
        else:
            return

        if number not in self.available_numbers:
            return

        if number in self.selected_factors:
            self.selected_factors.remove(number)
            self.number_buttons[number].selected = False
            self.number_buttons[number].color = WHITE
            self.number_buttons[number].text_color = BLACK
        else:
            self.selected_factors.append(number)
            self.number_buttons[number].selected = False
            self.number_buttons[number].color = selector_color
            self.number_buttons[number].text_color = WHITE

    def confirm_selection(self):
        if self.factor_selector == "player":
            selector = "player"
        elif self.factor_selector == "computer" and self.game_mode == "two_player":
            selector = "computer"
        else:
            return

        selected_set = set(self.selected_factors)
        required_set = set(self.required_factors)

        if len(selected_set) == 0:
            self.message = "Pilih minimal satu angka!"
            self.message_color = ORANGE
            self.message_timer = pygame.time.get_ticks()
            return

        invalid_selection = selected_set - required_set
        if invalid_selection:
            self.message = f"Ada pilihan yang salah! Tidak ada poin."
            self.message_color = RED
            self.message_timer = pygame.time.get_ticks()
            self.message_display_duration = 1000
           
            for factor in self.selected_factors:
                if factor in self.available_numbers:
                    self.number_buttons[factor].color = WHITE
                    self.number_buttons[factor].text_color = BLACK
            self.selected_factors = []
           
            self.pending_switch = True
            self.pending_switch_time = pygame.time.get_ticks() + self.message_display_duration
            return

        factor_points = sum(self.selected_factors)
       
        if selector == "player":
            self.player_score += factor_points
            self.message = f"{self.player1_name}: Benar! Anda dapat {factor_points} poin!"
            color = RED
            factor_list = self.player_factors
            self.player_last_turn_factors = self.selected_factors.copy()
        else:
            self.computer_score += factor_points
            self.message = f"{self.player2_name}: Benar! Anda dapat {factor_points} poin!"
            color = BLUE
            factor_list = self.computer_factors
            self.computer_last_turn_factors = self.selected_factors.copy()

        self.message_color = (0, 255, 128)
       
        for factor in self.selected_factors:
            factor_list.append(factor)
            self.available_numbers.remove(factor)
            self.number_buttons[factor].enabled = False

        self.message_timer = pygame.time.get_ticks()
        self.switch_player()

    def player_2_select_factors(self):
        factor_points = sum(self.required_factors)
        self.computer_score += factor_points
       
        if self.game_mode == "two_player":
            self.message = f" {self.player2_name} memilih faktor dengan benar dan dapat {factor_points} poin!"
        else:
            self.message = f" Komputer memilih faktor dengan benar dan dapat {factor_points} poin!"
           
        self.message_color = ORANGE
        self.message_timer = pygame.time.get_ticks()
       
        self.computer_last_turn_factors = self.required_factors.copy()
       
        for factor in self.required_factors:
            self.computer_factors.append(factor)
            self.available_numbers.remove(factor)
            self.number_buttons[factor].color = BLUE
            self.number_buttons[factor].text_color = WHITE
            self.number_buttons[factor].enabled = False
       
        self.computer_thinking = False
        self.switch_player()

    def switch_player(self, skip_phase=False):
        print(f"DEBUG: switch_player called with skip_phase={skip_phase}")
        print(f"DEBUG: Before - current_player = {self.current_player}, phase = {self.phase}")
        
        if not self.has_valid_moves():
            print(f"DEBUG: No valid moves, game over!")
            self.game_over = True
            return

        # Reset phase (parameter skip_phase diabaikan, selalu reset)
        self.phase = "choose_number"
        self.last_chosen_number = None
        self.required_factors = []
        self.selected_factors = []
        self.factor_selector = None
        self.number_chosen_by = None
       
        if self.current_player == "player":
            if self.player_last_move > 0:
                self.player_last_move_confirmed = self.player_last_move
        else:
            if self.computer_last_move > 0:
                self.computer_last_move_confirmed = self.computer_last_move
       
        self.current_player = "computer" if self.current_player == "player" else "player"
        
        print(f"DEBUG: After - current_player = {self.current_player}, phase = {self.phase}")
       
       # Set appropriate message and trigger computer thinking
        if self.current_player == "computer":
            if self.game_mode == "computer":
                print("DEBUG: Setting computer to think...")
                self.computer_thinking = True
                self.thinking_timer = pygame.time.get_ticks()

        elif self.game_mode == "two_player":
            # Jangan tampilkan pesan "Pilih sebuah angka" di sini,
            # karena nanti sudah otomatis muncul di fase berikutnya.
            pass

    def computer_choose_number(self):
        if not self.available_numbers or self.game_over:
            self.game_over = True
            return

        candidates = []
       
        for num in self.available_numbers:
            factors = self.get_proper_factors(num)
            available_factors = [f for f in factors if f in self.available_numbers]
           
            if available_factors:
                candidates.append(num)

        if not candidates:
            best_number = random.choice(list(self.available_numbers))
        else:
            best_number = random.choice(candidates)

        self.computer_thinking = False
        self.choose_number(best_number)

    def has_valid_moves(self):
        for num in self.available_numbers:
            factors = self.get_proper_factors(num)
            available_factors = [f for f in factors if f in self.available_numbers]
           
            if available_factors:
                return True
        return False
   
    def draw_header(self):
        pygame.draw.rect(self.screen, DEEP_BLUE, (0, 0, SCREEN_WIDTH, 75))
        pygame.draw.rect(self.screen, DARK_BLUE, (0, 0, SCREEN_WIDTH, 75), 3)

        text = self.font_xlarge.render("FACTOR GAME", True, GOLD)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 35))
        self.screen.blit(text, text_rect)

        # Update button states
        if not self.music_enabled:
            self.music_button.text = "BGM"
            self.music_button.color = GRAY
            self.music_button.text_color = BLACK
        else:
            self.music_button.text = "BGM"
            self.music_button.color = PURPLE
            self.music_button.text_color = WHITE
        
        if not self.sound_enabled:
            self.sound_button.text = "SFX"
            self.sound_button.color = GRAY
            self.sound_button.text_color = BLACK
        else:
            self.sound_button.text = "SFX"
            self.sound_button.color = ORANGE
            self.sound_button.text_color = WHITE

        # Draw buttons
        pygame.draw.rect(self.screen, BLACK, (self.music_button.rect.x + 1, self.music_button.rect.y + 1, 55, 40), border_radius=8)
        self.music_button.draw(self.screen, self.font_tiny)
    
        pygame.draw.rect(self.screen, BLACK, (self.sound_button.rect.x + 1, self.sound_button.rect.y + 1, 55, 40), border_radius=8)
        self.sound_button.draw(self.screen, self.font_tiny)
    
        pygame.draw.rect(self.screen, BLACK, (self.new_game_button.rect.x + 1, self.new_game_button.rect.y + 1, 130, 40), border_radius=8)
        self.new_game_button.draw(self.screen, self.font_small)

    def draw_name_with_edit(self, screen, name, x, y, color, is_editing, font):
        if is_editing:
            input_width = 180
            input_rect = pygame.Rect(x, y, input_width, 30)
            pygame.draw.rect(screen, WHITE, input_rect, border_radius=5)
            pygame.draw.rect(screen, color, input_rect, 2, border_radius=5)
           
            display_text = self.temp_name
            if self.name_cursor_visible:
                display_text += "|"
           
            text_surf = self.font_tiny.render(display_text, True, BLACK)
            text_rect = text_surf.get_rect(midleft=(x + 5, y + 15))
            screen.blit(text_surf, text_rect)
           
            count_text = self.font_tiny.render(f"{len(self.temp_name)}/20", True, GRAY)
            screen.blit(count_text, (x + input_width + 10, y + 7))
        else:
            text_surf = font.render(name, True, color)
            text_rect = text_surf.get_rect(midleft=(x, y + 15))
            screen.blit(text_surf, text_rect)
           
            edit_btn_rect = pygame.Rect(x + text_surf.get_width() + 10, y + 5, 25, 25)
            pygame.draw.rect(screen, LIGHT_GRAY, edit_btn_rect, border_radius=3)
            pygame.draw.rect(screen, color, edit_btn_rect, 1, border_radius=3)
            pencil = self.font_tiny.render("E", True, color)
            pencil_rect = pencil.get_rect(center=edit_btn_rect.center)
            screen.blit(pencil, pencil_rect)
           
            return edit_btn_rect

    def draw_left_panel(self):
        panel_height = SCREEN_HEIGHT - 90
        pygame.draw.rect(self.screen, BLACK, (12, 82, 318, panel_height + 2), border_radius=10)
        panel_rect = pygame.Rect(10, 80, 320, panel_height)
        pygame.draw.rect(self.screen, LIGHT_BLUE, panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, DEEP_BLUE, panel_rect, 3, border_radius=10)

        y_offset = 100

        player_header = pygame.Rect(20, y_offset, 300, 45)
        pygame.draw.rect(self.screen, DEEP_RED, player_header, border_radius=8)
        pygame.draw.rect(self.screen, RED, player_header, 3, border_radius=8)
       
        icon_text = self.font_small.render("[P1]", True, RED)
        self.screen.blit(icon_text, (28, y_offset + 15))
       
        self.player1_edit_btn = self.draw_name_with_edit(
            self.screen,
            self.player1_name if self.editing_name != "player1" else "",
            60,
            y_offset + 10,
            RED,
            self.editing_name == "player1",
            self.font_medium
        )

        y_offset += 55

        score_box = pygame.Rect(25, y_offset, 290, 50)
        pygame.draw.rect(self.screen, WHITE, score_box, border_radius=5)
        pygame.draw.rect(self.screen, RED, score_box, 2, border_radius=5)
        text = self.font_small.render("Skor:", True, BLACK)
        self.screen.blit(text, (35, y_offset + 5))
        text = self.font_xlarge.render(str(self.player_score), True, RED)
        text_rect = text.get_rect(center=(270, y_offset + 25))
        self.screen.blit(text, text_rect)

        y_offset += 65

        text = self.font_small.render("Pilihan Terakhir:", True, BLACK)
        self.screen.blit(text, (35, y_offset))
        move_box = pygame.Rect(25, y_offset + 20, 290, 35)
        pygame.draw.rect(self.screen, WHITE, move_box, border_radius=5)
        pygame.draw.rect(self.screen, RED, move_box, 2, border_radius=5)
        text = self.font_medium.render(str(self.player_last_move), True, RED)
        text_rect = text.get_rect(center=move_box.center)
        self.screen.blit(text, text_rect)

        y_offset += 70

        text = self.font_small.render("Faktor Dikuasai:", True, BLACK)
        self.screen.blit(text, (35, y_offset))
       
        if self.computer_last_move_confirmed > 0:
            all_factors = self.get_proper_factors(self.computer_last_move_confirmed)
        else:
            all_factors = []
       
        factors_box = pygame.Rect(25, y_offset + 20, 290, 45)
        pygame.draw.rect(self.screen, WHITE, factors_box, border_radius=5)
        pygame.draw.rect(self.screen, RED, factors_box, 2, border_radius=5)
       
        if all_factors:
            x_pos = 35
            y_pos = y_offset + 28
            for factor in all_factors:
                if factor in self.player_last_turn_factors:
                    color = RED
                elif factor in self.player_factors:
                    color = GRAY
                elif factor not in self.available_numbers:
                    color = GRAY
                else:
                    color = BLACK
               
                factor_text = self.font_tiny.render(str(factor), True, color)
                self.screen.blit(factor_text, (x_pos, y_pos))
                x_pos += factor_text.get_width() + 2
               
                if factor != all_factors[-1]:
                    comma = self.font_tiny.render(",", True, BLACK)
                    self.screen.blit(comma, (x_pos, y_pos))
                    x_pos += comma.get_width() + 3
               
                if x_pos > 300:
                    break
        else:
            text = self.font_tiny.render("-", True, BLACK)
            text_rect = text.get_rect(center=factors_box.center)
            self.screen.blit(text, text_rect)

        y_offset += 70

        opponent_name = self.player2_name if self.game_mode == "two_player" else "Komputer"
        computer_header = pygame.Rect(20, y_offset, 300, 45)
        pygame.draw.rect(self.screen, DEEP_BLUE, computer_header, border_radius=8)
        pygame.draw.rect(self.screen, BLUE, computer_header, 3, border_radius=8)
       
        if self.game_mode == "two_player":
            icon_text = self.font_small.render("[P2]", True, BLUE)
            self.screen.blit(icon_text, (28, y_offset + 15))
           
            self.player2_edit_btn = self.draw_name_with_edit(
                self.screen,
                opponent_name if self.editing_name != "player2" else "",
                60,
                y_offset + 10,
                BLUE,
                self.editing_name == "player2",
                self.font_medium
            )
        else:
            icon_text = self.font_small.render("[PC]", True, BLUE)
            self.screen.blit(icon_text, (28, y_offset + 15))
           
            text = self.font_medium.render(opponent_name, True, BLUE)
            text_rect = text.get_rect(midleft=(60, computer_header.centery))
            self.screen.blit(text, text_rect)
            self.player2_edit_btn = None

        y_offset += 55

        score_box = pygame.Rect(25, y_offset, 290, 50)
        pygame.draw.rect(self.screen, WHITE, score_box, border_radius=5)
        pygame.draw.rect(self.screen, BLUE, score_box, 2, border_radius=5)
        text = self.font_small.render("Skor:", True, BLACK)
        self.screen.blit(text, (35, y_offset + 5))
        text = self.font_xlarge.render(str(self.computer_score), True, BLUE)
        text_rect = text.get_rect(center=(270, y_offset + 25))
        self.screen.blit(text, text_rect)

        y_offset += 65

        text = self.font_small.render("Pilihan Terakhir:", True, BLACK)
        self.screen.blit(text, (35, y_offset))
        move_box = pygame.Rect(25, y_offset + 20, 290, 35)
        pygame.draw.rect(self.screen, WHITE, move_box, border_radius=5)
        pygame.draw.rect(self.screen, BLUE, move_box, 2, border_radius=5)
        text = self.font_medium.render(str(self.computer_last_move), True, BLUE)
        text_rect = text.get_rect(center=move_box.center)
        self.screen.blit(text, text_rect)

        y_offset += 70

        text = self.font_small.render("Faktor Dikuasai:", True, BLACK)
        self.screen.blit(text, (35, y_offset))
       
        if self.player_last_move_confirmed > 0:
            all_factors = self.get_proper_factors(self.player_last_move_confirmed)
        else:
            all_factors = []
       
        factors_box = pygame.Rect(25, y_offset + 20, 290, 45)
        pygame.draw.rect(self.screen, WHITE, factors_box, border_radius=5)
        pygame.draw.rect(self.screen, BLUE, factors_box, 2, border_radius=5)
       
        if all_factors:
            x_pos = 35
            y_pos = y_offset + 28
            for factor in all_factors:
                if factor in self.computer_last_turn_factors:
                    color = BLUE
                elif factor in self.computer_factors:
                    color = GRAY
                elif factor not in self.available_numbers:
                    color = GRAY
                else:
                    color = BLACK
               
                factor_text = self.font_tiny.render(str(factor), True, color)
                self.screen.blit(factor_text, (x_pos, y_pos))
                x_pos += factor_text.get_width() + 2
               
                if factor != all_factors[-1]:
                    comma = self.font_tiny.render(",", True, BLACK)
                    self.screen.blit(comma, (x_pos, y_pos))
                    x_pos += comma.get_width() + 3
               
                if x_pos > 300:
                    break
        else:
            text = self.font_tiny.render("-", True, BLACK)
            text_rect = text.get_rect(center=factors_box.center)
            self.screen.blit(text, text_rect)

    def draw_home_screen(self):
        """Halaman home/menu utama"""
        # Background gradient effect
        for i in range(SCREEN_HEIGHT):
            ratio = i / SCREEN_HEIGHT
            r = int(DEEP_BLUE[0] + (SKY_BLUE[0] - DEEP_BLUE[0]) * ratio)
            g = int(DEEP_BLUE[1] + (SKY_BLUE[1] - DEEP_BLUE[1]) * ratio)
            b = int(DEEP_BLUE[2] + (SKY_BLUE[2] - DEEP_BLUE[2]) * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, i), (SCREEN_WIDTH, i))
        
        # Main title with shadow
        title_y = 120
        shadow_text = self.font_xlarge.render("FACTOR GAME", True, BLACK)
        shadow_rect = shadow_text.get_rect(center=(SCREEN_WIDTH // 2 + 3, title_y + 3))
        self.screen.blit(shadow_text, shadow_rect)
        
        title_text = self.font_xlarge.render("FACTOR GAME", True, GOLD)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, title_y))
        self.screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle = self.font_medium.render("Permainan Faktor Matematika yang Seru!", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, title_y + 60))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Decorative elements
        pygame.draw.circle(self.screen, GOLD, (int(SCREEN_WIDTH * 0.15), int(SCREEN_HEIGHT * 0.15)), 30, 3)
        pygame.draw.circle(self.screen, GOLD, (int(SCREEN_WIDTH * 0.85), int(SCREEN_HEIGHT * 0.15)), 30, 3)
        pygame.draw.circle(self.screen, WHITE, (int(SCREEN_WIDTH * 0.1), int(SCREEN_HEIGHT * 0.75)), 20, 2)
        pygame.draw.circle(self.screen, WHITE, (int(SCREEN_WIDTH * 0.9), int(SCREEN_HEIGHT * 0.75)), 20, 2)

        # Menu buttons
        button_y = 280
        button_spacing = 80
        
        # Play button (main)
        play_btn = Button(SCREEN_WIDTH // 2 - 150, button_y, 300, 60, "MULAI PERMAINAN", DARK_GREEN, WHITE)
        
        # How to play button
        how_to_btn = Button(SCREEN_WIDTH // 2 - 150, button_y + button_spacing, 300, 60, "CARA BERMAIN", DARK_BLUE, WHITE)
        
        # Credits button
        credits_btn = Button(SCREEN_WIDTH // 2 - 150, button_y + button_spacing * 2, 300, 60, "TENTANG GAME", PURPLE, WHITE)
        
        # Exit button
        exit_btn = Button(SCREEN_WIDTH // 2 - 150, button_y + button_spacing * 3, 300, 60, "KELUAR", DEEP_RED, WHITE)
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw buttons with shadows
        for i, btn in enumerate([play_btn, how_to_btn, credits_btn, exit_btn]):
            btn.update_hover(mouse_pos)
            
            # Shadow
            shadow_rect = btn.rect.copy()
            shadow_rect.x += 4
            shadow_rect.y += 4
            pygame.draw.rect(self.screen, BLACK, shadow_rect, border_radius=10)
            
            # Button
            if i == 0:  # Play button bigger font
                btn.draw(self.screen, self.font_medium)
            else:
                btn.draw(self.screen, self.font_medium)
        
        # Footer text
        footer_y = SCREEN_HEIGHT - 50
        footer_text = self.font_tiny.render("© 2025 Factor Game | Belajar Matematika dengan Menyenangkan", True, WHITE)
        footer_rect = footer_text.get_rect(center=(SCREEN_WIDTH // 2, footer_y))
        self.screen.blit(footer_text, footer_rect)
        
        # Version info
        version_text = self.font_tiny.render("v1.0", True, WHITE)
        self.screen.blit(version_text, (SCREEN_WIDTH - 50, SCREEN_HEIGHT - 30))
        
        return play_btn, how_to_btn, credits_btn, exit_btn

    def draw_how_to_play(self):
        """Halaman cara bermain"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(230)
        overlay.fill(DEEP_BLUE)
        self.screen.blit(overlay, (0, 0))
        
        box_width = 700
        box_height = 550
        box_x = (SCREEN_WIDTH - box_width) // 2
        box_y = (SCREEN_HEIGHT - box_height) // 2
        
        # Main box
        pygame.draw.rect(self.screen, BLACK, (box_x + 4, box_y + 4, box_width, box_height), border_radius=20)
        pygame.draw.rect(self.screen, WHITE, (box_x, box_y, box_width, box_height), border_radius=20)
        pygame.draw.rect(self.screen, GOLD, (box_x, box_y, box_width, box_height), 4, border_radius=20)
        
        # Title
        title = self.font_xlarge.render("CARA BERMAIN", True, GOLD)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, box_y + 50))
        self.screen.blit(title, title_rect)
        
        # Instructions
        instructions = [
            "1. Pemain bergantian memilih angka dari papan",
            "2. Setelah pilih angka, lawan harus mengambil minimal satu faktor dari angka tersebut",
            "3. Faktor adalah angka yang dapat membagi habis angka yang dipilih",
            "   (kecuali angka itu sendiri)",
            "4. Pemain mendapat poin dari angka yang dipilih",
            "5. Lawan mendapat poin dari faktor-faktor",
            "6. Permainan berakhir saat tidak ada lagi angka yang memiliki faktor tersedia",
            "7. Pemain dengan skor tertinggi MENANG!"
        ]
        
        y_offset = box_y + 110
        for instruction in instructions:
            text = self.font_small.render(instruction, True, BLACK)
            self.screen.blit(text, (box_x + 50, y_offset))
            y_offset += 35
        
        # Example box
        example_y = y_offset + 10
        example_box = pygame.Rect(box_x + 50, example_y, box_width - 100, 60)
        pygame.draw.rect(self.screen, LIGHT_BLUE, example_box, border_radius=10)
        pygame.draw.rect(self.screen, DARK_BLUE, example_box, 2, border_radius=10)
        
        example_text1 = self.font_tiny.render("Contoh: Jika Anda pilih 12, faktornya: 1, 2, 3, 4, 6", True, BLACK)
        example_text2 = self.font_tiny.render("Anda dapat +12 poin, lawan dapat +(1+2+3+4+6) = +16 poin", True, BLACK)
        self.screen.blit(example_text1, (example_box.x + 20, example_box.y + 15))
        self.screen.blit(example_text2, (example_box.x + 20, example_box.y + 35))
        
        # Back button
        back_btn = Button(SCREEN_WIDTH // 2 - -85, box_y + box_height - 75, 200, 50, "KEMBALI", DARK_GREEN, WHITE)
        back_btn.update_hover(pygame.mouse.get_pos())
        
        pygame.draw.rect(self.screen, BLACK, (SCREEN_WIDTH // 2 - -87, box_y + box_height - 73, 200, 50), border_radius=10)
        back_btn.draw(self.screen, self.font_medium)
        
        return back_btn

    def draw_credits(self):
        """Halaman tentang game"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(230)
        overlay.fill(DEEP_BLUE)
        self.screen.blit(overlay, (0, 0))
        
        box_width = 600
        box_height = 450
        box_x = (SCREEN_WIDTH - box_width) // 2
        box_y = (SCREEN_HEIGHT - box_height) // 2
        
        # Main box
        pygame.draw.rect(self.screen, BLACK, (box_x + 4, box_y + 4, box_width, box_height), border_radius=20)
        pygame.draw.rect(self.screen, WHITE, (box_x, box_y, box_width, box_height), border_radius=20)
        pygame.draw.rect(self.screen, GOLD, (box_x, box_y, box_width, box_height), 4, border_radius=20)
        
        # Title
        title = self.font_xlarge.render("TENTANG GAME", True, GOLD)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, box_y + 50))
        self.screen.blit(title, title_rect)
        
        # Content
        content = [
            "",
            "FACTOR GAME",
            "Permainan Matematika Edukatif",
            "",
            "KECERDASAN BUATAN 2025",
            "",
            "Kelompok 1",
            "Haba L. Herlambang Banjarnahor (181231032)",
            "Stephen Lionel Halim (181231042)",
            "Alfian Anggara Putra Afandy (181231043)",
            "Abdul Hamid Amin (181231069)",
            "",
        ]
        
        y_offset = box_y + 110
        for line in content:
            if line == "FACTOR GAME":
                text = self.font_large.render(line, True, DEEP_BLUE)
            elif line in ["Permainan Matematika Edukatif", "Cocok untuk semua umur!"]:
                text = self.font_medium.render(line, True, RED)
            else:
                text = self.font_small.render(line, True, BLACK)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 25
        
        # Back button
        back_btn = Button(SCREEN_WIDTH // 2 - 100, box_y + box_height - 70, 200, 50, "KEMBALI", DARK_GREEN, WHITE)
        back_btn.update_hover(pygame.mouse.get_pos())
        
        pygame.draw.rect(self.screen, BLACK, (SCREEN_WIDTH // 2 - 98, box_y + box_height - 68, 200, 50), border_radius=10)
        back_btn.draw(self.screen, self.font_medium)
        
        return back_btn

    def draw_level_selection(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(DEEP_BLUE)
        self.screen.blit(overlay, (0, 0))

        box_width = min(750, SCREEN_WIDTH - 100)
        box_height = min(500, SCREEN_HEIGHT - 100)
        box_x = (SCREEN_WIDTH - box_width) // 2
        box_y = (SCREEN_HEIGHT - box_height) // 2
    
        pygame.draw.rect(self.screen, BLACK, (box_x + 3, box_y + 3, box_width, box_height), border_radius=20)
        pygame.draw.rect(self.screen, WHITE, (box_x, box_y, box_width, box_height), border_radius=20)
        pygame.draw.rect(self.screen, GOLD, (box_x, box_y, box_width, box_height), 4, border_radius=20)

        text = self.font_xlarge.render("[SETTING] Pilih Level", True, GOLD)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, box_y + 60))
        self.screen.blit(text, text_rect)

        desc_text = self.font_medium.render("Atur ukuran grid permainan", True, BLACK)
        desc_rect = desc_text.get_rect(center=(SCREEN_WIDTH // 2, box_y + 110))
        self.screen.blit(desc_text, desc_rect)

        slider_width = min(400, box_width - 200)
        slider_x = box_x + (box_width - slider_width) // 2
        
        self.row_slider.rect.x = slider_x
        self.row_slider.rect.y = box_y + 170
        self.row_slider.rect.width = slider_width
        
        self.col_slider.rect.x = slider_x
        self.col_slider.rect.y = box_y + 290
        self.col_slider.rect.width = slider_width
        
        # Draw sliders
        self.row_slider.draw(self.screen, self.font_small, self.font_medium)
        self.col_slider.draw(self.screen, self.font_small, self.font_medium)

        preview_text = f"Grid: {self.row_slider.value} x {self.col_slider.value} = {self.row_slider.value * self.col_slider.value} angka"
        text = self.font_large.render(preview_text, True, DEEP_BLUE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, box_y + 390))
        self.screen.blit(text, text_rect)

        start_btn = Button(SCREEN_WIDTH // 2 - 100, box_y + 430, 200, 50, "Lanjut >>", DARK_GREEN, WHITE)
        start_btn.update_hover(pygame.mouse.get_pos())
        pygame.draw.rect(self.screen, BLACK, (SCREEN_WIDTH // 2 - 99, box_y + 431, 200, 50), border_radius=8)
        start_btn.draw(self.screen, self.font_medium)

        return start_btn

    def draw_mode_selection(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(DEEP_BLUE)
        self.screen.blit(overlay, (0, 0))

        box_width = 450
        box_height = 350
        box_x = (SCREEN_WIDTH - box_width) // 2
        box_y = (SCREEN_HEIGHT - box_height) // 2
       
        pygame.draw.rect(self.screen, BLACK, (box_x + 3, box_y + 3, box_width, box_height), border_radius=20)
        pygame.draw.rect(self.screen, WHITE, (box_x, box_y, box_width, box_height), border_radius=20)
        pygame.draw.rect(self.screen, GOLD, (box_x, box_y, box_width, box_height), 4, border_radius=20)

        text = self.font_xlarge.render("[GAME] Pilih Mode", True, GOLD)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, box_y + 50))
        self.screen.blit(text, text_rect)

        desc_text = self.font_medium.render("Bermain vs Komputer atau Pemain Lain", True, BLACK)
        desc_rect = desc_text.get_rect(center=(SCREEN_WIDTH // 2, box_y + 90))
        self.screen.blit(desc_text, desc_rect)

        computer_btn = Button(box_x + 40, box_y + 130, 370, 70, "[PC] Lawan Komputer", DEEP_BLUE, WHITE)
        two_player_btn = Button(box_x + 40, box_y + 220, 370, 70, "[VS] 2 Pemain", DEEP_RED, WHITE)

        mouse_pos = pygame.mouse.get_pos()
        computer_btn.update_hover(mouse_pos)
        two_player_btn.update_hover(mouse_pos)
       
        computer_btn.draw(self.screen, self.font_medium)
        two_player_btn.draw(self.screen, self.font_medium)

        return computer_btn, two_player_btn

    def draw_game_board(self):
        board_start_x = 340
        board_width = SCREEN_WIDTH - board_start_x - 20
        board_height = SCREEN_HEIGHT - 160
        
        pygame.draw.rect(self.screen, BLACK, (board_start_x + 2, 102, board_width, board_height), border_radius=10)
        board_rect = pygame.Rect(board_start_x, 100, board_width, board_height)
        pygame.draw.rect(self.screen, (245, 245, 245), board_rect, border_radius=10)
        pygame.draw.rect(self.screen, DARK_BLUE, board_rect, 3, border_radius=10)

        is_message_active = self.message and pygame.time.get_ticks() - self.message_timer < 3000

        if self.game_over:
            if self.player_score > self.computer_score:
                msg = f"{self.player1_name} Menang!"
                color = RED
            elif self.computer_score > self.player_score:
                opponent = self.player2_name if self.game_mode == "two_player" else "Komputer"
                msg = f"{opponent} Menang!"
                color = BLUE
            else:
                msg = "Seri!"
                color = GOLD
           
            text = self.font_large.render(msg, True, color)
            message_center_x = 340 + (SCREEN_WIDTH - 340 - 20) // 2
            text_rect = text.get_rect(center=(message_center_x, 120))
            msg_bg = pygame.Rect(text_rect.x - 20, text_rect.y - 10, text_rect.width + 40, text_rect.height + 20)
            pygame.draw.rect(self.screen, WHITE, msg_bg, border_radius=8)
            pygame.draw.rect(self.screen, color, msg_bg, 3, border_radius=8)
            self.screen.blit(text, text_rect)
           
        elif self.phase == "select_factors":
            is_player_1_selecting = self.factor_selector == "player" and self.current_player == "computer"
            is_player_2_selecting = self.factor_selector == "computer" and self.current_player == "player" and self.game_mode == "two_player"

            if is_player_1_selecting or is_player_2_selecting:
                message_to_show = self.message
                color_to_use = self.message_color
               
                words = message_to_show.split()
                lines = []
                current_line = []
                for word in words:
                    current_line.append(word)
                    test_line = " ".join(current_line)
                    test_surf = self.font_small.render(test_line, True, BLACK)
                    if test_surf.get_width() > 580:
                        current_line.pop()
                        lines.append(" ".join(current_line))
                        current_line = [word]
                if current_line:
                    lines.append(" ".join(current_line))
               
                y = 115
                for line in lines[:2]:
                    text = self.font_small.render(line, True, color_to_use)
                    text_rect = text.get_rect(center=(board_start_x + board_width // 2, 115))
                    self.screen.blit(text, text_rect)
                    y += 22
            else:
                 opponent = self.player2_name if self.game_mode == "two_player" else "Komputer"
                 text = self.font_medium.render(f"{opponent} memilih faktor...", True, ORANGE)
                 text_rect = text.get_rect(center=(board_start_x + board_width // 2, 115))
                 self.screen.blit(text, text_rect)
                 
        elif is_message_active:
            words = self.message.split()
            lines = []
            current_line = []
            for word in words:
                current_line.append(word)
                test_line = " ".join(current_line)
                test_surf = self.font_small.render(test_line, True, BLACK)
                if test_surf.get_width() > 580:
                    current_line.pop()
                    lines.append(" ".join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(" ".join(current_line))
           
            y = 115
            for line in lines[:2]:
                text = self.font_small.render(line, True, self.message_color)
                text_rect = text.get_rect(center=(board_start_x + board_width // 2, 115))
                self.screen.blit(text, text_rect)
                y += 22
       
        elif self.phase == "choose_number":
            if self.current_player == "player":
                text = self.font_medium.render(f"{self.player1_name}: Pilih sebuah angka", True, RED)
            else:
                opponent = self.player2_name if self.game_mode == "two_player" else "Komputer"
                if self.game_mode == "two_player":
                    text = self.font_medium.render(f"{opponent}: Pilih sebuah angka", True, BLUE)
                else:
                    text = self.font_medium.render(f"{opponent} sedang berpikir...", True, ORANGE)
                   
            text_rect = text.get_rect(center=(board_start_x + board_width // 2, 115))
            self.screen.blit(text, text_rect)

        mouse_pos = pygame.mouse.get_pos()
       
        # Gambar tombol dengan efek berkedip untuk angka yang sedang dipilih faktornya
        for num, button in self.number_buttons.items():
            button.update_hover(mouse_pos)
           
            # Cek apakah ini angka yang sedang dipilih faktornya
            if self.phase == "select_factors" and num == self.last_chosen_number:
                # Simpan warna asli
                original_color = button.color
                original_text_color = button.text_color
               
                # Jika berkedip tidak visible, ubah ke warna putih
                if not self.blink_visible:
                    button.color = WHITE
                    button.text_color = BLACK
               
                button.draw(self.screen, self.font_small)
               
                # Kembalikan warna asli
                button.color = original_color
                button.text_color = original_text_color
            else:
                button.draw(self.screen, self.font_small)

        is_p1_selecting_factor = self.phase == "select_factors" and self.factor_selector == "player"
        is_p2_selecting_factor = self.phase == "select_factors" and self.factor_selector == "computer" and self.game_mode == "two_player"

        if is_p1_selecting_factor or is_p2_selecting_factor:
            self.confirm_button.update_hover(mouse_pos)
            self.confirm_button.draw(self.screen, self.font_medium)

    def draw_game_over_message(self):
        if not self.game_over:
            return

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(220)
        overlay.fill(DEEP_BLUE)
        self.screen.blit(overlay, (0, 0))

        box_width = 550
        box_height = 380
        box_x = (SCREEN_WIDTH - box_width) // 2
        box_y = (SCREEN_HEIGHT - box_height) // 2
       
        # Shadow
        pygame.draw.rect(self.screen, BLACK, (box_x + 5, box_y + 5, box_width, box_height), border_radius=20)
        # Main box
        pygame.draw.rect(self.screen, WHITE, (box_x, box_y, box_width, box_height), border_radius=20)
        pygame.draw.rect(self.screen, GOLD, (box_x, box_y, box_width, box_height), 5, border_radius=20)

        # Determine winner
        if self.player_score > self.computer_score:
            title = f"[WIN] {self.player1_name} Menang!"
            color = RED
        elif self.computer_score > self.player_score:
            opponent = self.player2_name if self.game_mode == "two_player" else "Komputer"
            title = f"[WIN] {opponent} Menang!"
            color = BLUE
        else:
            title = "[DRAW] Seri!"
            color = GOLD

        # Title with better spacing
        text = self.font_large.render(title, True, color)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, box_y + 60))
        self.screen.blit(text, text_rect)
        
        # Decorative line
        line_y = box_y + 95
        pygame.draw.line(self.screen, GOLD, (box_x + 50, line_y), (box_x + box_width - 50, line_y), 3)

        # Score section with better spacing
        score_y = box_y + 130
        
        # Player 1 score box
        p1_box = pygame.Rect(box_x + 40, score_y, box_width - 80, 60)
        pygame.draw.rect(self.screen, PINK, p1_box, border_radius=10)
        pygame.draw.rect(self.screen, RED, p1_box, 3, border_radius=10)
        
        # Player 1 name and score
        p1_name_text = self.font_medium.render(self.player1_name, True, RED)
        p1_score_text = self.font_xlarge.render(str(self.player_score), True, RED)
        
        p1_name_rect = p1_name_text.get_rect(midleft=(p1_box.x + 20, p1_box.centery))
        p1_score_rect = p1_score_text.get_rect(midright=(p1_box.right - 20, p1_box.centery))
        
        self.screen.blit(p1_name_text, p1_name_rect)
        self.screen.blit(p1_score_text, p1_score_rect)

        score_y += 80

        # Player 2 / Computer score box
        opponent = self.player2_name if self.game_mode == "two_player" else "Komputer"
        p2_box = pygame.Rect(box_x + 40, score_y, box_width - 80, 60)
        pygame.draw.rect(self.screen, LIGHT_BLUE, p2_box, border_radius=10)
        pygame.draw.rect(self.screen, BLUE, p2_box, 3, border_radius=10)
        
        # Player 2 name and score
        p2_name_text = self.font_medium.render(opponent, True, BLUE)
        p2_score_text = self.font_xlarge.render(str(self.computer_score), True, BLUE)
        
        p2_name_rect = p2_name_text.get_rect(midleft=(p2_box.x + 20, p2_box.centery))
        p2_score_rect = p2_score_text.get_rect(midright=(p2_box.right - 20, p2_box.centery))
        
        self.screen.blit(p2_name_text, p2_name_rect)
        self.screen.blit(p2_score_text, p2_score_rect)

        # Play again button with better positioning
        btn_y = box_y + 290
        play_again_btn = Button(SCREEN_WIDTH // 2 - 130, btn_y, 260, 55, "[RESTART] Main Lagi", DARK_GREEN, WHITE)
        play_again_btn.update_hover(pygame.mouse.get_pos())
        
        # Button shadow
        pygame.draw.rect(self.screen, BLACK, (SCREEN_WIDTH // 2 - 128, btn_y + 2, 260, 55), border_radius=10)
        play_again_btn.draw(self.screen, self.font_medium)
        
        return play_again_btn

    def run(self):
        running = True
        play_again_btn = None
        start_btn = None
        back_btn = None

        while running:
            self.clock.tick(FPS)

            mouse_pos = pygame.mouse.get_pos()
           
            if self.editing_name:
                current_time = pygame.time.get_ticks()
                if current_time - self.name_cursor_timer > 500:
                    self.name_cursor_visible = not self.name_cursor_visible
                    self.name_cursor_timer = current_time

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and not self.editing_name:
                        running = False
                        continue

                if self.editing_name and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                        if event.key == pygame.K_RETURN and len(self.temp_name.strip()) > 0:
                            if self.editing_name == "player1":
                                self.player1_name = self.temp_name.strip()
                            elif self.editing_name == "player2":
                                self.player2_name = self.temp_name.strip()
                        self.editing_name = None
                        self.temp_name = ""
                    elif event.key == pygame.K_BACKSPACE:
                        self.temp_name = self.temp_name[:-1]
                    elif len(self.temp_name) < 20 and event.unicode.isprintable():
                        self.temp_name += event.unicode

                if self.screen_state == "level_select":
                    self.row_slider.handle_event(event, mouse_pos)
                    self.col_slider.handle_event(event, mouse_pos)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    self.play_click_sound()  # Play sound effect

                    if self.screen_state == "home":
                        play_btn, how_to_btn, credits_btn, exit_btn = None, None, None, None
                        
                        # Get buttons from draw function
                        temp_buttons = self.draw_home_screen()
                        if temp_buttons:
                            play_btn, how_to_btn, credits_btn, exit_btn = temp_buttons
                        
                        if play_btn and play_btn.is_clicked(pos):
                            self.screen_state = "level_select"
                            continue
                        elif how_to_btn and how_to_btn.is_clicked(pos):
                            self.screen_state = "how_to_play"
                            continue
                        elif credits_btn and credits_btn.is_clicked(pos):
                            self.screen_state = "credits"
                            continue
                        elif exit_btn and exit_btn.is_clicked(pos):
                            running = False
                            continue

                    elif self.screen_state == "how_to_play":
                        if back_btn and back_btn.is_clicked(pos):
                            self.screen_state = "home"
                            continue

                    elif self.screen_state == "credits":
                        if back_btn and back_btn.is_clicked(pos):
                            self.screen_state = "home"
                            continue

                    elif self.screen_state == "level_select":
                        if start_btn and start_btn.is_clicked(pos):
                            self.screen_state = "mode_select"
                            continue

                    elif self.screen_state == "mode_select":
                        computer_btn = Button((SCREEN_WIDTH - 450) // 2 + 40, (SCREEN_HEIGHT - 350) // 2 + 130, 370, 70, "", DEEP_BLUE)
                        two_player_btn = Button((SCREEN_WIDTH - 450) // 2 + 40, (SCREEN_HEIGHT - 350) // 2 + 220, 370, 70, "", DEEP_RED)
                       
                        if computer_btn.rect.collidepoint(pos):
                            self.game_mode = "computer"
                            self.screen_state = "playing"
                            self.reset_game()
                            continue
                       
                        if two_player_btn.rect.collidepoint(pos):
                            self.game_mode = "two_player"
                            self.screen_state = "playing"
                            self.reset_game()
                            continue

                    elif self.screen_state == "playing":
                        if hasattr(self, 'player1_edit_btn') and self.player1_edit_btn and self.player1_edit_btn.collidepoint(pos) and not self.editing_name:
                            self.editing_name = "player1"
                            self.temp_name = self.player1_name
                            self.name_cursor_visible = True
                            self.name_cursor_timer = pygame.time.get_ticks()
                            continue
                       
                        if hasattr(self, 'player2_edit_btn') and self.player2_edit_btn and self.player2_edit_btn.collidepoint(pos) and not self.editing_name:
                            self.editing_name = "player2"
                            self.temp_name = self.player2_name
                            self.name_cursor_visible = True
                            self.name_cursor_timer = pygame.time.get_ticks()
                            continue

                        # Sound control buttons
                        if self.music_button.is_clicked(pos):
                            self.toggle_music()
                            continue
                        
                        if self.sound_button.is_clicked(pos):
                            self.toggle_sound()
                            continue

                        if self.new_game_button.is_clicked(pos):
                            self.game_mode = None
                            self.screen_state = "home"  # Kembali ke home
                            self.editing_name = None
                            self.reset_game()
                            continue

                        if self.game_over and play_again_btn and play_again_btn.is_clicked(pos):
                            self.game_mode = None
                            self.screen_state = "home"  # Kembali ke home
                            self.editing_name = None
                            self.reset_game()
                            continue

                        if self.phase == "select_factors" and (self.factor_selector == "player" or (self.factor_selector == "computer" and self.game_mode == "two_player")):
                            if self.confirm_button.is_clicked(pos):
                                self.confirm_selection()
                                continue

                        if not self.game_over:
                            for num, button in self.number_buttons.items():
                                if button.is_clicked(pos):
                                    if self.phase == "choose_number" and self.current_player == "player":
                                        self.choose_number(num)
                                    elif self.phase == "choose_number" and self.current_player == "computer" and self.game_mode == "two_player":
                                        self.choose_number(num)
                                    elif self.phase == "select_factors" and self.factor_selector == "player":
                                        self.toggle_factor_selection(num)
                                    elif self.phase == "select_factors" and self.factor_selector == "computer" and self.game_mode == "two_player":
                                        self.toggle_factor_selection(num)
                                    break
           
            if self.computer_thinking and not self.game_over and self.game_mode == "computer":
                if pygame.time.get_ticks() - self.thinking_timer > 1500:
                    if self.phase == "choose_number" and self.current_player == "computer":
                        self.computer_choose_number()
                    elif self.phase == "select_factors" and self.factor_selector == "computer":
                        self.player_2_select_factors()
           
            # Update efek berkedip
            if self.phase == "select_factors":
                current_time = pygame.time.get_ticks()
                if current_time - self.blink_timer > 400: 
                    self.blink_visible = not self.blink_visible
                    self.blink_timer = current_time
            else:
                self.blink_visible = True  # Reset saat tidak di fase select_factors

            self.screen.fill(CREAM)
           
            if self.screen_state == "home":
                play_btn, how_to_btn, credits_btn, exit_btn = self.draw_home_screen()
                play_again_btn = None
                start_btn = None
                back_btn = None
            elif self.screen_state == "how_to_play":
                back_btn = self.draw_how_to_play()
                play_again_btn = None
                start_btn = None
            elif self.screen_state == "credits":
                back_btn = self.draw_credits()
                play_again_btn = None
                start_btn = None
            elif self.screen_state == "level_select":
                start_btn = self.draw_level_selection()
                play_again_btn = None
                back_btn = None
            elif self.screen_state == "mode_select":
                computer_btn, two_player_btn = self.draw_mode_selection()
                play_again_btn = None
                start_btn = None
                back_btn = None
            elif self.screen_state == "playing":
                self.draw_header()
                self.draw_left_panel()
                self.draw_game_board()

                if hasattr(self, "pending_switch") and self.pending_switch:
                    if pygame.time.get_ticks() >= self.pending_switch_time:
                        self.pending_switch = False
                        self.switch_player()

                if self.game_over:
                    play_again_btn = self.draw_game_over_message()

            pygame.display.flip()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = FactorGame()
    game.run()