import random
import sys
from dataclasses import dataclass

import pygame

# =========================
# Simple 2D Vertical Shooter
# -------------------------
# Simple 2D Vertical Shooter
# Run from project root:
#   ./run_game1.sh
# =========================

WIDTH = 480
HEIGHT = 720
FPS = 60
TITLE = "Simple Vertical Shooter"

PLAYER_SPEED = 6
BULLET_SPEED = 10
ENEMY_MIN_SPEED = 2
ENEMY_MAX_SPEED = 5
ENEMY_SPAWN_INTERVAL = 700  # ms
PLAYER_SHOT_INTERVAL = 180  # ms
STAR_COUNT = 50

WHITE = (245, 245, 245)
BLACK = (20, 20, 30)
BLUE = (90, 180, 255)
RED = (255, 90, 90)
YELLOW = (255, 220, 90)
GREEN = (90, 255, 140)
GRAY = (170, 170, 170)


@dataclass
class Star:
    x: float
    y: float
    speed: float
    radius: int

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = -5
            self.x = random.randint(0, WIDTH)

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((6, 18), pygame.SRCALPHA)
        pygame.draw.rect(self.image, YELLOW, (0, 0, 6, 18), border_radius=3)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = BULLET_SPEED

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        w = random.randint(32, 56)
        h = random.randint(28, 48)
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.polygon(
            self.image,
            RED,
            [(w // 2, 0), (w, h - 8), (w // 2, h), (0, h - 8)],
        )
        pygame.draw.polygon(
            self.image,
            WHITE,
            [(w // 2, 7), (w - 10, h - 10), (10, h - 10)],
            2,
        )
        self.rect = self.image.get_rect(
            center=(random.randint(30, WIDTH - 30), random.randint(-120, -40))
        )
        self.speed = random.randint(ENEMY_MIN_SPEED, ENEMY_MAX_SPEED)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.frames = []
        for radius in (8, 14, 20, 26):
            surface = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.circle(surface, YELLOW, (30, 30), radius)
            pygame.draw.circle(surface, RED, (30, 30), max(radius - 6, 4), 3)
            self.frames.append(surface)
        self.index = 0
        self.image = self.frames[self.index]
        self.rect = self.image.get_rect(center=center)
        self.last_update = pygame.time.get_ticks()
        self.frame_interval = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_interval:
            self.last_update = now
            self.index += 1
            if self.index >= len(self.frames):
                self.kill()
            else:
                center = self.rect.center
                self.image = self.frames[self.index]
                self.rect = self.image.get_rect(center=center)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((44, 54), pygame.SRCALPHA)
        pygame.draw.polygon(
            self.image,
            BLUE,
            [(22, 0), (44, 44), (30, 54), (22, 44), (14, 54), (0, 44)],
        )
        pygame.draw.rect(self.image, WHITE, (18, 12, 8, 18), border_radius=3)
        pygame.draw.polygon(self.image, GREEN, [(22, 10), (29, 22), (15, 22)])
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 90))
        self.speed = PLAYER_SPEED
        self.hp = 3
        self.last_shot = 0

    def update(self, pressed_keys):
        dx = 0
        dy = 0
        if pressed_keys[pygame.K_LEFT] or pressed_keys[pygame.K_a]:
            dx -= self.speed
        if pressed_keys[pygame.K_RIGHT] or pressed_keys[pygame.K_d]:
            dx += self.speed
        if pressed_keys[pygame.K_UP] or pressed_keys[pygame.K_w]:
            dy -= self.speed
        if pressed_keys[pygame.K_DOWN] or pressed_keys[pygame.K_s]:
            dy += self.speed

        self.rect.x += dx
        self.rect.y += dy
        self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

    def can_shoot(self):
        now = pygame.time.get_ticks()
        return now - self.last_shot >= PLAYER_SHOT_INTERVAL

    def shoot(self):
        self.last_shot = pygame.time.get_ticks()
        return Bullet(self.rect.centerx, self.rect.top)


def draw_text(screen, text, size, x, y, color=WHITE, center=True):
    font = pygame.font.SysFont(None, size)
    surface = font.render(text, True, color)
    rect = surface.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(surface, rect)


def create_stars():
    stars = []
    for _ in range(STAR_COUNT):
        stars.append(
            Star(
                x=random.randint(0, WIDTH),
                y=random.randint(0, HEIGHT),
                speed=random.uniform(1.0, 4.0),
                radius=random.randint(1, 2),
            )
        )
    return stars


def reset_game():
    all_sprites = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    effects = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)

    return player, all_sprites, bullets, enemies, effects, 0, False


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    spawn_enemy_event = pygame.USEREVENT + 1
    pygame.time.set_timer(spawn_enemy_event, ENEMY_SPAWN_INTERVAL)

    stars = create_stars()
    player, all_sprites, bullets, enemies, effects, score, game_over = reset_game()

    running = True
    while running:
        dt = clock.tick(FPS)
        pressed_keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == spawn_enemy_event and not game_over:
                enemy = Enemy()
                all_sprites.add(enemy)
                enemies.add(enemy)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r and game_over:
                    player, all_sprites, bullets, enemies, effects, score, game_over = reset_game()

        if not game_over:
            for star in stars:
                star.update()

            player.update(pressed_keys)

            if pressed_keys[pygame.K_SPACE] and player.can_shoot():
                bullet = player.shoot()
                all_sprites.add(bullet)
                bullets.add(bullet)

            bullets.update()
            enemies.update()
            effects.update()

            hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
            for enemy in hits:
                score += 1
                explosion = Explosion(enemy.rect.center)
                all_sprites.add(explosion)
                effects.add(explosion)

            collisions = pygame.sprite.spritecollide(player, enemies, True)
            for enemy in collisions:
                player.hp -= 1
                explosion = Explosion(enemy.rect.center)
                all_sprites.add(explosion)
                effects.add(explosion)
                if player.hp <= 0:
                    game_over = True

        screen.fill(BLACK)

        for star in stars:
            star.draw(screen)

        all_sprites.draw(screen)

        pygame.draw.rect(screen, GRAY, (12, 12, 120, 16), border_radius=8)
        pygame.draw.rect(screen, GREEN, (12, 12, max(player.hp, 0) * 40, 16), border_radius=8)
        draw_text(screen, f"SCORE: {score}", 32, WIDTH - 100, 28)
        draw_text(screen, f"HP: {player.hp}", 28, 72, 48)

        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay, (0, 0))
            draw_text(screen, "がめおべら", 64, WIDTH // 2, HEIGHT // 2 - 40, RED)
            draw_text(screen, f"失われた命: {score}", 36, WIDTH // 2, HEIGHT // 2 + 20)
            draw_text(screen, "Press R to Restart / ESC to Quit", 30, WIDTH // 2, HEIGHT // 2 + 70)
        else:
            draw_text(screen, "移動はいつもの！　スペースで撃て！", 24, WIDTH // 2, HEIGHT - 24)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

