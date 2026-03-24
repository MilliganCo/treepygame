import pygame
from game_config import *

def draw_interface(screen, tree_health, player_health, player_mana):
    font = pygame.font.SysFont("Courier", 24)
    pygame.draw.rect(screen, (0, 0, 0), (0, 0, WINDOW_WIDTH, INTERFACE_HEIGHT))

    health_text = font.render(f"Tree: {tree_health}", True, (0, 255, 0))
    player_text = font.render(f"Player: {player_health}", True, (255, 0, 0))
    mana_text = font.render(f"Mana: {player_mana}", True, (0, 0, 255))

    screen.blit(health_text, (10, 10))
    screen.blit(player_text, (150, 10))
    screen.blit(mana_text, (300, 10))

def draw_ascii_map(screen, game_map, crow_positions, projectiles):
    font = pygame.font.SysFont("Courier", CELL_SIZE)

    for y, row in enumerate(game_map):
        for x, char in enumerate(row):
            if char.startswith("C"):
                continue
            color = ASCII_COLORS.get(char, (255, 255, 255))
            text_surface = font.render(char, True, color)
            screen.blit(text_surface, (x * CELL_SIZE, y * CELL_SIZE + INTERFACE_HEIGHT))

    for crow_x, crow_y, health in crow_positions:
        crow_color = ASCII_COLORS.get(f"C{health}", (255, 0, 0))
        text_surface = font.render("C", True, crow_color)
        screen.blit(text_surface, (crow_x * CELL_SIZE, crow_y * CELL_SIZE + INTERFACE_HEIGHT))

    for proj in projectiles:
        px, py, tx, ty, start_time = proj
        progress = min(1, (time.time() - start_time) * 0.01)
        proj_x = int(px + (tx - px) * progress)
        proj_y = int(py + (ty - py) * progress)

        if game_map[proj_y][proj_x] in ["#", "B", "B2", "S", "s", "F", "P", "R", "@"]:
            projectiles.remove(proj)
            continue

        text_surface = font.render("+", True, (255, 0, 0))
        screen.blit(text_surface, (proj_x * CELL_SIZE, proj_y * CELL_SIZE + INTERFACE_HEIGHT))

def draw_terminal(screen, messages):
    font = pygame.font.SysFont("Courier", 16)
    terminal_rect = pygame.Rect(0, WINDOW_HEIGHT - TERMINAL_HEIGHT, WINDOW_WIDTH, TERMINAL_HEIGHT)
    pygame.draw.rect(screen, (0, 0, 0), terminal_rect)
    pygame.draw.rect(screen, (255, 255, 255), terminal_rect, 2)

    for i, message in enumerate(messages[-5:]):
        text_surface = font.render(message, True, (255, 255, 255))
        screen.blit(text_surface, (10, WINDOW_HEIGHT - TERMINAL_HEIGHT + i * 20))
