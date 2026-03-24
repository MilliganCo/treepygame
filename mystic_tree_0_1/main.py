import pygame
import sys
from map_generator import generate_map
from player import move_player
import random

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
CELL_SIZE = 20
FPS = 30

# Высота терминала (в пикселях)
TERMINAL_HEIGHT = 100

ASCII_COLORS = {
    "#": (255, 255, 255),  # Стена
    ".": (20, 20, 20),  # Пустая клетка
    "T": (0, 255, 0),      # Дерево
    "@": (0, 0, 255),      # Игрок
    "^": (255, 255, 0),    # Ловушка (здоровье 2)
    "^1": (200, 200, 0),   # Ловушка (здоровье 1)
    "C3": (255, 0, 0),     # Ворона с 3 здоровья
    "C2": (255, 165, 0),   # Ворона с 2 здоровья
    "C1": (255, 255, 0),   # Ворона с 1 здоровьем
    "C5": (128, 0, 128),   # Босс-ворона (фиолетовая)
}

directions = {
    pygame.K_w: (0, -1),  # Вверх
    pygame.K_s: (0, 1),  # Вниз
    pygame.K_a: (-1, 0),  # Влево
    pygame.K_d: (1, 0),  # Вправо
}

TREE_HEALTH = 10

def draw_ascii_map(screen, game_map, crow_positions):
    font = pygame.font.SysFont("Courier", CELL_SIZE)
    for y, row in enumerate(game_map):
        for x, char in enumerate(row):
            if char.startswith("C"):
                continue  # Не рисуем ворону как обычный символ
            color = ASCII_COLORS.get(char, (255, 255, 255))
            text_surface = font.render("^" if char.startswith("^") else char, True, color)
            screen.blit(text_surface, (x * CELL_SIZE, y * CELL_SIZE))

    # Отрисовка ворон с учётом здоровья
    for crow_x, crow_y, health in crow_positions:
        crow_color = ASCII_COLORS.get(f"C{health}", (255, 0, 0))
        text_surface = font.render("C", True, crow_color)
        screen.blit(text_surface, (crow_x * CELL_SIZE, crow_y * CELL_SIZE))

def move_crows(game_map, crow_positions, tree_pos, add_message, step_count):
    """Движение ворон с учётом ловушек, предотвращением уничтожения стен и корректным состоянием карты."""
    new_positions = []
    tree_x, tree_y = tree_pos
    dead_crow_count = 0  # Счётчик убитых ворон

    # Замедляем движение ворон: двигаются каждые 7 кадров
    if step_count % 7 != 0:
        return crow_positions

    for crow in crow_positions:
        crow_x, crow_y, health = crow

        # Случайное перемещение (50% шанс)
        if random.random() < 0.5:
            for _ in range(10):  # До 10 попыток найти случайную клетку
                offset_x = random.randint(-2, 2)
                offset_y = random.randint(-2, 2)
                random_x, random_y = crow_x + offset_x, crow_y + offset_y
                if (
                        0 <= random_x < len(game_map[0])
                        and 0 <= random_y < len(game_map)
                        and game_map[random_y][random_x] == "."
                ):
                    # Ворона перемещается только на пустую клетку
                    game_map[crow_y][crow_x] = "."  # Очищаем старую клетку
                    game_map[random_y][random_x] = "C"  # Перемещаем ворону
                    new_positions.append((random_x, random_y, health))
                    break
            else:
                # Если не нашлось подходящей клетки, ворона остаётся на месте
                new_positions.append((crow_x, crow_y, health))
            continue

        # Если ворона достигла дерева
        if (crow_x, crow_y) == tree_pos:
            global TREE_HEALTH
            TREE_HEALTH -= 1
            add_message(f"Ворона нанесла урон дереву! У дерева осталось {TREE_HEALTH} здоровья.")
            game_map[tree_y][tree_x] = "T"  # Убедимся, что символ дерева остаётся
            # Перерождение вороны
            for _ in range(10):  # До 10 попыток найти место для перерождения
                offset_x = random.randint(-4, 4)
                offset_y = random.randint(-4, 4)
                respawn_x, respawn_y = crow_x + offset_x, crow_y + offset_y
                if (
                    0 <= respawn_x < len(game_map[0])
                    and 0 <= respawn_y < len(game_map)
                    and game_map[respawn_y][respawn_x] == "."
                ):
                    game_map[crow_y][crow_x] = "."  # Убираем ворону с дерева
                    game_map[respawn_y][respawn_x] = "C"  # Перемещаем ворону
                    new_positions.append((respawn_x, respawn_y, health - 1))
                    break
            else:
                add_message("Ворона не смогла найти место для перерождения!")
            continue

        # Проверяем доступные направления для движения к дереву
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # Вверх, вниз, влево, вправо
        valid_moves = []
        for dx, dy in directions:
            nx, ny = crow_x + dx, crow_y + dy
            if 0 <= nx < len(game_map[0]) and 0 <= ny < len(game_map) and game_map[ny][nx] != "#":
                valid_moves.append((nx, ny))

        # Если есть доступные ходы, выбираем ближайший к дереву
        if valid_moves:
            closest_move = min(valid_moves, key=lambda pos: abs(pos[0] - tree_x) + abs(pos[1] - tree_y))
            nx, ny = closest_move

            # Если ворона наступает на ловушку
            if game_map[ny][nx] in ["^", "^1"]:  # Проверяем ловушку
                if game_map[ny][nx] == "^":  # Ловушка с полным здоровьем
                    game_map[ny][nx] = "^1"  # Ослабляем ловушку
                    damage = 3
                else:  # Ловушка с малым здоровьем
                    game_map[ny][nx] = "."  # Ловушка исчезает
                    damage = 1

                health -= damage
                if health <= 0:  # Если здоровье вороны падает до 0
                    game_map[crow_y][crow_x] = "."  # Убираем ворону
                    add_message("Ворона погибла!")
                    dead_crow_count += 1
                    continue
                add_message(f"Ловушка нанесла {damage} урона вороне! Осталось {health} здоровья.")

            # Перемещаем ворону
            game_map[crow_y][crow_x] = "."  # Освобождаем старую клетку
            game_map[tree_y][tree_x] = "T"  # Убедимся, что символ дерева остаётся
            game_map[ny][nx] = "C"
            new_positions.append((nx, ny, health))
        else:
            # Если нет доступных ходов, ворона остаётся на месте
            new_positions.append((crow_x, crow_y, health))

    # Появление новой вороны при смерти 2
    if dead_crow_count >= 2 and random.random() < 0.5:  # 50% шанс
        for _ in range(10):  # До 10 попыток найти место на краю карты
            edge_x = random.choice([0, len(game_map[0]) - 1])
            edge_y = random.choice([0, len(game_map) - 1])
            if game_map[edge_y][edge_x] == ".":
                game_map[edge_y][edge_x] = "C"
                new_positions.append((edge_x, edge_y, 3))  # Новая ворона с 3 здоровьем
                add_message("На краю карты появилась новая ворона!")
                break

    # Появление босса или новых ворон при смерти всех
    if not new_positions and random.random() < 0.3:  # 50% шанс босса
        for _ in range(10):  # До 10 попыток найти место для босса
            boss_x = random.randint(1, len(game_map[0]) - 2)
            boss_y = random.randint(1, len(game_map) - 2)
            if game_map[boss_y][boss_x] == ".":
                game_map[boss_y][boss_x] = "C"
                new_positions.append((boss_x, boss_y, 5))  # Босс-ворона с 5 здоровьем
                add_message("Появилась босс-ворона с 5 здоровьем!")
                break
    elif not new_positions:  # Если босс не появился, создаём 3 обычных ворон
        for _ in range(3):
            for _ in range(10):  # До 10 попыток для каждой вороны
                crow_x = random.randint(1, len(game_map[0]) - 2)
                crow_y = random.randint(1, len(game_map) - 2)
                if game_map[crow_y][crow_x] == ".":
                    game_map[crow_y][crow_x] = "C"
                    new_positions.append((crow_x, crow_y, 3))
                    break
        add_message("Все вороны исчезли. Появилось 3 новых вороны!")

    return new_positions

def place_trap(game_map, player_pos, traps, add_message):
    """Устанавливает ловушку под игроком."""
    x, y = player_pos
    if traps > 0:
        if game_map[y][x] in [".", "@"]:
            game_map[y][x] = "^"
            traps -= 1
            add_message(f"Ловушка установлена в ({x}, {y}). Осталось ловушек: {traps}")
        else:
            add_message(f"Нельзя установить ловушку в ({x}, {y}): клетка занята ({game_map[y][x]}).")
    else:
        add_message("Ловушки закончились!")
    return traps

def draw_terminal(screen, messages):
    """Отрисовывает терминал сообщений."""
    font = pygame.font.SysFont("Courier", 16)
    terminal_rect = pygame.Rect(0, WINDOW_HEIGHT, WINDOW_WIDTH, TERMINAL_HEIGHT)
    pygame.draw.rect(screen, (0, 0, 0), terminal_rect)  # Фон терминала
    pygame.draw.rect(screen, (255, 255, 255), terminal_rect, 2)  # Рамка терминала

    for i, message in enumerate(messages[-5:]):  # Показываем последние 5 сообщений
        text_surface = font.render(message, True, (255, 255, 255))
        screen.blit(text_surface, (10, WINDOW_HEIGHT + i * 20))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT + TERMINAL_HEIGHT))
    pygame.display.set_caption("Mystic Tree Roguelike")
    clock = pygame.time.Clock()

    map_width = WINDOW_WIDTH // CELL_SIZE
    map_height = WINDOW_HEIGHT // CELL_SIZE

    game_map, player_pos, crow_positions = generate_map(map_width, map_height)
    tree_pos = [(x, y) for y, row in enumerate(game_map) for x, char in enumerate(row) if char == "T"][0]
    traps = 10
    messages = []  # Очередь сообщений в терминале
    step_count = 0  # Счётчик шагов для контроля частоты движения ворон

    def add_message(message):
        """Добавляет сообщение в терминал."""
        messages.append(message)
        if len(messages) > 10:  # Ограничиваем количество сообщений
            messages.pop(0)

    current_direction = None  # Направление движения игрока

    running = True
    while running:
        screen.fill((0, 0, 0))
        step_count += 1  # Увеличиваем счётчик шагов

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in directions:
                    current_direction = directions[event.key]
                elif event.key == pygame.K_f:
                    traps = place_trap(game_map, player_pos, traps, add_message)
            elif event.type == pygame.KEYUP:
                if event.key in directions:
                    current_direction = None

        if current_direction:
            player_pos = move_player(game_map, player_pos, current_direction)

        crow_positions = move_crows(game_map, crow_positions, tree_pos, add_message, step_count)

        draw_ascii_map(screen, game_map, crow_positions)  # Передаём crow_positions в функцию

        draw_terminal(screen, messages)

        font = pygame.font.SysFont("Courier", 24)
        health_surface = font.render(f"Tree Health: {TREE_HEALTH}", True, (255, 255, 255))
        screen.blit(health_surface, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

        if TREE_HEALTH <= 0:
            add_message("Game Over!")
            print("Game Over!")
            running = False

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
