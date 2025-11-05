import pygame
import sys

# Initialize Pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLUE = (135, 206, 235)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

# Player settings
PLAYER_WIDTH = 32
PLAYER_HEIGHT = 48
PLAYER_SPEED = 5
JUMP_SPEED = -15
GRAVITY = 0.8

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.score = 0
        
    def update(self, platforms):
        # Handle input
        keys = pygame.key.get_pressed()
        self.vel_x = 0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = PLAYER_SPEED
            
        # Apply gravity
        self.vel_y += GRAVITY
        
        # Move horizontally
        self.rect.x += self.vel_x
        
        # Check horizontal collisions
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.vel_x > 0:  # Moving right
                    self.rect.right = platform.left
                elif self.vel_x < 0:  # Moving left
                    self.rect.left = platform.right
                    
        # Move vertically
        self.rect.y += self.vel_y
        self.on_ground = False
        
        # Check vertical collisions
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.vel_y > 0:  # Falling
                    self.rect.bottom = platform.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:  # Jumping
                    self.rect.top = platform.bottom
                    self.vel_y = 0
                    
        # Keep player on screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            
    def jump(self):
        if self.on_ground:
            self.vel_y = JUMP_SPEED
            
    def draw(self, screen):
        # Draw Mario-like character
        pygame.draw.rect(screen, RED, self.rect)
        # Draw hat
        hat_rect = pygame.Rect(self.rect.x, self.rect.y - 5, self.rect.width, 8)
        pygame.draw.rect(screen, (200, 0, 0), hat_rect)

class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.collected = False
        
    def draw(self, screen):
        if not self.collected:
            pygame.draw.circle(screen, YELLOW, self.rect.center, 10)
            pygame.draw.circle(screen, (255, 215, 0), self.rect.center, 6)

class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 30, 30)
        self.vel_x = -2
        self.alive = True
        
    def update(self, platforms):
        if not self.alive:
            return
            
        # Move horizontally
        self.rect.x += self.vel_x
        
        # Bounce off platforms
        for platform in platforms:
            if self.rect.colliderect(platform):
                self.vel_x *= -1
                break
                
        # Reverse direction at screen edges
        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.vel_x *= -1
            
    def draw(self, screen):
        if self.alive:
            pygame.draw.rect(screen, BROWN, self.rect)
            # Draw eyes
            pygame.draw.circle(screen, BLACK, (self.rect.x + 8, self.rect.y + 8), 3)
            pygame.draw.circle(screen, BLACK, (self.rect.x + 22, self.rect.y + 8), 3)

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Super Mario Game")
    clock = pygame.time.Clock()
    
    # Create player
    player = Player(50, SCREEN_HEIGHT - 200)
    
    # Create platforms
    platforms = [
        pygame.Rect(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40),  # Ground
        pygame.Rect(200, SCREEN_HEIGHT - 120, 150, 20),       # Platform 1
        pygame.Rect(400, SCREEN_HEIGHT - 200, 150, 20),       # Platform 2
        pygame.Rect(600, SCREEN_HEIGHT - 160, 150, 20),       # Platform 3
    ]
    
    # Create coins
    coins = [
        Coin(250, SCREEN_HEIGHT - 150),
        Coin(450, SCREEN_HEIGHT - 230),
        Coin(650, SCREEN_HEIGHT - 190),
        Coin(300, SCREEN_HEIGHT - 70),
        Coin(500, SCREEN_HEIGHT - 70),
    ]
    
    # Create enemies
    enemies = [
        Enemy(250, SCREEN_HEIGHT - 150),
        Enemy(450, SCREEN_HEIGHT - 230),
    ]
    
    font = pygame.font.Font(None, 36)
    
    running = True
    game_over = False
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()
                elif event.key == pygame.K_r and game_over:
                    # Restart game
                    player = Player(50, SCREEN_HEIGHT - 200)
                    for coin in coins:
                        coin.collected = False
                    for enemy in enemies:
                        enemy.alive = True
                    game_over = False
                    
        if not game_over:
            # Update game objects
            player.update(platforms)
            
            for enemy in enemies:
                enemy.update(platforms)
                
            # Check coin collection
            for coin in coins:
                if not coin.collected and player.rect.colliderect(coin.rect):
                    coin.collected = True
                    player.score += 10
                    
            # Check enemy collision
            for enemy in enemies:
                if enemy.alive and player.rect.colliderect(enemy.rect):
                    # Check if player is jumping on enemy
                    if player.vel_y > 0 and player.rect.bottom - enemy.rect.top < 10:
                        enemy.alive = False
                        player.vel_y = JUMP_SPEED // 2  # Small bounce
                        player.score += 50
                    else:
                        game_over = True
                        
            # Check if player falls off screen
            if player.rect.top > SCREEN_HEIGHT:
                game_over = True
        
        # Draw everything
        screen.fill(BLUE)  # Sky background
        
        # Draw platforms
        for platform in platforms:
            pygame.draw.rect(screen, GREEN, platform)
            
        # Draw coins
        for coin in coins:
            coin.draw(screen)
            
        # Draw enemies
        for enemy in enemies:
            enemy.draw(screen)
            
        # Draw player
        player.draw(screen)
        
        # Draw UI
        score_text = font.render(f"Score: {player.score}", True, BLACK)
        screen.blit(score_text, (10, 10))
        
        if game_over:
            game_over_text = font.render("GAME OVER! Press R to restart", True, RED)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(game_over_text, text_rect)
            
        # Draw instructions
        instructions = [
            "Arrow Keys or WASD: Move",
            "Space: Jump",
            "Collect coins and avoid enemies!"
        ]
        
        for i, instruction in enumerate(instructions):
            text = pygame.font.Font(None, 24).render(instruction, True, BLACK)
            screen.blit(text, (10, SCREEN_HEIGHT - 80 + i * 25))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()