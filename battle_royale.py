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
MAP_WIDTH = 2400
MAP_HEIGHT = 1800
HUD_HEIGHT = 50
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
GRASS_GREEN = (34, 139, 34)
LIGHT_GREEN = (144, 238, 144)
DARK_GREEN = (0, 100, 0)
BROWN = (139, 69, 19)
SAND = (238, 214, 175)
WATER_BLUE = (65, 105, 225)
PURPLE = (128, 0, 128)
GOLD = (255, 215, 0)
ORANGE = (255, 165, 0)

# Game settings
PLAYER_SIZE = 20
BOT_SIZE = 20
PLAYER_SPEED = 5
BOT_SPEED = 3
ZONE_DAMAGE = 1
BULLET_SPEED = 7
BULLET_SIZE = 5
BULLET_DAMAGE = 34
SHOOT_COOLDOWN = 500
SCORE_PER_HIT = 10
SCORE_PER_KILL = 50
NUM_BOTS = 10
BOT_DIRECTION_CHANGE_TIME = 1000

PARTICLE_COLORS = [
    (255, 223, 0),   # Gold
    (255, 215, 0),   # Yellow Gold
    (255, 255, 0),   # Yellow
    (255, 200, 0),   # Orange Gold
    (255, 255, 255), # White
]

# List of colors for bots (excluding player color)
BOT_COLORS = [
    RED,      # Aggressive red
    (255, 0, 255),   # Royal purple
    (255, 165, 0),   # Bright orange
    (50, 255, 50),   # Neon green
    (0, 255, 255),   # Electric blue
    (255, 192, 203), # Soft pink
    (0, 128, 128),   # Deep teal
    (255, 128, 0),    # Dark orange
    (128, 0, 255)     # Deep purple
]

class Bullet:
    def __init__(self, x, y, dx, dy, damage, speed, size, owner, is_enemy=False):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.damage = damage
        self.speed = speed
        self.size = size
        self.owner = owner
        self.is_enemy = is_enemy

    def move(self):
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed

    def draw(self):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.size)

    def is_off_screen(self):
        return (self.x < 0 or self.x > MAP_WIDTH or 
                self.y < HUD_HEIGHT or self.y > MAP_HEIGHT)

class Player:
    def __init__(self, x, y, color, is_bot=False):
        self.x = x
        self.y = y
        self.color = color
        self.max_health = 200
        self.health = self.max_health
        self.alive = True
        self.hit_flash_time = 0
        self.last_shot_time = 0
        self.is_bot = is_bot
        self.weapon_inventory = None

    def can_shoot(self, current_time):
        return current_time - self.last_shot_time >= SHOOT_COOLDOWN

    def move(self, dx, dy):
        if not self.alive:
            return
            
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Keep player within bounds
        new_x = max(0, min(new_x, MAP_WIDTH))
        new_y = max(HUD_HEIGHT, min(new_y, MAP_HEIGHT))
        
        self.x = new_x
        self.y = new_y

    def draw(self):
        if not self.alive:
            return
            
        current_time = pygame.time.get_ticks()
        draw_color = WHITE if current_time - self.hit_flash_time < 100 else self.color
        
        # Draw body (rectangle)
        body_width = PLAYER_SIZE - 4
        body_height = PLAYER_SIZE + 4
        pygame.draw.rect(screen, draw_color, 
                        (self.x - body_width//2, 
                         self.y - body_height//2, 
                         body_width, body_height))
        
        # Draw head (circle)
        head_radius = PLAYER_SIZE//3
        pygame.draw.circle(screen, draw_color, 
                          (int(self.x), int(self.y - body_height//2 - head_radius)), 
                          head_radius)
        
        # Draw health bar
        health_width = 30
        health_height = 4
        pygame.draw.rect(screen, RED, 
                        (self.x - health_width//2, 
                         self.y - body_height - head_radius*2 - 5,
                         health_width, health_height))
        pygame.draw.rect(screen, GREEN, 
                        (self.x - health_width//2, 
                         self.y - body_height - head_radius*2 - 5,
                         health_width * (self.health/self.max_health), health_height))

    def draw_at_pos(self, x, y):
        if not self.alive:
            return
            
        current_time = pygame.time.get_ticks()
        draw_color = WHITE if current_time - self.hit_flash_time < 100 else self.color
        
        # Draw body (rectangle)
        body_width = PLAYER_SIZE - 4
        body_height = PLAYER_SIZE + 4
        pygame.draw.rect(screen, draw_color, 
                        (x - body_width//2, 
                         y - body_height//2, 
                         body_width, body_height))
        
        # Draw head (circle)
        head_radius = PLAYER_SIZE//3
        pygame.draw.circle(screen, draw_color, 
                          (int(x), int(y - body_height//2 - head_radius)), 
                          head_radius)
        
        # Draw health bar
        health_width = 30
        health_height = 4
        pygame.draw.rect(screen, RED, 
                        (x - health_width//2, 
                         y - body_height - head_radius*2 - 5,
                         health_width, health_height))
        pygame.draw.rect(screen, GREEN, 
                        (x - health_width//2, 
                         y - body_height - head_radius*2 - 5,
                         health_width * (self.health/self.max_health), health_height))

    def shoot(self, target_x, target_y, current_time):
        if not self.alive or not self.can_shoot(current_time):
            return None

        self.last_shot_time = current_time
        return self.weapon_inventory.shoot(self, target_x, target_y, current_time)

class Bot(Player):
    def __init__(self, x, y, color):
        super().__init__(x, y, color, is_bot=True)
        self.target_x = x
        self.target_y = y
        self.decision_time = 0
        self.decision_interval = 1000
        self.max_health = 200
        self.health = self.max_health
        self.weapon_inventory = None
        self.last_shot_time = 0

    def update(self, player, current_time):
        if not self.alive:
            return

        # Update decision making
        if current_time - self.decision_time > self.decision_interval:
            self.decision_time = current_time
            # 70% chance to target player, 30% chance to move randomly
            if random.random() < 0.7 and player.alive:
                self.target_x = player.x + random.randint(-100, 100)
                self.target_y = player.y + random.randint(-100, 100)
            else:
                self.target_x = random.randint(0, MAP_WIDTH)
                self.target_y = random.randint(HUD_HEIGHT, MAP_HEIGHT)

        # Move towards target
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            dx = dx/distance * BOT_SPEED
            dy = dy/distance * BOT_SPEED
            
            # Update position
            new_x = self.x + dx
            new_y = self.y + dy
            
            # Keep bot within bounds
            new_x = max(0, min(new_x, MAP_WIDTH))
            new_y = max(HUD_HEIGHT, min(new_y, MAP_HEIGHT))
            
            self.x = new_x
            self.y = new_y

    def draw(self):
        if not self.alive:
            return
            
        # Draw body (rectangle)
        body_width = 30
        body_height = 40
        pygame.draw.rect(screen, self.color, 
                        (self.x - body_width//2,
                         self.y - body_height//2,
                         body_width, body_height))
        
        # Draw head (circle)
        head_radius = 10
        pygame.draw.circle(screen, self.color,
                         (int(self.x), int(self.y - body_height//2 - head_radius)),
                         head_radius)
        
        # Draw health bar
        health_width = 40
        health_height = 5
        # Draw background (red)
        pygame.draw.rect(screen, RED, 
                        (self.x - health_width//2, 
                         self.y - body_height - head_radius*2 - 5,
                         health_width, health_height))
        # Draw current health (green)
        pygame.draw.rect(screen, GREEN, 
                        (self.x - health_width//2, 
                         self.y - body_height - head_radius*2 - 5,
                         health_width * (self.health/self.max_health), health_height))

    def draw_at_pos(self, x, y):
        if not self.alive:
            return
            
        # Draw body (rectangle)
        body_width = 30
        body_height = 40
        pygame.draw.rect(screen, self.color, 
                        (x - body_width//2,
                         y - body_height//2,
                         body_width, body_height))
        
        # Draw head (circle)
        head_radius = 10
        pygame.draw.circle(screen, self.color,
                         (int(x), int(y - body_height//2 - head_radius)),
                         head_radius)
        
        # Draw health bar
        health_width = 40
        health_height = 5
        # Draw background (red)
        pygame.draw.rect(screen, RED, 
                        (x - health_width//2, 
                         y - body_height - head_radius*2 - 5,
                         health_width, health_height))
        # Draw current health (green)
        pygame.draw.rect(screen, GREEN, 
                        (x - health_width//2, 
                         y - body_height - head_radius*2 - 5,
                         health_width * (self.health/self.max_health), health_height))

class TerrainPatch:
    def __init__(self, x, y, size, type):
        self.x = x
        self.y = y
        self.size = size
        self.type = type  # 'grass', 'tree', 'rock', 'water', 'sand'
        
        if self.type == 'tree':
            self.color = DARK_GREEN
        elif self.type == 'rock':
            self.color = GRAY
        elif self.type == 'water':
            self.color = WATER_BLUE
        elif self.type == 'sand':
            self.color = SAND
        else:  # grass
            self.color = LIGHT_GREEN

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

class DamageNumber:
    def __init__(self, x, y, damage):
        self.x = x
        self.y = y
        self.damage = damage
        self.lifetime = 30  # Number of frames the damage number will be visible
        self.y_offset = 0
        self.alpha = 255
        self.font = pygame.font.Font(None, 36)
    
    def update(self):
        self.lifetime -= 1
        self.y_offset -= 1  # Move up
        self.alpha = int((self.lifetime / 30) * 255)  # Fade out
        return self.lifetime > 0
    
    def draw(self, screen):
        text = self.font.render(str(int(self.damage)), True, (255, 255, 0))
        text.set_alpha(self.alpha)
        screen.blit(text, (self.x - text.get_width()//2, self.y + self.y_offset - 20))

class Weapon:
    def __init__(self, name, damage, fire_rate, bullet_speed, bullet_size, bullet_color, sound_freq):
        self.name = name
        self.damage = damage
        self.fire_rate = fire_rate
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
            'Pistol': Weapon('Pistol', 
                           damage=15, 
                           fire_rate=400,  
                           bullet_speed=12, 
                           bullet_size=3,
                           bullet_color=YELLOW,
                           sound_freq=440),
                           
            'Shotgun': Weapon('Shotgun', 
                            damage=8,  
                            fire_rate=800,  
                            bullet_speed=8,  
                            bullet_size=4,
                            bullet_color=RED,
                            sound_freq=220),
                            
            'Sniper': Weapon('Sniper', 
                           damage=75,  
                           fire_rate=1500,  
                           bullet_speed=20,  
                           bullet_size=2,  
                           bullet_color=BLUE,
                           sound_freq=880),
                           
            'AssaultRifle': Weapon('AssaultRifle', 
                                 damage=20,
                                 fire_rate=200,  
                                 bullet_speed=15,
                                 bullet_size=3,
                                 bullet_color=GREEN,
                                 sound_freq=660),
                                 
            'SMG': Weapon('SMG', 
                         damage=12,  
                         fire_rate=100,  
                         bullet_speed=14,
                         bullet_size=2,
                         bullet_color=PURPLE,
                         sound_freq=550),
                         
            'Revolver': Weapon('Revolver', 
                             damage=40,  
                             fire_rate=600,  
                             bullet_speed=13,
                             bullet_size=4,
                             bullet_color=ORANGE,
                             sound_freq=330),
        }
        self.current_weapon = self.weapons[random.choice(list(self.weapons.keys()))]

    def shoot(self, shooter, target_x, target_y, current_time):
        if not shooter.alive or not self.current_weapon:
            return []

        weapon = self.current_weapon
        if current_time - shooter.last_shot_time < weapon.fire_rate:
            return []

        shooter.last_shot_time = current_time
        bullets = []

        dx = target_x - shooter.x
        dy = target_y - shooter.y
        length = math.sqrt(dx*dx + dy*dy)
        if length > 0:
            dx = dx/length
            dy = dy/length

        if weapon.name == "Shotgun":
            num_pellets = 5
            spread_angle = math.pi / 8  
            for i in range(num_pellets):
                angle = math.atan2(dy, dx) + random.uniform(-spread_angle, spread_angle)
                pellet_dx = math.cos(angle)
                pellet_dy = math.sin(angle)
                bullets.append(Bullet(
                    shooter.x, shooter.y,
                    pellet_dx, pellet_dy,
                    weapon.damage // num_pellets,  
                    weapon.bullet_speed,
                    weapon.bullet_size,
                    shooter,
                    isinstance(shooter, Bot)
                ))
        else:
            bullets.append(Bullet(
                shooter.x, shooter.y,
                dx, dy,
                weapon.damage,
                weapon.bullet_speed,
                weapon.bullet_size,
                shooter,
                isinstance(shooter, Bot)
            ))

        return bullets

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

class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.zoom = 0.5  
    
    def update(self, target_x, target_y):
        visible_width = WINDOW_WIDTH / self.zoom
        visible_height = (WINDOW_HEIGHT - HUD_HEIGHT) / self.zoom
        
        self.x = target_x - visible_width // 2
        self.y = target_y - visible_height // 2
        
        self.x = max(0, min(self.x, MAP_WIDTH - visible_width))
        self.y = max(0, min(self.y, MAP_HEIGHT - visible_height))
    
    def apply(self, x, y):
        screen_x = (x - self.x) * self.zoom
        screen_y = (y - self.y) * self.zoom
        return screen_x, screen_y

    def apply_radius(self, radius):
        return radius * self.zoom

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Battle Royale")
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.camera = Camera()
        self.game_started = False
        self.in_countdown = False
        self.in_weapon_select = False
        self.selected_weapon_index = 0
        self.game_over = False
        self.reset_game()

    def reset_game(self):
        self.player = Player(MAP_WIDTH//2, MAP_HEIGHT//2, BLUE)
        self.bots = []
        self.bullets = []
        self.particles = []
        self.damage_numbers = []
        self.safe_zone_radius = min(MAP_WIDTH, MAP_HEIGHT) // 2
        self.safe_zone_center = (MAP_WIDTH//2, MAP_HEIGHT//2)
        self.score = 0
        self.storm_start_time = pygame.time.get_ticks()
        self.storm_started = False
        self.create_bots()

        self.player.weapon_inventory = WeaponInventory()
        self.terrain_patches = []
        
        # Add water bodies
        for _ in range(3):
            x = random.randint(0, MAP_WIDTH)
            y = random.randint(HUD_HEIGHT, MAP_HEIGHT)
            size = random.randint(100, 200)
            self.terrain_patches.append(TerrainPatch(x, y, size, 'water'))
            
            # Add sand around water
            for i in range(8):
                angle = i * (math.pi/4)
                sand_x = x + math.cos(angle) * (size + 20)
                sand_y = y + math.sin(angle) * (size + 20)
                self.terrain_patches.append(TerrainPatch(sand_x, sand_y, 40, 'sand'))
        
        # Add trees
        for _ in range(50):
            x = random.randint(0, MAP_WIDTH)
            y = random.randint(HUD_HEIGHT, MAP_HEIGHT)
            size = random.randint(30, 50)
            self.terrain_patches.append(TerrainPatch(x, y, size, 'tree'))
        
        # Add rocks
        for _ in range(30):
            x = random.randint(0, MAP_WIDTH)
            y = random.randint(HUD_HEIGHT, MAP_HEIGHT)
            size = random.randint(20, 35)
            self.terrain_patches.append(TerrainPatch(x, y, size, 'rock'))
        
        # Add grass patches
        for _ in range(200):
            x = random.randint(0, MAP_WIDTH)
            y = random.randint(HUD_HEIGHT, MAP_HEIGHT)
            size = random.randint(20, 40)
            self.terrain_patches.append(TerrainPatch(x, y, size, 'grass'))

    def create_bots(self):
        self.bots = []
        bot_weapons = ['Pistol', 'SMG', 'Shotgun', 'Sniper']
        
        for _ in range(NUM_BOTS):
            while True:
                x = random.randint(0, MAP_WIDTH)
                y = random.randint(HUD_HEIGHT, MAP_HEIGHT)
                distance_to_player = math.sqrt((x - self.player.x)**2 + (y - self.player.y)**2)
                if distance_to_player > 200:
                    bot = Bot(x, y, random.choice(BOT_COLORS))
                    bot.weapon_inventory = WeaponInventory()
                    chosen_weapon = random.choice(bot_weapons)
                    bot.weapon_inventory.switch_weapon(chosen_weapon)
                    self.bots.append(bot)
                    break

    def handle_input(self):
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -PLAYER_SPEED
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = PLAYER_SPEED
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -PLAYER_SPEED
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = PLAYER_SPEED
        
        # Only move if a movement key is pressed
        if dx != 0 or dy != 0:
            # Normalize diagonal movement
            if dx != 0 and dy != 0:
                dx *= 0.707  # 1/sqrt(2)
                dy *= 0.707
            
            # Update position
            new_x = self.player.x + dx
            new_y = self.player.y + dy
            
            # Keep player within bounds
            self.player.x = max(0, min(new_x, MAP_WIDTH))
            self.player.y = max(HUD_HEIGHT, min(new_y, MAP_HEIGHT))
        
        # Update camera to follow player
        self.camera.update(self.player.x, self.player.y)

    def update_particles(self):
        self.particles = [p for p in self.particles if p.update()]

    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet.move()
            
            if bullet.is_off_screen():
                if bullet in self.bullets:
                    self.bullets.remove(bullet)
                continue
            
            if self.player.alive and bullet.owner != self.player:
                dx = bullet.x - self.player.x
                dy = bullet.y - self.player.y
                distance = math.sqrt(dx**2 + dy**2)
                if distance < PLAYER_SIZE:
                    self.player.health -= bullet.damage
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    if self.player.health <= 0:
                        self.player.alive = False
                        self.player.health = 0
                    continue
            
            for bot in self.bots:
                if bot.alive and bullet.owner != bot:
                    dx = bullet.x - bot.x
                    dy = bullet.y - bot.y
                    distance = math.sqrt(dx**2 + dy**2)
                    if distance < BOT_SIZE:
                        bot.health -= bullet.damage
                        if bullet in self.bullets:
                            self.bullets.remove(bullet)
                        if bullet.owner == self.player:
                            self.damage_numbers.append(DamageNumber(bot.x, bot.y - 20, bullet.damage))
                        if bot.health <= 0:
                            bot.alive = False
                            bot.health = 0
                        break

    def update_safe_zone(self):
        current_time = pygame.time.get_ticks()
        
        if not self.storm_started and self.game_started and current_time - self.storm_start_time >= 20000:
            self.storm_started = True
        
        if self.storm_started:
            self.safe_zone_radius = max(100, self.safe_zone_radius - 0.1)  

    def check_zone_damage(self):
        if not self.storm_started:
            return  
        
        distance_to_center = math.sqrt((self.player.x - self.safe_zone_center[0])**2 + 
                                     (self.player.y - self.safe_zone_center[1])**2)
        if distance_to_center > self.safe_zone_radius and self.player.alive:
            self.player.health -= ZONE_DAMAGE
            if self.player.health <= 0:
                self.player.alive = False
                self.player.health = 0
        
        for bot in self.bots:
            if bot.alive:
                distance_to_center = math.sqrt((bot.x - self.safe_zone_center[0])**2 + 
                                             (bot.y - self.safe_zone_center[1])**2)
                if distance_to_center > self.safe_zone_radius:
                    bot.health -= ZONE_DAMAGE
                    if bot.health <= 0:
                        bot.alive = False
                        bot.health = 0

    def move_bots(self):
        current_time = pygame.time.get_ticks()
        for bot in self.bots:
            if not bot.alive:
                continue

            closest_target = None
            closest_distance = float('inf')
            
            if self.player.alive:
                dx = self.player.x - bot.x
                dy = self.player.y - bot.y
                player_distance = math.sqrt(dx*dx + dy*dy)
                if player_distance < closest_distance:
                    closest_distance = player_distance
                    closest_target = self.player
            
            for other_bot in self.bots:
                if other_bot != bot and other_bot.alive:
                    dx = other_bot.x - bot.x
                    dy = other_bot.y - bot.y
                    bot_distance = math.sqrt(dx*dx + dy*dy)
                    if bot_distance < closest_distance:
                        closest_distance = bot_distance
                        closest_target = other_bot
            
            if closest_target and closest_distance > 50:  
                dx = closest_target.x - bot.x
                dy = closest_target.y - bot.y
                distance = math.sqrt(dx*dx + dy*dy)
                if distance > 0:
                    dx = dx/distance * BOT_SPEED
                    dy = dy/distance * BOT_SPEED
                    
                    new_x = bot.x + dx
                    new_y = bot.y + dy
                    
                    can_move = True
                    for other_bot in self.bots:
                        if other_bot != bot and other_bot.alive:
                            dist = math.sqrt((new_x - other_bot.x)**2 + (new_y - other_bot.y)**2)
                            if dist < 40:  
                                can_move = False
                                break
                    
                    if self.player.alive:
                        dist = math.sqrt((new_x - self.player.x)**2 + (new_y - self.player.y)**2)
                        if dist < 40:
                            can_move = False
                    
                    if can_move:
                        new_x = max(0, min(new_x, MAP_WIDTH))
                        new_y = max(HUD_HEIGHT, min(new_y, MAP_HEIGHT))
                        bot.x = new_x
                        bot.y = new_y
            
            if closest_target and closest_distance < 300:  
                target_x = closest_target.x + random.uniform(-20, 20)
                target_y = closest_target.y + random.uniform(-20, 20)
                bullets = self.shoot(bot, target_x, target_y, current_time)
                if bullets:
                    self.bullets.extend(bullets)

    def handle_bullet_collision(self, bullet):
        if self.player.alive and bullet.owner != self.player:
            dx = self.player.x - bullet.x
            dy = self.player.y - bullet.y
            distance = math.sqrt(dx*dx + dy*dy)
            if distance < PLAYER_SIZE:
                damage = bullet.damage
                self.player.health -= damage
                if self.player.health <= 0:
                    self.player.alive = False
                    self.player.health = 0
                return True

        for bot in self.bots:
            if bot.alive and bullet.owner != bot:
                dx = bot.x - bullet.x
                dy = bot.y - bullet.y
                distance = math.sqrt(dx*dx + dy*dy)
                if distance < BOT_SIZE:
                    damage = bullet.damage
                    bot.health -= damage
                    if bullet.owner == self.player:
                        damage_number = DamageNumber(bot.x, bot.y, damage)
                        self.damage_numbers.append(damage_number)
                    if bot.health <= 0:
                        bot.alive = False
                        bot.health = 0
                        if bullet.owner == self.player:
                            self.score += 1
                    return True
        return False

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
            health_width = 200
            health_height = 20
            health_x = WINDOW_WIDTH//2 - health_width//2
            health_y = 10
            
            # Draw health bar background
            pygame.draw.rect(screen, RED, (health_x, health_y, health_width, health_height))
            # Draw current health
            pygame.draw.rect(screen, GREEN, 
                           (health_x, health_y, 
                            health_width * (self.player.health/self.player.max_health), 
                            health_height))
            
            # Draw health text
            health_text = self.font.render(f'Health: {int(self.player.health)}', True, WHITE)
            screen.blit(health_text, (health_x + health_width//2 - health_text.get_width()//2, 
                                    health_y + health_height + 5))
        
        # Draw current weapon
        if self.player.weapon_inventory.current_weapon:
            weapon_text = self.font.render(f'Weapon: {self.player.weapon_inventory.current_weapon.name}', 
                                         True, WHITE)
            screen.blit(weapon_text, (10, HUD_HEIGHT - 30))

    def draw_game_over_screen(self):
        screen.fill(BLACK)
        if self.player.alive:
            text = self.font.render("Victory Royale!", True, GOLD)
        else:
            text = self.font.render("Game Over", True, RED)
        
        text_rect = text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50))
        screen.blit(text, text_rect)
        
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 20))
        screen.blit(score_text, score_rect)
        
        restart_text = self.font.render("Click anywhere to restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 90))
        screen.blit(restart_text, restart_rect)

    def draw_start_screen(self):
        screen.fill(BLACK)
        title_text = self.font.render("Battle Royale", True, WHITE)
        start_text = self.font.render("Click to Start", True, WHITE)
        
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50))
        start_rect = start_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 50))
        
        screen.blit(title_text, title_rect)
        
        # Draw start button
        button_rect = pygame.Rect(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 - 25, 200, 50)
        pygame.draw.rect(screen, BLUE, button_rect)
        screen.blit(start_text, start_rect)
        
        # Draw instructions
        instructions = [
            "Controls:",
            "WASD/Arrow Keys - Move",
            "Space - Shoot",
            "R - Switch Weapon"
        ]
        
        y_pos = WINDOW_HEIGHT - 150
        for line in instructions:
            text = self.small_font.render(line, True, WHITE)
            text_rect = text.get_rect(center=(WINDOW_WIDTH//2, y_pos))
            screen.blit(text, text_rect)
            y_pos += 25
        
        return button_rect

    def draw_countdown(self):
        screen.fill(BLACK)
        time_elapsed = (pygame.time.get_ticks() - self.countdown_start) / 1000
        count = 4 - int(time_elapsed)
        if count > 0:
            count_text = self.font.render(str(count), True, WHITE)
            text_rect = count_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            screen.blit(count_text, text_rect)

    def draw_weapon_select_screen(self):
        screen.fill((20, 20, 40))  # Dark blue background
        
        # Draw title
        title = self.font.render("Select Your Weapon", True, WHITE)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, 50))
        screen.blit(title, title_rect)
        
        # Get list of weapons
        weapons = list(self.player.weapon_inventory.weapons.values())
        
        # Calculate layout
        start_y = 150
        spacing = 100
        
        # Draw weapon options
        for i, weapon in enumerate(weapons):
            # Create weapon selection box
            rect = pygame.Rect(WINDOW_WIDTH//4, start_y + i*spacing, WINDOW_WIDTH//2, 80)
            
            # Highlight selected weapon
            if i == self.selected_weapon_index:
                pygame.draw.rect(screen, (60, 60, 100), rect)  # Highlighted color
                pygame.draw.rect(screen, WHITE, rect, 2)  # White border
            else:
                pygame.draw.rect(screen, (40, 40, 80), rect)  # Normal color
            
            # Draw weapon name
            name = self.font.render(weapon.name, True, WHITE)
            name_rect = name.get_rect(center=(WINDOW_WIDTH//2, start_y + i*spacing + 20))
            screen.blit(name, name_rect)
            
            # Draw weapon stats
            stats_color = GOLD if i == self.selected_weapon_index else GRAY
            fire_rate = 1000 / weapon.fire_rate  # Convert to shots per second
            stats = self.small_font.render(
                f"Damage: {weapon.damage} | Fire Rate: {fire_rate:.1f}/s | Speed: {weapon.bullet_speed}",
                True, stats_color
            )
            stats_rect = stats.get_rect(center=(WINDOW_WIDTH//2, start_y + i*spacing + 50))
            screen.blit(stats, stats_rect)
        
        # Draw instructions at bottom
        instructions = [
            "↑/↓: Select Weapon",
            "SPACE: Confirm Selection"
        ]
        
        y_pos = WINDOW_HEIGHT - 80
        for instruction in instructions:
            text = self.small_font.render(instruction, True, WHITE)
            text_rect = text.get_rect(center=(WINDOW_WIDTH//2, y_pos))
            screen.blit(text, text_rect)
            y_pos += 30

    def draw(self):
        if self.in_weapon_select:
            self.draw_weapon_select_screen()
        elif self.in_countdown:
            self.draw_countdown()
            if pygame.time.get_ticks() - self.countdown_start >= 3000:
                self.in_countdown = False
                self.game_started = True
        elif not self.game_started and not self.in_countdown and not self.in_weapon_select:
            button_rect = self.draw_start_screen()
            pygame.display.flip()
            return button_rect
        elif self.game_started and not self.game_over:
            screen.fill(GRASS_GREEN)
            self.draw_hud()
            pygame.draw.line(screen, WHITE, (0, HUD_HEIGHT), (WINDOW_WIDTH, HUD_HEIGHT))
            
            if self.storm_started:
                pygame.draw.circle(screen, YELLOW, self.safe_zone_center, int(self.safe_zone_radius), 2)
            
            for bullet in self.bullets:
                bullet.draw()
            
            for particle in self.particles:
                particle.draw(screen)
            
            if self.player.alive:
                self.player.draw()
            
            for bot in self.bots:
                if bot.alive:
                    bot.draw()
            
            self.damage_numbers = [num for num in self.damage_numbers if num.update()]
            for damage_number in self.damage_numbers:
                damage_number.draw(screen)
            
            pygame.display.flip()
            return None  
        elif self.game_over:
            self.draw_game_over_screen()
            pygame.display.flip()
            return None  

    def draw_game_objects(self):
        screen.fill(GRASS_GREEN)
        
        for patch in self.terrain_patches:
            screen_pos = self.camera.apply(patch.x, patch.y)
            if (0 <= screen_pos[0] <= WINDOW_WIDTH and 
                HUD_HEIGHT <= screen_pos[1] <= WINDOW_HEIGHT):
                scaled_size = self.camera.apply_radius(patch.size)
                
                if patch.type == 'tree':
                    # Draw tree trunk
                    trunk_width = scaled_size // 3
                    trunk_height = scaled_size // 2
                    pygame.draw.rect(screen, BROWN, 
                                  (screen_pos[0] - trunk_width//2,
                                   screen_pos[1] - trunk_height//2,
                                   trunk_width, trunk_height))
                    # Draw tree top
                    pygame.draw.circle(screen, patch.color,
                                    (int(screen_pos[0]), int(screen_pos[1] - trunk_height//2)),
                                    int(scaled_size//2))
                else:
                    pygame.draw.circle(screen, patch.color,
                                    (int(screen_pos[0]), int(screen_pos[1])),
                                    int(scaled_size))
        
        if self.storm_started:
            screen_pos = self.camera.apply(self.safe_zone_center[0], self.safe_zone_center[1])
            scaled_radius = self.camera.apply_radius(self.safe_zone_radius)
            pygame.draw.circle(screen, YELLOW, (int(screen_pos[0]), int(screen_pos[1])), 
                            int(scaled_radius), 2)
        else:
            time_until_storm = max(0, 20 - (pygame.time.get_ticks() - self.storm_start_time) / 1000)
            if time_until_storm > 0:
                timer_text = self.font.render(f"Storm begins in: {int(time_until_storm)}s", True, YELLOW)
                text_rect = timer_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 30))
                screen.blit(timer_text, text_rect)
        
        for bullet in self.bullets:
            screen_pos = self.camera.apply(bullet.x, bullet.y)
            scaled_size = self.camera.apply_radius(bullet.size)
            pygame.draw.circle(screen, WHITE, (int(screen_pos[0]), int(screen_pos[1])), 
                            int(scaled_size))
        
        if self.player.alive:
            screen_pos = self.camera.apply(self.player.x, self.player.y)
            scaled_size = self.camera.apply_radius(PLAYER_SIZE)
            body_width = scaled_size - 4
            body_height = scaled_size + 4
            pygame.draw.rect(screen, self.player.color, 
                        (screen_pos[0] - body_width//2, 
                         screen_pos[1] - body_height//2, 
                         body_width, body_height))
            head_radius = scaled_size//3
            pygame.draw.circle(screen, self.player.color,
                          (int(screen_pos[0]), int(screen_pos[1] - body_height//2 - head_radius)),
                          head_radius)
        
        for bot in self.bots:
            if bot.alive:
                screen_pos = self.camera.apply(bot.x, bot.y)
                scaled_size = self.camera.apply_radius(BOT_SIZE)
                body_width = scaled_size - 4
                body_height = scaled_size + 4
                pygame.draw.rect(screen, bot.color, 
                            (screen_pos[0] - body_width//2,
                             screen_pos[1] - body_height//2,
                             body_width, body_height))
                head_radius = scaled_size//3
                pygame.draw.circle(screen, bot.color,
                              (int(screen_pos[0]), int(screen_pos[1] - body_height//2 - head_radius)),
                              head_radius)

    def shoot(self, shooter, target_x, target_y, current_time):
        if not shooter.alive or not shooter.weapon_inventory.current_weapon:
            return []

        weapon = shooter.weapon_inventory.current_weapon
        if current_time - shooter.last_shot_time < weapon.fire_rate:
            return []

        shooter.last_shot_time = current_time
        bullets = []

        dx = target_x - shooter.x
        dy = target_y - shooter.y
        length = math.sqrt(dx*dx + dy*dy)
        if length > 0:
            dx = dx/length
            dy = dy/length

        if weapon.name == "Shotgun":
            num_pellets = 5
            spread_angle = math.pi / 8  
            for i in range(num_pellets):
                angle = math.atan2(dy, dx) + random.uniform(-spread_angle, spread_angle)
                pellet_dx = math.cos(angle)
                pellet_dy = math.sin(angle)
                bullets.append(Bullet(
                    shooter.x, shooter.y,
                    pellet_dx, pellet_dy,
                    weapon.damage // num_pellets,  
                    weapon.bullet_speed,
                    weapon.bullet_size,
                    shooter,
                    isinstance(shooter, Bot)
                ))
        else:
            bullets.append(Bullet(
                shooter.x, shooter.y,
                dx, dy,
                weapon.damage,
                weapon.bullet_speed,
                weapon.bullet_size,
                shooter,
                isinstance(shooter, Bot)
            ))

        return bullets

    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            current_time = pygame.time.get_ticks()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game_over:
                        # Reset everything when clicking after game over
                        self.game_over = False
                        self.game_started = False
                        self.in_countdown = False
                        self.in_weapon_select = False
                        self.reset_game()
                    elif not self.game_started and not self.in_countdown and not self.in_weapon_select:
                        print("Start button clicked")
                        mouse_pos = pygame.mouse.get_pos()
                        button_rect = pygame.Rect(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 - 25, 200, 50)
                        if button_rect.collidepoint(mouse_pos):
                            print("Start button clicked in the rectangle. Entering weapon select.")
                            self.reset_game()
                            self.in_weapon_select = True
                elif event.type == pygame.KEYDOWN:
                    if self.in_weapon_select:
                        weapons = list(self.player.weapon_inventory.weapons.values())
                        if event.key == pygame.K_UP:
                            self.selected_weapon_index = (self.selected_weapon_index - 1) % len(weapons)
                        elif event.key == pygame.K_DOWN:
                            self.selected_weapon_index = (self.selected_weapon_index + 1) % len(weapons)
                        elif event.key == pygame.K_SPACE:
                            # Select weapon and start countdown
                            weapon_name = list(self.player.weapon_inventory.weapons.keys())[self.selected_weapon_index]
                            self.player.weapon_inventory.switch_weapon(weapon_name)
                            self.in_weapon_select = False
                            self.in_countdown = True
                            self.countdown_start = current_time
                    elif self.game_started and not self.game_over:
                        if event.key == pygame.K_SPACE:
                            # Shooting logic here...
                            if self.game_started and self.player.alive:
                                # Get the last movement direction
                                dx = 0
                                dy = 0
                                keys = pygame.key.get_pressed()
                                if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                                    dx = -1
                                if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                                    dx = 1
                                if keys[pygame.K_w] or keys[pygame.K_UP]:
                                    dy = -1
                                if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                                    dy = 1
                                
                                # If not moving, shoot in the last direction we were facing
                                if dx == 0 and dy == 0:
                                    if hasattr(self.player, 'facing_dx'):
                                        dx = self.player.facing_dx
                                        dy = self.player.facing_dy
                                    else:
                                        dx = 1  # Default to facing right
                                        dy = 0
                                
                                # Normalize the direction
                                length = math.sqrt(dx*dx + dy*dy)
                                if length > 0:
                                    dx = dx/length
                                    dy = dy/length
                                    
                                    # Store facing direction
                                    self.player.facing_dx = dx
                                    self.player.facing_dy = dy
                                    
                                    # Calculate target point in facing direction
                                    target_x = self.player.x + dx * 100
                                    target_y = self.player.y + dy * 100
                                    
                                    bullets = self.shoot(self.player, target_x, target_y, current_time)
                                    if bullets:
                                        self.bullets.extend(bullets)
                        elif event.key == pygame.K_w:
                            self.player.weapon_inventory.prev_weapon()
                        elif event.key == pygame.K_e:
                            self.player.weapon_inventory.next_weapon()

            if self.game_started and not self.game_over:
                # Handle movement
                keys = pygame.key.get_pressed()
                dx = 0
                dy = 0
                if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                    dx = -PLAYER_SPEED
                if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                    dx = PLAYER_SPEED
                if keys[pygame.K_w] or keys[pygame.K_UP]:
                    dy = -PLAYER_SPEED
                if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                    dy = PLAYER_SPEED
                
                # Store facing direction when moving
                if dx != 0 or dy != 0:
                    length = math.sqrt(dx*dx + dy*dy)
                    self.player.facing_dx = dx/length
                    self.player.facing_dy = dy/length
                
                # Normalize diagonal movement
                if dx != 0 and dy != 0:
                    dx *= 0.707  # 1/sqrt(2)
                    dy *= 0.707
                
                # Update player position
                if dx != 0 or dy != 0:
                    new_x = self.player.x + dx
                    new_y = self.player.y + dy
                    
                    # Keep player within bounds
                    self.player.x = max(0, min(new_x, MAP_WIDTH))
                    self.player.y = max(HUD_HEIGHT, min(new_y, MAP_HEIGHT))
                
                # Update camera to follow player
                self.camera.update(self.player.x, self.player.y)
                
                # Update game state
                self.update_bullets()
                self.update_safe_zone()
                self.check_zone_damage()
                self.update_particles()
                self.move_bots()
                
                # Draw everything
                screen.fill(GRASS_GREEN)
                self.draw_game_objects()
                self.draw_hud()
                
                # Draw storm timer if storm hasn't started
                if not self.storm_started:
                    time_until_storm = max(0, 20 - (current_time - self.storm_start_time) / 1000)
                    if time_until_storm > 0:
                        timer_text = self.font.render(f"Storm begins in: {int(time_until_storm)}s", True, YELLOW)
                        text_rect = timer_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 30))
                        screen.blit(timer_text, text_rect)
                
                # Draw damage numbers
                self.damage_numbers = [num for num in self.damage_numbers if num.update()]
                for damage_number in self.damage_numbers:
                    damage_number.draw(screen)
                
                # Check win/lose conditions
                alive_bots = len([bot for bot in self.bots if bot.alive])
                if alive_bots == 0 and self.player.alive:
                    self.game_over = True
                    self.victory = True
                elif not self.player.alive:
                    self.game_over = True
                    self.victory = False
                
                pygame.display.flip()
                clock.tick(60)
            
            elif self.game_over:
                self.draw_game_over_screen()
                pygame.display.flip()
                clock.tick(60)

            if self.in_countdown:
                self.draw_countdown()
                if current_time - self.countdown_start >= 3000:
                    self.in_countdown = False
                    self.game_started = True
                pygame.display.flip()
                clock.tick(60)

            if not self.game_started and not self.in_countdown and not self.in_weapon_select:
                button_rect = self.draw_start_screen()
                pygame.display.flip()
                clock.tick(60)

            if self.in_weapon_select:
                self.draw_weapon_select_screen()
                pygame.display.flip()
                clock.tick(60)

        pygame.quit()

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
if __name__ == "__main__":
    game = Game()
    game.run()
