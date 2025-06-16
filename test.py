import pygame
import sys
import random

# --- Constants and Configuration ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)
GROUND_COLOR = (148, 114, 89)
PIPE_GREEN = (46, 172, 57)
PIPE_HIGHLIGHT = (127, 255, 138)
BIRD_YELLOW_LIGHT = (255, 240, 100)
BIRD_YELLOW_DARK = (245, 190, 40)
PARTICLE_COLOR = (255, 255, 224)

# Game Physics
GRAVITY = 0.4
JUMP_STRENGTH = -9
PIPE_SPEED = -4
PIPE_GAP_SIZE = 180
PIPE_SPAWN_INTERVAL = 1400  # milliseconds

class Bird(pygame.sprite.Sprite):
    """
    Represents the player-controlled bird.
    Handles movement, animation, and particle effects.
    """
    def __init__(self):
        super().__init__()
        # Create the bird's visual representation (surface)
        self.image = pygame.Surface((45, 35), pygame.SRCALPHA)
        self.draw_bird(self.image, BIRD_YELLOW_LIGHT, BIRD_YELLOW_DARK)
        
        self.rect = self.image.get_rect(center=(150, SCREEN_HEIGHT / 2))
        self.velocity = 0
        self.particles = []

    def draw_bird(self, surface, primary_color, shadow_color):
        """Draws a stylized bird with a gradient effect onto the given surface."""
        # Main body
        pygame.draw.circle(surface, shadow_color, (22, 20), 15)
        pygame.draw.circle(surface, primary_color, (22, 17), 15)
        # Beak
        pygame.draw.polygon(surface, (245, 130, 50), [(38, 18), (50, 22), (38, 26)])
        # Eye
        pygame.draw.circle(surface, BLACK, (32, 14), 4)
        pygame.draw.circle(surface, WHITE, (33, 13), 2)
        # Wing
        pygame.draw.ellipse(surface, shadow_color, (15, 12, 20, 10))
        pygame.draw.ellipse(surface, primary_color, (15, 10, 20, 10))


    def update(self):
        """Updates the bird's state each frame."""
        # Apply gravity
        self.velocity += GRAVITY
        self.rect.y += int(self.velocity)

        # Prevent bird from going off the top of the screen
        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity = 0
        
        # Add particles for a trail effect
        self.add_particles()
        self.update_particles()
            
    def jump(self):
        """Makes the bird jump upwards."""
        self.velocity = JUMP_STRENGTH

    def add_particles(self):
        """Adds particles to create a trail effect."""
        p_x = self.rect.left - 5
        p_y = self.rect.centery + random.randint(-5, 5)
        p_radius = random.randint(2, 4)
        p_lifetime = random.randint(10, 20)
        particle = {'pos': [p_x, p_y], 'radius': p_radius, 'lifetime': p_lifetime}
        self.particles.append(particle)

    def update_particles(self):
        """Updates the position and lifetime of particles."""
        for particle in self.particles[:]:
            particle['lifetime'] -= 1
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
            else:
                particle['pos'][0] -= 2 # Move particles left
                particle['radius'] -= 0.1 # Shrink particles

    def draw(self, screen):
        """Draws the bird and its particles."""
        screen.blit(self.image, self.rect)
        for particle in self.particles:
            if particle['radius'] > 0:
                 pygame.draw.circle(screen, PARTICLE_COLOR, particle['pos'], int(particle['radius']))


class Pipe(pygame.sprite.Sprite):
    """
    Represents a pair of pipes (top and bottom).
    """
    def __init__(self, x, is_top, gap_y):
        super().__init__()
        self.width = 80
        self.is_top = is_top

        if self.is_top:
            height = gap_y - PIPE_GAP_SIZE // 2
            self.image = self.create_pipe_surface(self.width, height)
            self.rect = self.image.get_rect(bottomleft=(x, gap_y - PIPE_GAP_SIZE // 2))
        else:
            height = SCREEN_HEIGHT - (gap_y + PIPE_GAP_SIZE // 2)
            self.image = self.create_pipe_surface(self.width, height)
            self.rect = self.image.get_rect(topleft=(x, gap_y + PIPE_GAP_SIZE // 2))

    def create_pipe_surface(self, width, height):
        """Creates a visually appealing pipe surface with gradients and highlights."""
        pipe_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        # Main pipe body with gradient
        for i in range(width):
            ratio = i / width
            color_val = 20 + int(ratio * 60)
            color = (max(0, PIPE_GREEN[0] - color_val), max(0, PIPE_GREEN[1] - color_val), max(0, PIPE_GREEN[2] - color_val))
            pygame.draw.line(pipe_surface, color, (i, 0), (i, height))

        # Pipe end cap
        cap_height = 30
        end_cap_rect = pygame.Rect(0, 0, width, cap_height)
        if self.is_top:
            end_cap_rect.bottom = height
        
        pygame.draw.rect(pipe_surface, PIPE_GREEN, end_cap_rect)
        pygame.draw.rect(pipe_surface, BLACK, end_cap_rect, 3) # Border
        
        # Highlight
        highlight_rect = end_cap_rect.copy().inflate(-15, -15)
        pygame.draw.rect(pipe_surface, PIPE_HIGHLIGHT, highlight_rect, 4, border_radius=5)
        
        return pipe_surface

    def update(self):
        """Moves the pipe to the left."""
        self.rect.x += PIPE_SPEED


class ParallaxBackground:
    """
    Manages multiple scrolling background layers for a parallax effect.
    """
    def __init__(self):
        self.layers = []
        # Create layers programmatically
        self.create_layers()

    def create_layers(self):
        """Generates the surfaces for each background layer."""
        # Layer 1: Distant Clouds (slowest)
        layer1 = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for _ in range(10):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(50, 200)
            radius = random.randint(20, 50)
            pygame.draw.circle(layer1, (220, 235, 245), (x, y), radius)
        self.layers.append({'surface': layer1, 'speed': 0.5, 'x': 0})
        
        # Layer 2: Distant Cityscape
        layer2 = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for i in range(25):
            x = i * 40
            h = random.randint(50, 150)
            y = SCREEN_HEIGHT - 100 - h
            pygame.draw.rect(layer2, (100, 100, 120), (x, y, 30, h))
        self.layers.append({'surface': layer2, 'speed': 1, 'x': 0})

        # Layer 3: Foreground Hills
        layer3 = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.ellipse(layer3, (50, 180, 50), (-100, SCREEN_HEIGHT-150, SCREEN_WIDTH/2, 200))
        pygame.draw.ellipse(layer3, (50, 180, 50), (SCREEN_WIDTH/2 - 50, SCREEN_HEIGHT-180, SCREEN_WIDTH/1.5, 250))
        self.layers.append({'surface': layer3, 'speed': 2, 'x': 0})

    def update(self):
        """Scrolls each layer."""
        for layer in self.layers:
            layer['x'] -= layer['speed']
            if layer['x'] <= -SCREEN_WIDTH:
                layer['x'] = 0

    def draw(self, screen):
        """Draws all layers onto the screen."""
        screen.fill(SKY_BLUE)
        for layer in self.layers:
            screen.blit(layer['surface'], (layer['x'], 0))
            screen.blit(layer['surface'], (layer['x'] + SCREEN_WIDTH, 0))


class Game:
    """
    Main game class that orchestrates all game components.
    """
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Graphics-Heavy Flappy Bird")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 40)
        self.game_active = False
        self.score = 0
        self.shake = 0
        self.reset_game()

    def reset_game(self):
        """Resets the game to its initial state."""
        self.background = ParallaxBackground()
        self.bird = Bird()
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.bird)
        self.pipes = pygame.sprite.Group()
        self.score = 0
        self.pipe_timer = pygame.USEREVENT + 1
        pygame.time.set_timer(self.pipe_timer, PIPE_SPAWN_INTERVAL)
        self.death_particles = []
        self.game_active = True

    def run(self):
        """The main game loop."""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.game_active:
                        self.bird.jump()
                    if event.key == pygame.K_SPACE and not self.game_active:
                        self.reset_game()
                if event.type == self.pipe_timer and self.game_active:
                    self.add_pipe_pair()

            self.screen.fill(SKY_BLUE)
            
            # --- Update and Draw ---
            self.background.update()
            self.background.draw(self.screen)

            if self.game_active:
                self.update_game_active()
            else:
                self.update_game_over()
            
            # Draw ground last
            self.draw_ground()
            
            # Apply screen shake if active
            offset = (0, 0)
            if self.shake > 0:
                self.shake -= 1
                offset = (random.randint(-5, 5), random.randint(-5, 5))
            
            # We blit the main screen to itself to apply the shake
            temp_surface = self.screen.copy()
            self.screen.fill(SKY_BLUE)
            self.screen.blit(temp_surface, offset)
            
            pygame.display.update()
            self.clock.tick(FPS)

    def update_game_active(self):
        """Handles updates when the game is running."""
        # Update sprites
        self.pipes.update()
        self.bird.update()

        # Draw everything
        self.pipes.draw(self.screen)
        self.bird.draw(self.screen)

        self.check_collisions()
        self.update_score()
        self.draw_score()

    def update_game_over(self):
        """Handles updates and drawing when it's game over."""
        self.pipes.draw(self.screen) # Keep pipes visible
        self.update_death_particles()
        self.draw_death_particles()
        self.draw_game_over_screen()

    def add_pipe_pair(self):
        """Creates and adds a new pair of pipes to the game."""
        gap_y = random.randint(200, SCREEN_HEIGHT - 200)
        top_pipe = Pipe(SCREEN_WIDTH + 50, True, gap_y)
        bottom_pipe = Pipe(SCREEN_WIDTH + 50, False, gap_y)
        self.pipes.add(top_pipe, bottom_pipe)
        self.all_sprites.add(top_pipe, bottom_pipe)

    def check_collisions(self):
        """Checks for collisions between bird and pipes or ground."""
        if pygame.sprite.spritecollide(self.bird, self.pipes, False):
            self.end_game()
        if self.bird.rect.bottom >= SCREEN_HEIGHT - 100:
            self.bird.rect.bottom = SCREEN_HEIGHT - 100
            self.end_game()

    def end_game(self):
        """Triggers the game over state."""
        self.game_active = False
        self.shake = 20 # Activate screen shake
        self.create_death_particles()

    def update_score(self):
        """Increments the score when the bird passes a pipe."""
        for pipe in self.pipes:
            # Check if pipe has a 'passed' attribute
            if not hasattr(pipe, 'passed'):
                pipe.passed = False
            
            if not pipe.passed and pipe.rect.centerx < self.bird.rect.centerx:
                if not pipe.is_top: # Only score for one of the pipes in a pair
                    self.score += 1
                pipe.passed = True # Mark both pipes in pair as passed
                for p in self.pipes:
                    if p.rect.centerx == pipe.rect.centerx:
                        p.passed = True
        
        # Clean up old pipes
        self.pipes.sprites()
        for pipe in self.pipes.sprites():
            if pipe.rect.right < 0:
                pipe.kill()


    def draw_score(self):
        """Renders the current score on the screen."""
        score_surface = self.font.render(str(self.score), True, WHITE)
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH / 2, 50))
        # Draw shadow
        shadow_surface = self.font.render(str(self.score), True, BLACK)
        self.screen.blit(shadow_surface, score_rect.move(3, 3))
        # Draw main text
        self.screen.blit(score_surface, score_rect)
        
    def draw_ground(self):
        """Draws the ground area."""
        pygame.draw.rect(self.screen, GROUND_COLOR, (0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100))
        pygame.draw.line(self.screen, BLACK, (0, SCREEN_HEIGHT - 100), (SCREEN_WIDTH, SCREEN_HEIGHT - 100), 5)


    def draw_game_over_screen(self):
        """Displays the game over text and final score."""
        # "Game Over" Text
        over_text = self.font.render("Game Over", True, (200, 0, 0))
        over_rect = over_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50))
        self.screen.blit(over_text, over_rect.move(3,3)) # Shadow
        self.screen.blit(self.font.render("Game Over", True, WHITE), over_rect)

        # "Press Space to Restart" Text
        restart_text = self.small_font.render("Press Space to Restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50))
        self.screen.blit(restart_text, restart_rect.move(2,2)) # Shadow
        self.screen.blit(self.small_font.render("Press Space to Restart", True, (200, 200, 200)), restart_rect)


    def create_death_particles(self):
        """Creates a burst of particles on bird death."""
        for _ in range(30):
            p_pos = list(self.bird.rect.center)
            p_vel = [random.uniform(-4, 4), random.uniform(-6, 2)]
            p_size = random.randint(5, 10)
            p_color = random.choice([BIRD_YELLOW_LIGHT, BIRD_YELLOW_DARK, (255, 100, 100)])
            particle = {'pos': p_pos, 'vel': p_vel, 'size': p_size, 'color': p_color}
            self.death_particles.append(particle)

    def update_death_particles(self):
        """Updates physics for the death particles."""
        for p in self.death_particles:
            p['vel'][1] += 0.3 # Gravity
            p['pos'][0] += p['vel'][0]
            p['pos'][1] += p['vel'][1]
            p['size'] -= 0.2

    def draw_death_particles(self):
        """Draws the death particles."""
        for p in self.death_particles:
            if p['size'] > 0:
                pygame.draw.rect(self.screen, p['color'], (p['pos'][0], p['pos'][1], p['size'], p['size']))


if __name__ == '__main__':
    game = Game()
    game.run()
