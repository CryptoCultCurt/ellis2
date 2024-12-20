import pygame
import random
import math
import numpy as np

# Initialize Pygame and its mixer
pygame.init()
pygame.mixer.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
HUD_HEIGHT = 50  # Height of the HUD area
PLAYER_SIZE = 20
BOT_SIZE = 20
PLAYER_SPEED = 5
BOT_SPEED = 3
SAFE_ZONE_SHRINK_RATE = 0.999
DAMAGE_OUTSIDE_ZONE = 1
BULLET_SPEED = 7
BULLET_SIZE = 5
BULLET_DAMAGE = 34  # Increased damage (3 hits to kill)
SHOOT_COOLDOWN = 500
SCORE_PER_HIT = 10
SCORE_PER_KILL = 50  # Added bonus points for kills
NUM_BOTS = 3  # Reduced number of bots
BOT_DIRECTION_CHANGE_TIME = 1000  # Time in ms before bot changes direction

PARTICLE_COLORS = [
    (255, 223, 0),   # Gold
    (255, 215, 0),   # Yellow Gold
    (255, 255, 0),   # Yellow
    (255, 200, 0),   # Orange Gold
    (255, 255, 255), # White
]

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)  # Player color (lighter blue)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)
LIME = (50, 255, 50)
TEAL = (0, 128, 128)
GRAY = (128, 128, 128)  # Added back for HUD
GOLD = (255, 215, 0)

# List of colors for bots (excluding player color)
BOT_COLORS = [
    RED,      # Aggressive red
    PURPLE,   # Royal purple
    ORANGE,   # Bright orange
    LIME,     # Neon green
    CYAN,     # Electric blue
    PINK,     # Soft pink
    TEAL,     # Deep teal
    (255, 128, 0),    # Dark orange
    (128, 0, 255)     # Deep purple
]

class Bullet:
    def __init__(self, start_x, start_y, target_x, target_y, is_enemy, color=WHITE, speed=10, size=3, damage=10):
        self.x = start_x
        self.y = start_y
        self.is_enemy = is_enemy
        self.color = color
        self.size = size
        self.damage = damage
        
        # Calculate direction
        dx = target_x - start_x
        dy = target_y - start_y
        length = math.sqrt(dx * dx + dy * dy)
        if length > 0:
            self.dx = (dx / length) * speed
            self.dy = (dy / length) * speed
        else:
            self.dx = speed
            self.dy = 0

    def move(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

    def is_off_screen(self):
        return (self.x < 0 or self.x > WINDOW_WIDTH or 
                self.y < HUD_HEIGHT or self.y > WINDOW_HEIGHT)

class Player:
    def __init__(self, x, y, color, is_bot=False):
        self.x = x
        self.y = y
        self.color = color
        self.health = 100
        self.alive = True
        self.hit_flash_time = 0
        self.last_shot_time = 0
        self.is_bot = is_bot

    def can_shoot(self, current_time):
        return current_time - self.last_shot_time >= SHOOT_COOLDOWN

    def move(self, dx, dy):
        if not self.alive:
            return
            
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Keep player within bounds
        new_x = max(PLAYER_SIZE, min(WINDOW_WIDTH - PLAYER_SIZE, new_x))
        new_y = max(HUD_HEIGHT + PLAYER_SIZE, min(WINDOW_HEIGHT - PLAYER_SIZE, new_y))
        
        self.x = new_x
        self.y = new_y

    def draw(self):
        if self.alive:
            if pygame.time.get_ticks() - self.hit_flash_time < 100:
                pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), PLAYER_SIZE)
            else:
                pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), PLAYER_SIZE)

    def shoot(self, target_x, target_y, current_time):
        if not self.alive or not self.can_shoot(current_time):
            return None

        self.last_shot_time = current_time
        return Bullet(self.x, self.y, target_x, target_y, False, self.color)

class Bot(Player):
    def __init__(self, x, y, color):
        super().__init__(x, y, color, is_bot=True)
        self.direction_change_time = 0
        self.dx = random.choice([-1, 1]) * BOT_SPEED
        self.dy = random.choice([-1, 1]) * BOT_SPEED
        
    def normalize_direction(self):
        length = math.sqrt(self.dx * self.dx + self.dy * self.dy)
        if length != 0:
            self.dx /= length
            self.dy /= length
    
    def update_direction(self, current_time):
        if current_time - self.direction_change_time > BOT_DIRECTION_CHANGE_TIME:
            # 70% chance to pick a new random direction, 30% chance to move towards safe zone
            if random.random() < 0.7:
                self.dx = random.uniform(-1, 1)
                self.dy = random.uniform(-1, 1)
                self.normalize_direction()
            else:
                # Move towards the center
                dx = WINDOW_WIDTH//2 - self.x
                dy = (WINDOW_HEIGHT + HUD_HEIGHT)//2 - self.y
                length = math.sqrt(dx * dx + dy * dy)
                if length != 0:
                    self.dx = dx / length
                    self.dy = dy / length
            self.direction_change_time = current_time
    
    def move_with_direction(self):
        if not self.alive:
            return
        current_time = pygame.time.get_ticks()
        self.update_direction(current_time)
        self.move(self.dx * BOT_SPEED, self.dy * BOT_SPEED)

    def draw(self):
        if self.alive:
            # Draw the bot with its unique color
            if pygame.time.get_ticks() - self.hit_flash_time < 100:
                pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), BOT_SIZE)
            else:
                pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), BOT_SIZE)
                # Add a small white dot in the center for better visibility
                pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), BOT_SIZE//4)

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = random.choice(PARTICLE_COLORS)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 6)
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
        self.lifetime = 255
        self.size = random.randint(2, 4)
        
    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.dy += 0.1  # Gravity
        self.lifetime -= 3
        return self.lifetime > 0
        
    def draw(self, screen):
        alpha = max(0, min(255, self.lifetime))
        color = (self.color[0], self.color[1], self.color[2], alpha)
        surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (self.size, self.size), self.size)
        screen.blit(surf, (int(self.x - self.size), int(self.y - self.size)))

class Weapon:
    def __init__(self, name, damage, fire_rate, bullet_speed, bullet_size, bullet_color, sound_freq):
        self.name = name
        self.damage = damage
        self.fire_rate = fire_rate  # milliseconds between shots
        self.bullet_speed = bullet_speed
        self.bullet_size = bullet_size
        self.bullet_color = bullet_color
        self.sound_freq = sound_freq
        self.last_shot = 0

    def can_shoot(self, current_time):
        return current_time - self.last_shot >= self.fire_rate

    def shoot(self, current_time):
        self.last_shot = current_time
        return True

class WeaponInventory:
    def __init__(self):
        self.weapons = {
            'Pistol': Weapon('Pistol', damage=10, fire_rate=500, bullet_speed=10, 
                           bullet_size=3, bullet_color=YELLOW, sound_freq=440),
            'Shotgun': Weapon('Shotgun', damage=15, fire_rate=1000, bullet_speed=8, 
                            bullet_size=4, bullet_color=RED, sound_freq=220),
            'Sniper': Weapon('Sniper', damage=50, fire_rate=2000, bullet_speed=15, 
                           bullet_size=2, bullet_color=BLUE, sound_freq=880),
            'MachineGun': Weapon('MachineGun', damage=5, fire_rate=100, bullet_speed=12, 
                                bullet_size=2, bullet_color=GREEN, sound_freq=660)
        }
        self.current_weapon = self.weapons['Pistol']
    
    def switch_weapon(self, weapon_name):
        if weapon_name in self.weapons:
            self.current_weapon = self.weapons[weapon_name]
            return True
        return False

    def next_weapon(self):
        weapons_list = list(self.weapons.keys())
        current_index = weapons_list.index(self.current_weapon.name)
        next_index = (current_index + 1) % len(weapons_list)
        self.current_weapon = self.weapons[weapons_list[next_index]]

    def prev_weapon(self):
        weapons_list = list(self.weapons.keys())
        current_index = weapons_list.index(self.current_weapon.name)
        prev_index = (current_index - 1) % len(weapons_list)
        self.current_weapon = self.weapons[weapons_list[prev_index]]

class Game:
    def __init__(self):
        self.reset_game()
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 74)
        self.title_font = pygame.font.Font(None, 100)
        self.countdown_font = pygame.font.Font(None, 200)  # Large font for countdown
        self.game_over = False
        self.victory = False
        self.game_started = False
        self.countdown_start = 0
        self.in_countdown = False
        self.particles = []
        self.victory_start_time = 0
        
        # Initialize sound effects as None first
        self.shoot_sound = None
        self.hit_sound = None
        self.death_sound = None
        self.victory_sound = None
        self.game_over_sound = None
        self.victory_music = None
        self.countdown_sound = None
        
        # Try to load sound effects
        try:
            import os
            sound_dir = os.path.join(os.path.dirname(__file__), 'sounds')
            
            if os.path.exists(os.path.join(sound_dir, 'shoot.wav')):
                self.shoot_sound = pygame.mixer.Sound(os.path.join(sound_dir, 'shoot.wav'))
                self.shoot_sound.set_volume(0.3)
            
            if os.path.exists(os.path.join(sound_dir, 'hit.wav')):
                self.hit_sound = pygame.mixer.Sound(os.path.join(sound_dir, 'hit.wav'))
                self.hit_sound.set_volume(0.4)
            
            if os.path.exists(os.path.join(sound_dir, 'death.wav')):
                self.death_sound = pygame.mixer.Sound(os.path.join(sound_dir, 'death.wav'))
                self.death_sound.set_volume(0.5)
            
            if os.path.exists(os.path.join(sound_dir, 'victory_music.wav')):
                self.victory_music = pygame.mixer.Sound(os.path.join(sound_dir, 'victory_music.wav'))
                self.victory_music.set_volume(0.6)
            
            if os.path.exists(os.path.join(sound_dir, 'game_over.wav')):
                self.game_over_sound = pygame.mixer.Sound(os.path.join(sound_dir, 'game_over.wav'))
                self.game_over_sound.set_volume(0.6)

            if os.path.exists(os.path.join(sound_dir, 'countdown_beep.wav')):
                self.countdown_sound = pygame.mixer.Sound(os.path.join(sound_dir, 'countdown_beep.wav'))
                self.countdown_sound.set_volume(0.4)
        except Exception as e:
            print(f"Warning: Could not load sound effects: {e}")

    def play_sound(self, sound):
        if sound is not None:
            try:
                sound.play()
            except Exception as e:
                print(f"Warning: Could not play sound effect: {e}")

    def create_particles(self, x, y, count=20):
        for _ in range(count):
            self.particles.append(Particle(x, y))

    def update_particles(self):
        self.particles = [p for p in self.particles if p.update()]

    def reset_game(self):
        self.player = Player(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + HUD_HEIGHT, BLUE)
        self.bots = []
        self.bullets = []
        self.particles = []
        self.safe_zone_radius = min(WINDOW_WIDTH, WINDOW_HEIGHT - HUD_HEIGHT) // 2
        self.safe_zone_center = (WINDOW_WIDTH//2, (WINDOW_HEIGHT + HUD_HEIGHT)//2)
        self.score = 0
        self.game_over = False
        self.victory = False
        self.victory_start_time = 0
        self.game_started = False
        self.in_countdown = False
        self.weapon_inventory = WeaponInventory()
        self.create_bots()

    def create_bots(self):
        for i in range(NUM_BOTS):
            # Pick a unique color for each bot
            bot_color = BOT_COLORS[i % len(BOT_COLORS)]
            
            # Spawn bots around the edges
            if i == 0:  # Top edge
                x = random.randint(0, WINDOW_WIDTH)
                y = HUD_HEIGHT + BOT_SIZE
            elif i == 1:  # Right edge
                x = WINDOW_WIDTH - BOT_SIZE
                y = random.randint(HUD_HEIGHT, WINDOW_HEIGHT)
            else:  # Left edge
                x = BOT_SIZE
                y = random.randint(HUD_HEIGHT, WINDOW_HEIGHT)
            
            self.bots.append(Bot(x, y, bot_color))

    def move_bots(self):
        for bot in self.bots:
            if not bot.alive:
                continue
            bot.move_with_direction()
            
            # Bot shooting
            current_time = pygame.time.get_ticks()
            if bot.can_shoot(current_time) and random.random() < 0.02:
                if self.player.alive:
                    # Shoot at player with some randomness
                    target_x = self.player.x + random.uniform(-50, 50)
                    target_y = self.player.y + random.uniform(-50, 50)
                    bullet = bot.shoot(target_x, target_y, current_time)
                    if bullet:
                        self.bullets.append(bullet)

    def update_bullets(self):
        # Move bullets and check for collisions
        for bullet in self.bullets[:]:
            bullet.move()
            
            # Check collision with player
            if self.player.alive:
                dx = bullet.x - self.player.x
                dy = bullet.y - self.player.y
                distance = math.sqrt(dx**2 + dy**2)
                if distance < PLAYER_SIZE + bullet.size and bullet.is_enemy:
                    self.player.health -= bullet.damage
                    self.player.hit_flash_time = pygame.time.get_ticks()
                    self.play_sound(self.hit_sound)
                    print(f"Player hit! Health: {self.player.health}")
                    if self.player.health <= 0:
                        self.player.alive = False
                        self.play_sound(self.death_sound)
                        print("Player eliminated!")
                    self.bullets.remove(bullet)
                    continue

            # Check collision with bots
            for bot in self.bots:
                if bot.alive:
                    dx = bullet.x - bot.x
                    dy = bullet.y - bot.y
                    distance = math.sqrt(dx**2 + dy**2)
                    if distance < BOT_SIZE + bullet.size and not bullet.is_enemy:
                        bot.health -= bullet.damage
                        bot.hit_flash_time = pygame.time.get_ticks()
                        self.play_sound(self.hit_sound)
                        print(f"Bot hit! Health: {bot.health}")
                        self.score += SCORE_PER_HIT
                        if bot.health <= 0:
                            bot.alive = False
                            self.score += SCORE_PER_KILL
                            self.play_sound(self.death_sound)
                            print("Bot eliminated!")
                        self.bullets.remove(bullet)
                        break

            # Remove bullets that are out of bounds
            if bullet in self.bullets and bullet.is_off_screen():
                self.bullets.remove(bullet)

    def update_safe_zone(self):
        self.safe_zone_radius *= SAFE_ZONE_SHRINK_RATE
        if self.safe_zone_radius < 50:
            self.safe_zone_radius = 50

    def check_zone_damage(self):
        # Check player
        if self.player.alive:
            distance = math.sqrt((self.player.x - self.safe_zone_center[0])**2 + 
                               (self.player.y - self.safe_zone_center[1])**2)
            if distance > self.safe_zone_radius:
                self.player.health -= DAMAGE_OUTSIDE_ZONE
                if self.player.health <= 0:
                    self.player.alive = False

        # Check bots
        for bot in self.bots:
            if not bot.alive:
                continue
            distance = math.sqrt((bot.x - self.safe_zone_center[0])**2 + 
                               (bot.y - self.safe_zone_center[1])**2)
            if distance > self.safe_zone_radius:
                bot.health -= DAMAGE_OUTSIDE_ZONE
                if bot.health <= 0:
                    bot.alive = False

    def draw_hud(self):
        # Draw HUD background
        pygame.draw.rect(screen, GRAY, (0, 0, WINDOW_WIDTH, HUD_HEIGHT))
        
        # Draw score
        score_text = self.font.render(f'Score: {self.score}', True, WHITE)
        screen.blit(score_text, (10, 10))
        
        # Draw number of players remaining
        alive_bots = len([bot for bot in self.bots if bot.alive])
        players_text = self.font.render(f'Players: {alive_bots + (1 if self.player.alive else 0)}', True, WHITE)
        screen.blit(players_text, (WINDOW_WIDTH - 150, 10))
        
        # Draw player health with color indicator
        if self.player.alive:
            health_text = self.font.render(f'Health: {int(self.player.health)}', True, BLUE)  # Match player color
            screen.blit(health_text, (WINDOW_WIDTH // 2 - 50, 10))

        # Draw current weapon
        weapon_text = self.font.render(f'Weapon: {self.weapon_inventory.current_weapon.name}', True, WHITE)
        screen.blit(weapon_text, (10, 40))

    def draw_game_over_screen(self):
        screen.fill(BLACK)
        
        # Draw game over text
        if self.victory:
            text = self.title_font.render("VICTORY!", True, GREEN)
        else:
            text = self.title_font.render("GAME OVER", True, RED)
        text_rect = text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//3))
        screen.blit(text, text_rect)
        
        # Draw score
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
        screen.blit(score_text, score_rect)
        
        # Draw play again button
        button_width = 200
        button_height = 50
        button_x = WINDOW_WIDTH//2 - button_width//2
        button_y = WINDOW_HEIGHT * 2//3
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_over_button = (button_x <= mouse_pos[0] <= button_x + button_width and 
                           button_y <= mouse_pos[1] <= button_y + button_height)
        
        print(f"Game Over Screen - Button: x={button_x}, y={button_y}, w={button_width}, h={button_height}")
        print(f"Mouse: x={mouse_pos[0]}, y={mouse_pos[1]}")
        print(f"Mouse over button: {mouse_over_button}")
        
        button_color = (100, 100, 255) if mouse_over_button else (70, 70, 200)
        
        pygame.draw.rect(screen, button_color, (button_x, button_y, button_width, button_height))
        pygame.draw.rect(screen, WHITE, (button_x, button_y, button_width, button_height), 2)
        
        play_again_text = self.font.render("Play Again", True, WHITE)
        text_rect = play_again_text.get_rect(center=(WINDOW_WIDTH//2, button_y + button_height//2))
        screen.blit(play_again_text, text_rect)
        
        pygame.display.flip()
        
        # Return button rectangle for click detection
        return (button_x, button_y, button_width, button_height)

    def draw_start_screen(self):
        screen.fill(BLACK)
        
        # Draw title
        title = self.title_font.render("BATTLE ROYALE", True, BLUE)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, 100))
        screen.blit(title, title_rect)
        
        # Draw instructions
        instructions = [
            "Controls:",
            "Arrow Keys - Move",
            "Spacebar - Shoot",
            "",
            "Objective:",
            "Eliminate all bots",
            "Stay in the safe zone",
            "Score points with hits and kills",
            "",
            "Press ENTER or click Start to begin"
        ]
        
        y_pos = 200
        for line in instructions:
            text = self.font.render(line, True, WHITE)
            text_rect = text.get_rect(center=(WINDOW_WIDTH//2, y_pos))
            screen.blit(text, text_rect)
            y_pos += 35
        
        # Draw start button
        button_width = 200
        button_height = 50
        button_x = WINDOW_WIDTH//2 - button_width//2
        button_y = WINDOW_HEIGHT - 100
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_over_button = (button_x <= mouse_pos[0] <= button_x + button_width and 
                           button_y <= mouse_pos[1] <= button_y + button_height)
        
        # Debug output for button position and mouse
      #  print(f"Button: x={button_x}, y={button_y}, w={button_width}, h={button_height}")
     #   print(f"Mouse: x={mouse_pos[0]}, y={mouse_pos[1]}")
      #  print(f"Mouse over button: {mouse_over_button}")
        
        button_color = (100, 100, 255) if mouse_over_button else (70, 70, 200)
        
        pygame.draw.rect(screen, button_color, (button_x, button_y, button_width, button_height))
        pygame.draw.rect(screen, WHITE, (button_x, button_y, button_width, button_height), 2)
        
        start_text = self.font.render("Start Game", True, WHITE)
        text_rect = start_text.get_rect(center=(WINDOW_WIDTH//2, button_y + button_height//2))
        screen.blit(start_text, text_rect)
        
        pygame.display.flip()
        
        # Return button rectangle for click detection
        return (button_x, button_y, button_width, button_height)

    def draw(self):
        if self.game_started:
            if self.game_over:
                return self.draw_game_over_screen()  # Return button rect for game over screen
            else:
                # Draw game screen
                screen.fill(BLACK)
                
                # Draw game elements
                self.draw_hud()
                pygame.draw.line(screen, WHITE, (0, HUD_HEIGHT), (WINDOW_WIDTH, HUD_HEIGHT))
                pygame.draw.circle(screen, YELLOW, self.safe_zone_center, int(self.safe_zone_radius), 2)
                
                # Draw players and bullets
                if self.player.alive:
                    self.player.draw()
                for bot in self.bots:
                    if bot.alive:
                        bot.draw()
                for bullet in self.bullets:
                    bullet.draw()
                
                pygame.display.flip()
                return None  # No button rect needed
        elif self.in_countdown:
            self.draw_countdown()
            return None  # No button rect needed
        else:
            return self.draw_start_screen()  # Returns button rect

    def draw_countdown(self):
        screen.fill(BLACK)
        current_time = pygame.time.get_ticks()
        time_elapsed = (current_time - self.countdown_start) / 1000  # Convert to seconds
        countdown_value = 4 - int(time_elapsed)  # Start from 3
        
        print(f"Countdown - Time elapsed: {time_elapsed:.1f}s, Value: {countdown_value}")
        
        if countdown_value <= 0:
            print("Countdown finished - Starting game!")
            self.in_countdown = False
            self.game_started = True
            return
        
        # Play beep sound at the start of each number
        if countdown_value < 4 and abs(time_elapsed - int(time_elapsed)) < 0.1:
            self.play_sound(self.countdown_sound)
            print(f"Beep! Countdown: {countdown_value}")
        
        if countdown_value <= 3:  # Don't show 4
            # Calculate scale based on time within this second
            scale = 1 + 0.5 * (1 - (time_elapsed - int(time_elapsed)))
            
            # Render countdown number
            text = self.countdown_font.render(str(countdown_value), True, WHITE)
            text_rect = text.get_rect()
            scaled_surface = pygame.transform.scale(text, 
                                                 (int(text_rect.width * scale), 
                                                  int(text_rect.height * scale)))
            text_rect = scaled_surface.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            screen.blit(scaled_surface, text_rect)
        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        running = True
        print("Game starting...")

        while running:
            # Get current button state and draw current frame
            button_rect = self.draw()
            pygame.display.flip()  # Make sure we update the display
            
            # Debug output for game state
            if self.game_started:
                if not hasattr(self, '_last_game_state') or self._last_game_state != 'game':
                    print("\nGame State: Playing Game")
                    print(f"Player alive: {self.player.alive}")
                    print(f"Bots alive: {sum(1 for bot in self.bots if bot.alive)}")
                    self._last_game_state = 'game'
            elif self.in_countdown:
                if not hasattr(self, '_last_game_state') or self._last_game_state != 'countdown':
                    print("\nGame State: Countdown")
                    self._last_game_state = 'countdown'
            else:
                if not hasattr(self, '_last_game_state') or self._last_game_state != 'start':
                    print("\nGame State: Start Screen")
                    self._last_game_state = 'start'
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    print(f"\nMouse Click at {mouse_pos}")
                    print(f"Button rect: {button_rect}")
                    
                    if button_rect:
                        # Check if click is within button bounds
                        in_button = (button_rect[0] <= mouse_pos[0] <= button_rect[0] + button_rect[2] and 
                                   button_rect[1] <= mouse_pos[1] <= button_rect[1] + button_rect[3])
                        print(f"Click in button bounds: {in_button}")
                        
                        if in_button:  # Only trigger if click is within button
                            if not self.game_started and not self.in_countdown:
                                print("Starting countdown!")
                                self.in_countdown = True
                                self.countdown_start = pygame.time.get_ticks()
                            elif self.game_over:
                                print("Resetting game!")
                                self.reset_game()
                                self.in_countdown = True
                                self.countdown_start = pygame.time.get_ticks()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    print("Enter key pressed!")
                    if not self.game_started and not self.in_countdown:
                        print("Starting countdown!")
                        self.in_countdown = True
                        self.countdown_start = pygame.time.get_ticks()
                    elif self.game_over:
                        print("Resetting game!")
                        self.reset_game()
                        self.in_countdown = True
                        self.countdown_start = pygame.time.get_ticks()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if self.game_started and not self.game_over:
                        current_time = pygame.time.get_ticks()
                        if self.weapon_inventory.current_weapon.can_shoot(current_time):
                            dx = 0
                            dy = 0
                            keys = pygame.key.get_pressed()
                            if keys[pygame.K_UP]:
                                dy -= 1
                            if keys[pygame.K_DOWN]:
                                dy += 1
                            if keys[pygame.K_LEFT]:
                                dx -= 1
                            if keys[pygame.K_RIGHT]:
                                dx += 1
                            length = math.sqrt(dx * dx + dy * dy)
                            if length > 0:
                                target_x = self.player.x + (dx / length) * 100
                                target_y = self.player.y + (dy / length) * 100
                            else:
                                target_x = self.player.x + 100
                                target_y = self.player.y
                            bullet = Bullet(self.player.x, self.player.y, target_x, target_y, False, 
                                            self.weapon_inventory.current_weapon.bullet_color, 
                                            self.weapon_inventory.current_weapon.bullet_speed, 
                                            self.weapon_inventory.current_weapon.bullet_size, 
                                            self.weapon_inventory.current_weapon.damage)
                            self.bullets.append(bullet)
                            self.weapon_inventory.current_weapon.shoot(current_time)
                            self.play_sound(self.shoot_sound)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_w:
                    self.weapon_inventory.prev_weapon()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                    self.weapon_inventory.next_weapon()

            # Update game state if needed
            if self.in_countdown:
                current_time = pygame.time.get_ticks()
                time_elapsed = (current_time - self.countdown_start) / 1000
                if time_elapsed >= 3:  # 3 second countdown
                    print("\nCountdown finished!")
                    print("Starting game...")
                    self.in_countdown = False
                    self.game_started = True
            
            # Update game logic when game is running
            if self.game_started and not self.game_over and not self.in_countdown:
                if self.player.alive:
                    # Handle player movement and shooting
                    keys = pygame.key.get_pressed()
                    dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * PLAYER_SPEED
                    dy = (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * PLAYER_SPEED
                    
                    # Move player
                    self.player.move(dx, dy)
                    
                # Update game state
                self.move_bots()
                self.update_bullets()
                self.update_safe_zone()
                self.check_zone_damage()

                # Check win/lose condition
                alive_bots = [bot for bot in self.bots if bot.alive]
                if not alive_bots and self.player.alive:
                    self.game_over = True
                    self.victory = True
                    self.play_sound(self.victory_music)
                    print("Victory!")
                elif not self.player.alive:
                    self.game_over = True
                    self.victory = False
                    self.play_sound(self.game_over_sound)
                    print("Game Over!")
                elif not alive_bots and not self.player.alive:
                    self.game_over = True
                    self.victory = False
                    self.play_sound(self.game_over_sound)
                    print("Draw!")

            clock.tick(60)

        pygame.quit()

    def reset_game(self):
        self.player = Player(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + HUD_HEIGHT, BLUE)
        self.bots = []
        self.bullets = []
        self.particles = []
        self.safe_zone_radius = min(WINDOW_WIDTH, WINDOW_HEIGHT - HUD_HEIGHT) // 2
        self.safe_zone_center = (WINDOW_WIDTH//2, (WINDOW_HEIGHT + HUD_HEIGHT)//2)
        self.score = 0
        self.game_over = False
        self.victory = False
        self.victory_start_time = 0
        self.game_started = False
        self.in_countdown = False
        self.weapon_inventory = WeaponInventory()
        self.create_bots()

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Battle Royale")
    game = Game()
    game.run()
