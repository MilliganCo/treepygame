# game_config.py
import pygame

directions = {
    pygame.K_w: (0, -1),  # Вверх
    pygame.K_s: (0, 1),  # Вниз
    pygame.K_a: (-1, 0),  # Влево
    pygame.K_d: (1, 0),  # Вправо
}

# Константы окна
CELL_SIZE = 20
TERMINAL_HEIGHT = 100  # Высота терминала сообщений
INTERFACE_HEIGHT = 50  # Высота интерфейса сверху
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = (40 * CELL_SIZE) + INTERFACE_HEIGHT + TERMINAL_HEIGHT
FPS = 30

# Игровые параметры
TREE_HEALTH = 10  # Здоровье дерева
PLAYER_HEALTH = 4
PLAYER_MAX_HEALTH = 4
PLAYER_MANA = 200
PLAYER_MAX_MANA = 200
selected_trap = "bomb"  # Ловушка по умолчанию

# Цвета символов ASCII
ASCII_COLORS = {
    "#": (255, 255, 255), ".": (10, 10, 10), "T": (0, 255, 0), "@": (0, 100, 255),
    "B": (255, 255, 0), "B2": (140, 140, 50), "S": (0, 255, 0), "s": (0, 255, 0),
    "F": (0, 0, 255), "P": (255, 182, 193), "R": (0, 255, 255), "+": (255, 0, 0),
    "*": (0, 0, 255), '"': (100, 0, 255), "C3": (255, 0, 0), "C2": (255, 165, 0),
    "C1": (255, 255, 0), "C5": (128, 0, 128), "C4": (150, 50, 50)  # Ворона с 4 HP
}

trap_keys = {
    "bomb": 0,
    "shooter": 0,
    "freeze": 0,
    "bait": 0,
    "heal_rune": 0
}
