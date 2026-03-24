### mana.py
import random
import pygame

PLAYER_MAX_MANA = 200

def animate_mana(game_map, step_count):
    """Анимация маны: переключение символа между * и "."""
    if step_count % 3 == 0:  # Анимация каждые 20 кадров
        for y, row in enumerate(game_map):
            for x, char in enumerate(row):
                if char == "*":
                    game_map[y][x] = '"'
                elif char == '"':
                    game_map[y][x] = "*"

def spawn_mana(game_map):
    if random.random() < 0.3:  # 30% шанс появления
        while True:
            x, y = random.randint(1, len(game_map[0]) - 2), random.randint(1, len(game_map) - 2)
            if game_map[y][x] == ".":
                game_map[y][x] = "*"
                break

def collect_mana(game_map, player_pos, mana):
    x, y = player_pos
    if game_map[y][x] == "*":
        collected = random.randint(1, 8) * 10
        mana = min(PLAYER_MAX_MANA, mana + collected)
        game_map[y][x] = "."
    return mana

def draw_interface(screen, mana, health, max_health):
    font = pygame.font.SysFont("Courier", 24)
    mana_surface = font.render(f"Mana: {mana}/{PLAYER_MAX_MANA}", True, (0, 255, 255))
    health_surface = font.render(f"Health: {health}/{max_health}", True, (255, 0, 0))
    screen.blit(mana_surface, (10, 40))
    screen.blit(health_surface, (10, 70))