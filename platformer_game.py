import pygame
import math
import sys
import random

# Initialize Pygame
pygame.init()

# Constants - back to original resolution
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 150, 255)
RED = (255, 100, 100)
GREEN = (100, 255, 100)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
YELLOW = (255, 255, 100)
PURPLE = (200, 100, 255)

# Physics constants
GRAVITY = 0.8
JUMP_STRENGTH = -15
PLAYER_SPEED = 5
PLATFORM_FADE_TIME = 5000  # 5 seconds in milliseconds
MOVING_PLATFORM_SPEED = 1
SPIKE_DAMAGE_COOLDOWN = 1000  # 1 second cooldown between spike damage

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 40
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.color = BLUE
        self.last_spike_damage = 0
        self.score = 0
        
        # Animation properties
        self.animation_frame = 0
        self.animation_speed = 0.2
        self.facing_right = True
        self.is_walking = False
        self.jump_animation = 0
        
    def update(self, platforms, screen_width, screen_height, spikes=None, collectibles=None, disappearing_platforms=None):
        # Handle input
        keys = pygame.key.get_pressed()
        self.vel_x = 0
        self.is_walking = False
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -PLAYER_SPEED
            self.facing_right = False
            self.is_walking = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = PLAYER_SPEED
            self.facing_right = True
            self.is_walking = True
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False
            self.jump_animation = 1.0
        
        # Update animations
        if self.is_walking and self.on_ground:
            self.animation_frame += self.animation_speed
        else:
            self.animation_frame = 0
            
        # Jump animation decay
        if self.jump_animation > 0:
            self.jump_animation -= 0.05
        
        # Apply gravity
        self.vel_y += GRAVITY
        
        # Store old position for moving platform detection
        old_x = self.x
        
        # Update position
        self.x += self.vel_x
        self.y += self.vel_y
        
        # Check collisions with platforms
        self.on_ground = False
        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        for platform in platforms:
            if platform.active and player_rect.colliderect(platform.rect):
                # Trigger disappearing platforms
                if isinstance(platform, DisappearingPlatform):
                    platform.trigger()
                
                # Landing on top of platform
                if self.vel_y > 0 and self.y < platform.rect.top:
                    self.y = platform.rect.top - self.height
                    self.vel_y = 0
                    self.on_ground = True
                    
                    # Move with moving platforms
                    if isinstance(platform, MovingPlatform):
                        platform_movement = platform.speed * platform.direction
                        self.x += platform_movement
                        
                # Hitting platform from below
                elif self.vel_y < 0 and self.y > platform.rect.bottom:
                    self.y = platform.rect.bottom
                    self.vel_y = 0
                # Hitting platform from the side
                else:
                    if self.vel_x > 0:  # Moving right
                        self.x = platform.rect.left - self.width
                    elif self.vel_x < 0:  # Moving left
                        self.x = platform.rect.right
        
        # Check spike collisions
        if spikes:
            current_time = pygame.time.get_ticks()
            for spike in spikes:
                if player_rect.colliderect(spike.rect):
                    if current_time - self.last_spike_damage > SPIKE_DAMAGE_COOLDOWN:
                        self.last_spike_damage = current_time
                        # Reset player position on spike hit
                        self.reset_position(screen_height)
                        break
        
        # Check collectible collisions
        if collectibles:
            for collectible in collectibles:
                if not collectible.collected and player_rect.colliderect(collectible.rect):
                    collectible.collected = True
                    self.score += 10
        
        # Keep player on screen
        if self.x < 0:
            self.x = 0
        elif self.x > screen_width - self.width:
            self.x = screen_width - self.width
        
        # Reset if player falls off screen
        if self.y > screen_height:
            self.reset_position(screen_height)
    
    def reset_position(self, screen_height=SCREEN_HEIGHT):
        self.x = 50
        self.y = screen_height - 200
        self.vel_x = 0
        self.vel_y = 0
    
    def draw(self, screen):
        # Calculate animation offsets
        walk_bounce = 0
        if self.is_walking and self.on_ground:
            walk_bounce = math.sin(self.animation_frame * 3) * 2
        
        jump_stretch = 0
        if self.jump_animation > 0:
            jump_stretch = self.jump_animation * 3
        
        # Body position with animation
        body_x = self.x
        body_y = self.y + walk_bounce
        body_width = self.width
        body_height = self.height + jump_stretch
        
        # Draw main body - rounded rectangle for friendlier look
        body_rect = pygame.Rect(body_x + 2, body_y + 5, body_width - 4, body_height - 8)
        pygame.draw.rect(screen, self.color, body_rect)
        pygame.draw.rect(screen, (60, 100, 180), body_rect, 2)
        
        # Draw head - larger and rounder
        head_size = 18
        head_x = body_x + body_width // 2
        head_y = body_y + head_size // 2 + 2
        pygame.draw.circle(screen, (120, 160, 255), (int(head_x), int(head_y)), head_size // 2)
        pygame.draw.circle(screen, (80, 120, 200), (int(head_x), int(head_y)), head_size // 2, 2)
        
        # Draw cheerful eyes - bigger and more expressive
        eye_size = 3
        eye_y = head_y - 2
        
        if self.facing_right:
            # Eyes looking right with happy expression
            left_eye_x = head_x - 5
            right_eye_x = head_x + 2
            
            # Eye whites
            pygame.draw.circle(screen, WHITE, (int(left_eye_x), int(eye_y)), eye_size + 1)
            pygame.draw.circle(screen, WHITE, (int(right_eye_x), int(eye_y)), eye_size + 1)
            
            # Pupils looking right
            pygame.draw.circle(screen, BLACK, (int(left_eye_x + 1), int(eye_y)), eye_size - 1)
            pygame.draw.circle(screen, BLACK, (int(right_eye_x + 1), int(eye_y)), eye_size - 1)
            
            # Eye highlights for life
            pygame.draw.circle(screen, WHITE, (int(left_eye_x + 1), int(eye_y - 1)), 1)
            pygame.draw.circle(screen, WHITE, (int(right_eye_x + 1), int(eye_y - 1)), 1)
        else:
            # Eyes looking left with happy expression
            left_eye_x = head_x - 2
            right_eye_x = head_x + 5
            
            # Eye whites
            pygame.draw.circle(screen, WHITE, (int(left_eye_x), int(eye_y)), eye_size + 1)
            pygame.draw.circle(screen, WHITE, (int(right_eye_x), int(eye_y)), eye_size + 1)
            
            # Pupils looking left
            pygame.draw.circle(screen, BLACK, (int(left_eye_x - 1), int(eye_y)), eye_size - 1)
            pygame.draw.circle(screen, BLACK, (int(right_eye_x - 1), int(eye_y)), eye_size - 1)
            
            # Eye highlights for life
            pygame.draw.circle(screen, WHITE, (int(left_eye_x - 1), int(eye_y - 1)), 1)
            pygame.draw.circle(screen, WHITE, (int(right_eye_x - 1), int(eye_y - 1)), 1)
        
        # Draw a big happy smile
        smile_y = head_y + 4
        smile_width = 10
        smile_rect = pygame.Rect(head_x - smile_width // 2, smile_y, smile_width, 6)
        pygame.draw.arc(screen, BLACK, smile_rect, 0, math.pi, 2)
        
        # Add rosy cheeks for extra friendliness
        cheek_color = (255, 200, 200)
        pygame.draw.circle(screen, cheek_color, (int(head_x - 8), int(head_y + 1)), 3)
        pygame.draw.circle(screen, cheek_color, (int(head_x + 8), int(head_y + 1)), 3)
        
        # Draw arms with animation - more visible and friendly
        arm_swing = 0
        if self.is_walking and self.on_ground:
            arm_swing = math.sin(self.animation_frame * 3) * 4
        
        arm_color = (100, 140, 220)
        
        # Left arm
        left_arm_x = body_x + 3
        left_arm_y = body_y + 15 + arm_swing
        pygame.draw.circle(screen, arm_color, (int(left_arm_x), int(left_arm_y)), 4)
        pygame.draw.circle(screen, (80, 120, 200), (int(left_arm_x), int(left_arm_y)), 4, 1)
        
        # Right arm
        right_arm_x = body_x + body_width - 3
        right_arm_y = body_y + 15 - arm_swing
        pygame.draw.circle(screen, arm_color, (int(right_arm_x), int(right_arm_y)), 4)
        pygame.draw.circle(screen, (80, 120, 200), (int(right_arm_x), int(right_arm_y)), 4, 1)
        
        # Draw legs with walking animation - more prominent
        leg_offset = 0
        if self.is_walking and self.on_ground:
            leg_offset = math.sin(self.animation_frame * 3) * 3
        
        leg_color = (80, 120, 200)
        
        # Left leg
        left_leg_x = body_x + 8 + leg_offset
        left_leg_y = body_y + body_height - 2
        pygame.draw.circle(screen, leg_color, (int(left_leg_x), int(left_leg_y)), 5)
        
        # Right leg  
        right_leg_x = body_x + body_width - 8 - leg_offset
        right_leg_y = body_y + body_height - 2
        pygame.draw.circle(screen, leg_color, (int(right_leg_x), int(right_leg_y)), 5)
        
        # Add little feet
        foot_color = (60, 100, 180)
        pygame.draw.ellipse(screen, foot_color, (left_leg_x - 3, left_leg_y + 3, 6, 4))
        pygame.draw.ellipse(screen, foot_color, (right_leg_x - 3, right_leg_y + 3, 6, 4))

class Platform:
    def __init__(self, x, y, width, height, temporary=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.temporary = temporary
        self.active = True
        self.creation_time = pygame.time.get_ticks() if temporary else 0
        self.color = PURPLE if temporary else GRAY
        
    def update(self):
        if self.temporary and self.active:
            current_time = pygame.time.get_ticks()
            if current_time - self.creation_time > PLATFORM_FADE_TIME:
                self.active = False
    
    def draw(self, screen):
        if self.active:
            alpha = 255
            if self.temporary:
                # Fade out effect in the last second
                current_time = pygame.time.get_ticks()
                time_left = PLATFORM_FADE_TIME - (current_time - self.creation_time)
                if time_left < 1000:  # Last second
                    alpha = int(255 * (time_left / 1000))
            
            # Create surface with alpha for fading effect
            surf = pygame.Surface((self.rect.width, self.rect.height))
            surf.set_alpha(alpha)
            surf.fill(self.color)
            screen.blit(surf, self.rect)
            
            # Draw sketch-like border with slightly rough edges
            pygame.draw.rect(screen, BLACK, self.rect, 2)
            # Add inner highlight for depth
            if self.rect.width > 4 and self.rect.height > 4:
                inner_rect = pygame.Rect(self.rect.x + 1, self.rect.y + 1, 
                                       self.rect.width - 2, self.rect.height - 2)
                pygame.draw.rect(screen, (255, 255, 255, 100), inner_rect, 1)

class MovingPlatform(Platform):
    def __init__(self, x, y, width, height, start_x, end_x, speed=MOVING_PLATFORM_SPEED):
        super().__init__(x, y, width, height)
        self.start_x = start_x
        self.end_x = end_x
        self.speed = speed
        self.direction = 1
        self.color = (150, 150, 255)  # Light blue for moving platforms
        
    def update(self):
        # Move platform back and forth
        self.rect.x += self.speed * self.direction
        
        # Reverse direction at boundaries
        if self.rect.x <= self.start_x or self.rect.x >= self.end_x:
            self.direction *= -1
            
    def draw(self, screen):
        if self.active:
            pygame.draw.rect(screen, self.color, self.rect)
            pygame.draw.rect(screen, BLACK, self.rect, 2)
            # Add arrows to show movement direction
            center_x = self.rect.centerx
            center_y = self.rect.centery
            if self.direction > 0:
                # Right arrow
                pygame.draw.polygon(screen, BLACK, [
                    (center_x + 5, center_y),
                    (center_x - 5, center_y - 5),
                    (center_x - 5, center_y + 5)
                ])
            else:
                # Left arrow
                pygame.draw.polygon(screen, BLACK, [
                    (center_x - 5, center_y),
                    (center_x + 5, center_y - 5),
                    (center_x + 5, center_y + 5)
                ])

class Spike:
    def __init__(self, x, y, width=30, height=20):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (255, 50, 50)  # Red spikes
        
    def draw(self, screen):
        # Draw spikes as triangles
        num_spikes = self.rect.width // 10
        spike_width = self.rect.width // num_spikes
        
        for i in range(num_spikes):
            spike_x = self.rect.x + i * spike_width
            points = [
                (spike_x, self.rect.bottom),
                (spike_x + spike_width, self.rect.bottom),
                (spike_x + spike_width // 2, self.rect.top)
            ]
            pygame.draw.polygon(screen, self.color, points)
            pygame.draw.polygon(screen, BLACK, points, 2)

class Collectible:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.collected = False
        self.animation_offset = 0
        self.color = (255, 215, 0)  # Gold
        
    def update(self):
        self.animation_offset += 0.2
        
    def draw(self, screen):
        if not self.collected:
            # Floating animation
            float_y = self.rect.y + math.sin(self.animation_offset) * 3
            # Draw as a diamond
            center_x = self.rect.centerx
            center_y = float_y + self.rect.height // 2
            points = [
                (center_x, center_y - 10),
                (center_x + 8, center_y),
                (center_x, center_y + 10),
                (center_x - 8, center_y)
            ]
            pygame.draw.polygon(screen, self.color, points)
            pygame.draw.polygon(screen, BLACK, points, 2)

class DisappearingPlatform(Platform):
    def __init__(self, x, y, width, height, trigger_delay=2000, disappear_time=3000):
        super().__init__(x, y, width, height)
        self.triggered = False
        self.trigger_time = 0
        self.trigger_delay = trigger_delay  # Time before disappearing
        self.disappear_time = disappear_time  # How long it stays gone
        self.original_active = True
        self.color = (255, 200, 100)  # Orange
        
    def trigger(self):
        if not self.triggered:
            self.triggered = True
            self.trigger_time = pygame.time.get_ticks()
            
    def update(self):
        if self.triggered:
            current_time = pygame.time.get_ticks()
            time_since_trigger = current_time - self.trigger_time
            
            if time_since_trigger > self.trigger_delay and time_since_trigger < self.trigger_delay + self.disappear_time:
                self.active = False
            else:
                self.active = True
                # Reset trigger state when platform reappears so it can be triggered again
                if time_since_trigger >= self.trigger_delay + self.disappear_time:
                    self.triggered = False
                
    def draw(self, screen):
        if self.active:
            # Flash warning when about to disappear
            alpha = 255
            if self.triggered:
                current_time = pygame.time.get_ticks()
                time_since_trigger = current_time - self.trigger_time
                if time_since_trigger < self.trigger_delay:
                    # Flash faster as disappear time approaches
                    flash_speed = max(1, self.trigger_delay - time_since_trigger) / 200
                    alpha = int(128 + 127 * math.sin(current_time * flash_speed / 100))
            
            surf = pygame.Surface((self.rect.width, self.rect.height))
            surf.set_alpha(alpha)
            surf.fill(self.color)
            screen.blit(surf, self.rect)
            pygame.draw.rect(screen, BLACK, self.rect, 2)

class Goal:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.animation_offset = 0
        
    def update(self):
        self.animation_offset += 0.1
        
    def draw(self, screen):
        # Animated goal with floating effect
        float_y = self.y + math.sin(self.animation_offset) * 5
        pygame.draw.rect(screen, YELLOW, (self.x, float_y, self.width, self.height))
        pygame.draw.rect(screen, BLACK, (self.x, float_y, self.width, self.height), 3)
        
        # Draw star inside
        center_x = self.x + self.width // 2
        center_y = float_y + self.height // 2
        star_points = []
        for i in range(10):
            angle = i * math.pi / 5
            if i % 2 == 0:
                radius = 12
            else:
                radius = 6
            x = center_x + radius * math.cos(angle - math.pi / 2)
            y = center_y + radius * math.sin(angle - math.pi / 2)
            star_points.append((x, y))
        
        pygame.draw.polygon(screen, RED, star_points)

class DrawingSystem:
    def __init__(self):
        self.drawing = False
        self.start_pos = None
        self.current_pos = None
        self.min_platform_length = 30
        
    def start_drawing(self, pos):
        self.drawing = True
        self.start_pos = pos
        self.current_pos = pos
        
    def update_drawing(self, pos):
        if self.drawing:
            self.current_pos = pos
            
    def finish_drawing(self):
        if self.drawing and self.start_pos and self.current_pos:
            # Calculate platform dimensions
            x1, y1 = self.start_pos
            x2, y2 = self.current_pos
            
            # Make sure platform is horizontal-ish and long enough
            distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            if distance >= self.min_platform_length:
                # Create platform from start to end position
                left = min(x1, x2)
                right = max(x1, x2)
                top = min(y1, y2)
                
                platform = Platform(left, top, right - left, 10, temporary=True)
                self.drawing = False
                self.start_pos = None
                self.current_pos = None
                return platform
        
        self.drawing = False
        self.start_pos = None
        self.current_pos = None
        return None
        
    def draw_preview(self, screen):
        if self.drawing and self.start_pos and self.current_pos:
            # Calculate platform dimensions
            distance = math.sqrt((self.current_pos[0] - self.start_pos[0]) ** 2 + 
                               (self.current_pos[1] - self.start_pos[1]) ** 2)
            
            if distance < self.min_platform_length:
                color = RED
                line_width = 3
            else:
                color = GREEN
                line_width = 8
            
            # Draw sketch-like preview line with dashed effect
            pygame.draw.line(screen, color, self.start_pos, self.current_pos, line_width)
            
            # Add dotted line effect for sketch feel
            if distance >= self.min_platform_length:
                # Draw small marks along the line to show it will become a platform
                steps = int(distance / 20)
                for i in range(steps):
                    t = i / max(steps - 1, 1)
                    x = int(self.start_pos[0] + t * (self.current_pos[0] - self.start_pos[0]))
                    y = int(self.start_pos[1] + t * (self.current_pos[1] - self.start_pos[1]))
                    pygame.draw.circle(screen, PURPLE, (x, y), 2)
            
            # Draw endpoint indicators
            pygame.draw.circle(screen, color, self.start_pos, 5)
            pygame.draw.circle(screen, color, self.current_pos, 5)

class LevelGenerator:
    def __init__(self):
        self.level_types = ['horizontal_gaps', 'vertical_climb', 'mixed_challenge', 'maze_like', 'timing_challenge', 'moving_platforms', 'spike_gauntlet', 'disappearing_challenge']
        self.level_type_names = {
            'horizontal_gaps': 'Horizontal Gaps',
            'vertical_climb': 'Vertical Climb', 
            'mixed_challenge': 'Mixed Challenge',
            'maze_like': 'Maze Navigation',
            'timing_challenge': 'Timing Challenge',
            'moving_platforms': 'Moving Platforms',
            'spike_gauntlet': 'Spike Gauntlet',
            'disappearing_challenge': 'Disappearing Platforms'
        }
        self.last_level_type = 'Horizontal Gaps'
        
    def generate_level(self, level_num):
        """Generate a random level based on the level number for progressive difficulty"""
        platforms = []
        moving_platforms = []
        spikes = []
        collectibles = []
        disappearing_platforms = []
        goals = []
        
        # Always add ground platform
        platforms.append(Platform(0, SCREEN_HEIGHT - 50, 200, 50))
        
        # Determine difficulty based on level number
        difficulty = min(level_num, 10)  # Cap difficulty at level 10
        max_platforms = 2 + (difficulty // 2)  # Increase drawable platforms with difficulty
        
        # Choose level type based on level number and randomness
        if level_num <= 3:
            # First few levels are more structured
            level_type = ['horizontal_gaps', 'vertical_climb', 'mixed_challenge'][level_num - 1]
        else:
            # Random level types for higher levels, including new types
            level_type = random.choice(self.level_types)
        
        # Store for UI display
        self.last_level_type = self.level_type_names[level_type]
        
        if level_type == 'horizontal_gaps':
            platforms.extend(self._generate_horizontal_gaps(difficulty))
        elif level_type == 'vertical_climb':
            platforms.extend(self._generate_vertical_climb(difficulty))
        elif level_type == 'mixed_challenge':
            platforms.extend(self._generate_mixed_challenge(difficulty))
        elif level_type == 'maze_like':
            platforms.extend(self._generate_maze_like(difficulty))
        elif level_type == 'timing_challenge':
            platforms.extend(self._generate_timing_challenge(difficulty))
        elif level_type == 'moving_platforms':
            platforms.extend(self._generate_basic_platforms(difficulty))
            moving_platforms.extend(self._generate_moving_platforms(difficulty))
        elif level_type == 'spike_gauntlet':
            platforms.extend(self._generate_spike_level(difficulty))
            spikes.extend(self._generate_spikes(difficulty))
        elif level_type == 'disappearing_challenge':
            platforms.extend(self._generate_basic_platforms(difficulty))
            disappearing_platforms.extend(self._generate_disappearing_platforms(difficulty))
        
        # Add goal at a challenging but reachable position
        goal_x, goal_y = self._find_goal_position(platforms + moving_platforms + disappearing_platforms, difficulty)
        goals.append(Goal(goal_x, goal_y))
        
        # Add some collectibles randomly, avoiding goal position
        if random.random() < 0.6:  # 60% chance of collectibles
            collectibles.extend(self._generate_collectibles(platforms + moving_platforms, difficulty, (goal_x, goal_y)))
        
        return platforms, moving_platforms, spikes, collectibles, disappearing_platforms, goals, max_platforms
    
    def _generate_horizontal_gaps(self, difficulty):
        """Generate level with horizontal gaps to jump across"""
        platforms = []
        
        # Create gaps of varying sizes
        num_gaps = 2 + difficulty // 2
        gap_size = 150 + random.randint(0, 100 + difficulty * 10)
        
        current_x = 250
        for i in range(num_gaps):
            # Add platform before gap
            platform_width = 80 + random.randint(0, 40)
            platform_height = SCREEN_HEIGHT - 150 - random.randint(0, 100)
            platforms.append(Platform(current_x, platform_height, platform_width, 20))
            
            current_x += platform_width + gap_size
            gap_size = 120 + random.randint(0, 80 + difficulty * 15)
            
            if current_x > SCREEN_WIDTH - 200:
                break
        
        # Add final platform near the end
        if current_x < SCREEN_WIDTH - 150:
            platforms.append(Platform(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 200 - random.randint(0, 100), 100, 20))
        
        return platforms
    
    def _generate_vertical_climb(self, difficulty):
        """Generate level requiring vertical climbing"""
        platforms = []
        
        num_levels = 3 + difficulty // 2
        current_y = SCREEN_HEIGHT - 150
        
        for i in range(num_levels):
            # Alternate sides for zigzag climbing
            if i % 2 == 0:
                x = 100 + random.randint(0, 200)
            else:
                x = SCREEN_WIDTH - 300 + random.randint(0, 200)
            
            width = 80 + random.randint(0, 60)
            platforms.append(Platform(x, current_y, width, 20))
            
            current_y -= 120 + random.randint(20, 60)
            
            if current_y < 100:
                break
        
        return platforms
    
    def _generate_mixed_challenge(self, difficulty):
        """Generate level with both horizontal and vertical challenges"""
        platforms = []
        
        # Start with some horizontal platforms
        platforms.extend(self._generate_horizontal_gaps(difficulty // 2 + 1)[:2])
        
        # Add vertical section
        start_x = SCREEN_WIDTH // 2 + random.randint(-100, 100)
        current_y = SCREEN_HEIGHT - 200
        
        for i in range(2 + difficulty // 3):
            x = start_x + random.randint(-80, 80)
            width = 60 + random.randint(0, 40)
            platforms.append(Platform(x, current_y, width, 20))
            current_y -= 100 + random.randint(20, 40)
        
        return platforms
    
    def _generate_maze_like(self, difficulty):
        """Generate level with maze-like platform arrangement"""
        platforms = []
        
        # Create a grid-like structure with some platforms missing
        grid_width = 8
        grid_height = 6
        cell_width = SCREEN_WIDTH // grid_width
        cell_height = (SCREEN_HEIGHT - 100) // grid_height
        
        # Randomly place platforms in grid
        for row in range(1, grid_height):
            for col in range(1, grid_width - 1):
                if random.random() < 0.4 + (difficulty * 0.05):  # More platforms with higher difficulty
                    x = col * cell_width + random.randint(10, cell_width - 90)
                    y = SCREEN_HEIGHT - 100 - (row * cell_height)
                    width = 60 + random.randint(0, 30)
                    platforms.append(Platform(x, y, width, 20))
        
        return platforms
    
    def _generate_timing_challenge(self, difficulty):
        """Generate level that requires precise timing and platform usage"""
        platforms = []
        
        # Create platforms that require strategic drawing
        num_sections = 2 + difficulty // 2
        section_width = SCREEN_WIDTH // num_sections
        
        for i in range(num_sections):
            section_start = i * section_width + 50
            
            # Add one or two platforms per section at different heights
            for j in range(1 + random.randint(0, 1)):
                x = section_start + random.randint(0, section_width - 100)
                y = SCREEN_HEIGHT - 150 - random.randint(0, 200)
                width = 60 + random.randint(0, 40)
                platforms.append(Platform(x, y, width, 20))
        
        return platforms
    
    def _find_goal_position(self, platforms, difficulty):
        """Find a good position for the goal based on existing platforms"""
        # Try to place goal on or near the highest/furthest platform
        if not platforms:
            return SCREEN_WIDTH - 100, SCREEN_HEIGHT - 200
        
        # Find the platform that's furthest right and reasonably high
        best_platform = None
        best_score = 0
        
        for platform in platforms[1:]:  # Skip ground platform
            # Score based on distance from start and height
            distance_score = platform.rect.x / SCREEN_WIDTH
            height_score = (SCREEN_HEIGHT - platform.rect.y) / SCREEN_HEIGHT
            total_score = distance_score + height_score
            
            if total_score > best_score:
                best_score = total_score
                best_platform = platform
        
        if best_platform:
            goal_x = best_platform.rect.x + best_platform.rect.width // 2 - 20
            goal_y = best_platform.rect.y - 60
        else:
            goal_x = SCREEN_WIDTH - 100
            goal_y = SCREEN_HEIGHT - 200
        
        return goal_x, goal_y
    
    def _generate_basic_platforms(self, difficulty):
        """Generate basic platforms for levels with special elements"""
        platforms = []
        
        num_platforms = 3 + difficulty // 2
        section_width = SCREEN_WIDTH // (num_platforms + 1)
        
        for i in range(num_platforms):
            x = (i + 1) * section_width + random.randint(-50, 50)
            y = SCREEN_HEIGHT - 150 - random.randint(0, 100)
            width = 80 + random.randint(0, 40)
            platforms.append(Platform(x, y, width, 20))
            
        return platforms
    
    def _generate_moving_platforms(self, difficulty):
        """Generate moving platforms"""
        moving_platforms = []
        
        num_moving = 2 + difficulty // 3
        
        for i in range(num_moving):
            # Random position and movement range
            center_x = 200 + random.randint(0, SCREEN_WIDTH - 400)
            y = SCREEN_HEIGHT - 200 - random.randint(0, 200)
            movement_range = 100 + random.randint(0, 150)
            
            start_x = max(50, center_x - movement_range // 2)
            end_x = min(SCREEN_WIDTH - 150, center_x + movement_range // 2)
            
            speed = MOVING_PLATFORM_SPEED + random.uniform(0, 1)
            
            moving_platforms.append(MovingPlatform(start_x, y, 100, 20, start_x, end_x, speed))
            
        return moving_platforms
    
    def _generate_spike_level(self, difficulty):
        """Generate platforms for spike gauntlet levels"""
        platforms = []
        
        # Create safe platforms above spike areas
        num_safe_zones = 3 + difficulty // 2
        section_width = SCREEN_WIDTH // num_safe_zones
        
        for i in range(num_safe_zones):
            x = i * section_width + random.randint(20, section_width - 120)
            y = SCREEN_HEIGHT - 200 - random.randint(0, 100)
            width = 80 + random.randint(0, 40)
            platforms.append(Platform(x, y, width, 20))
            
        return platforms
    
    def _generate_spikes(self, difficulty):
        """Generate spike traps"""
        spikes = []
        
        # Add spikes on ground level
        num_spike_areas = 2 + difficulty // 2
        spike_width = 60 + random.randint(0, 40)
        
        for i in range(num_spike_areas):
            x = 250 + i * 200 + random.randint(-50, 50)
            if x + spike_width < SCREEN_WIDTH - 100:
                spikes.append(Spike(x, SCREEN_HEIGHT - 70, spike_width))
                
        # Add some elevated spikes
        if difficulty > 3:
            for i in range(difficulty // 3):
                x = random.randint(100, SCREEN_WIDTH - 150)
                y = SCREEN_HEIGHT - 150 - random.randint(0, 100)
                spikes.append(Spike(x, y, 40))
                
        return spikes
    
    def _generate_disappearing_platforms(self, difficulty):
        """Generate disappearing platforms"""
        disappearing_platforms = []
        
        num_disappearing = 2 + difficulty // 3
        
        for i in range(num_disappearing):
            x = 300 + i * 200 + random.randint(-50, 50)
            y = SCREEN_HEIGHT - 200 - random.randint(0, 150)
            width = 80 + random.randint(0, 40)
            
            # Vary timing based on difficulty
            trigger_delay = max(1000, 3000 - difficulty * 200)
            disappear_time = 2000 + random.randint(0, 1000)
            
            disappearing_platforms.append(DisappearingPlatform(x, y, width, 20, trigger_delay, disappear_time))
            
        return disappearing_platforms
    
    def _generate_collectibles(self, platforms, difficulty, goal_position=None):
        """Generate collectible items, avoiding goal position"""
        collectibles = []
        
        num_collectibles = 1 + difficulty // 3
        
        for i in range(num_collectibles):
            # Place collectibles near platforms
            if platforms:
                attempts = 0
                max_attempts = 10
                
                while attempts < max_attempts:
                    platform = random.choice(platforms[1:])  # Skip ground platform
                    x = platform.rect.x + random.randint(10, platform.rect.width - 30)
                    y = platform.rect.y - 30
                    
                    # Check if collectible would be too close to goal
                    if goal_position:
                        goal_x, goal_y = goal_position
                        distance = math.sqrt((x - goal_x) ** 2 + (y - goal_y) ** 2)
                        if distance > 80:  # Minimum distance from goal
                            collectibles.append(Collectible(x, y))
                            break
                    else:
                        collectibles.append(Collectible(x, y))
                        break
                    
                    attempts += 1
                
        return collectibles

class Game:
    def __init__(self):
        # Use original resolution for proper game scaling
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.fullscreen = False
            
        pygame.display.set_caption("Draw Platform Puzzler - Infinite Levels")
        self.clock = pygame.time.Clock()
        
        # Game objects
        self.player = Player(50, self.screen_height - 200)
        self.drawing_system = DrawingSystem()
        self.level_generator = LevelGenerator()
        self.current_level = 1
        self.max_platforms = 3
        
        # Initialize all lists
        self.platforms = []
        self.moving_platforms = []
        self.spikes = []
        self.collectibles = []
        self.disappearing_platforms = []
        self.drawn_platforms = []
        self.goals = []
        
        # Initialize level
        self.load_level(self.current_level)
        
    def load_level(self, level_num):
        """Load a randomly generated level"""
        self.platforms = []
        self.moving_platforms = []
        self.spikes = []
        self.collectibles = []
        self.disappearing_platforms = []
        self.drawn_platforms = []
        self.goals = []
        
        # Generate random level
        platforms, moving_platforms, spikes, collectibles, disappearing_platforms, goals, max_platforms = self.level_generator.generate_level(level_num)
        
        self.platforms = platforms
        self.moving_platforms = moving_platforms
        self.spikes = spikes
        self.collectibles = collectibles
        self.disappearing_platforms = disappearing_platforms
        self.goals = goals
        self.max_platforms = max_platforms
        
        # Store level type for UI display
        if level_num <= 3:
            level_types = ['Horizontal Gaps', 'Vertical Climb', 'Mixed Challenge']
            self.current_level_type = level_types[level_num - 1]
        else:
            # Get the last generated level type
            self.current_level_type = self.level_generator.last_level_type
        
        # Reset player position
        self.player.reset_position()
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Exit fullscreen/quit game
                    return False
                elif event.key == pygame.K_F11:
                    # Toggle fullscreen
                    self.toggle_fullscreen()
                elif event.key == pygame.K_r:
                    # Reset level
                    self.load_level(self.current_level)
                elif event.key == pygame.K_n and len(self.drawn_platforms) < self.max_platforms:
                    # Clear all drawn platforms (for testing)
                    self.drawn_platforms.clear()
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and len(self.drawn_platforms) < self.max_platforms:  # Left click
                    self.drawing_system.start_drawing(event.pos)
                    
            elif event.type == pygame.MOUSEMOTION:
                self.drawing_system.update_drawing(event.pos)
                
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left click release
                    new_platform = self.drawing_system.finish_drawing()
                    if new_platform and len(self.drawn_platforms) < self.max_platforms:
                        self.drawn_platforms.append(new_platform)
        
        return True
    
    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode"""
        if self.fullscreen:
            # Switch to windowed mode - back to original resolution
            self.screen_width = SCREEN_WIDTH
            self.screen_height = SCREEN_HEIGHT
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
            self.fullscreen = False
        else:
            # Switch to fullscreen - use current screen resolution
            info = pygame.display.Info()
            self.screen_width = info.current_w
            self.screen_height = info.current_h
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
            self.fullscreen = True
        
    def update(self):
        # Update all platforms
        all_platforms = self.platforms + self.drawn_platforms + self.moving_platforms + self.disappearing_platforms
        for platform in all_platforms:
            platform.update()
        
        # Update collectibles
        for collectible in self.collectibles:
            collectible.update()
        
        # Remove inactive drawn platforms
        self.drawn_platforms = [p for p in self.drawn_platforms if p.active]
        
        # Update player
        self.player.update(all_platforms, self.screen_width, self.screen_height, self.spikes, self.collectibles, self.disappearing_platforms)
        
        # Update goals
        for goal in self.goals:
            goal.update()
            
        # Check goal collision
        player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
        for goal in self.goals:
            if player_rect.colliderect(goal.rect):
                self.current_level += 1
                self.load_level(self.current_level)
                break
        
    def draw_grid_background(self):
        """Draw a sketch pad grid background with better visibility"""
        grid_size = 40
        grid_color = (220, 220, 220)  # Darker gray for better visibility
        
        # Draw vertical lines
        for x in range(0, self.screen_width, grid_size):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, self.screen_height), 1)
        
        # Draw horizontal lines
        for y in range(0, self.screen_height, grid_size):
            pygame.draw.line(self.screen, grid_color, (0, y), (self.screen_width, y), 1)
            
        # Add thicker lines every 5 grid squares for better structure
        major_grid_color = (200, 200, 200)
        major_grid_size = grid_size * 5
        
        # Major vertical lines
        for x in range(0, self.screen_width, major_grid_size):
            pygame.draw.line(self.screen, major_grid_color, (x, 0), (x, self.screen_height), 2)
        
        # Major horizontal lines
        for y in range(0, self.screen_height, major_grid_size):
            pygame.draw.line(self.screen, major_grid_color, (0, y), (self.screen_width, y), 2)
    
    def draw(self):
        # Fill with white background
        self.screen.fill(WHITE)
        
        # Draw grid background
        self.draw_grid_background()
        
        # Draw platforms
        for platform in self.platforms + self.drawn_platforms + self.moving_platforms + self.disappearing_platforms:
            platform.draw(self.screen)
        
        # Draw spikes
        for spike in self.spikes:
            spike.draw(self.screen)
        
        # Draw collectibles
        for collectible in self.collectibles:
            collectible.draw(self.screen)
        
        # Draw goals
        for goal in self.goals:
            goal.draw(self.screen)
        
        # Draw player
        self.player.draw(self.screen)
        
        # Draw drawing preview
        self.drawing_system.draw_preview(self.screen)
        
        # Draw UI
        self.draw_ui()
        
        pygame.display.flip()
        
    def draw_ui(self):
        font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 20)  # Smaller font for more compact UI
        tiny_font = pygame.font.Font(None, 18)   # Even smaller for instructions
        
        # Compact UI positioning - much smaller area
        ui_x = SCREEN_WIDTH - 220  # Narrower panel
        
        # Level indicator
        level_text = font.render(f"Level {self.current_level}", True, BLACK)
        self.screen.blit(level_text, (ui_x, 10))
        
        # Level type indicator
        if hasattr(self, 'current_level_type'):
            type_text = small_font.render(f"Type: {self.current_level_type}", True, DARK_GRAY)
            self.screen.blit(type_text, (ui_x, 45))
        
        # Platform counter
        platforms_left = self.max_platforms - len(self.drawn_platforms)
        platform_text = small_font.render(f"Platforms: {platforms_left}", True, BLACK)
        self.screen.blit(platform_text, (ui_x, 65))
        
        # Score
        score_text = small_font.render(f"Score: {self.player.score}", True, BLACK)
        self.screen.blit(score_text, (ui_x, 85))
        
        # Platform timer indicators - compact
        y_offset = 110
        active_timers = 0
        for i, platform in enumerate(self.drawn_platforms):
            if platform.temporary and platform.active:
                current_time = pygame.time.get_ticks()
                time_left = PLATFORM_FADE_TIME - (current_time - platform.creation_time)
                seconds_left = max(0, time_left / 1000)
                
                timer_text = tiny_font.render(f"P{i+1}: {seconds_left:.1f}s", True, PURPLE)
                self.screen.blit(timer_text, (ui_x, y_offset + active_timers * 18))
                active_timers += 1
        
        # Controls moved to top left
        controls = [
            "CONTROLS:",
            "WASD/Arrows = Move",
            "Space = Jump", 
            "Click+Drag = Platform",
            "R = Reset  N = Clear",
            "ESC = Exit  F11 = Fullscreen"
        ]
        
        for i, control in enumerate(controls):
            color = BLACK if i == 0 else DARK_GRAY
            font_to_use = small_font if i == 0 else tiny_font
            text = font_to_use.render(control, True, color)
            self.screen.blit(text, (10, 10 + i * 18))
        
        # Legend for new elements - top left, below controls
        legend_start_y = 10 + len(controls) * 18 + 10  # Start after controls with some spacing
        legend_items = []
        if self.moving_platforms:
            legend_items.append(("Light Blue = Moving", (150, 150, 255)))
        if self.spikes:
            legend_items.append(("Red = Spikes!", (255, 50, 50)))
        if self.disappearing_platforms:
            legend_items.append(("Orange = Disappears", (255, 200, 100)))
        if self.collectibles:
            legend_items.append(("Gold = +10pts", (255, 215, 0)))
            
        for i, (text, color) in enumerate(legend_items):
            legend_text = tiny_font.render(text, True, color)
            self.screen.blit(legend_text, (10, legend_start_y + i * 18))
        
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
