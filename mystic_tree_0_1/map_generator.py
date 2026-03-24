import random


def initialize_empty_map(width, height):
    """Создаёт карту, полностью заполненную стенами."""
    return [["#" for _ in range(width)] for _ in range(height)]


def get_neighbors(x, y, width, height, step=2):
    """Возвращает список соседей для клетки (x, y) с заданным шагом."""
    neighbors = []
    if x - step > 0:
        neighbors.append((x - step, y))
    if x + step < width - 1:  # Граница карты
        neighbors.append((x + step, y))
    if y - step > 0:
        neighbors.append((x, y - step))
    if y + step < height - 1:  # Граница карты
        neighbors.append((x, y + step))
    return neighbors


def generate_labyrinth(width, height):
    """Генерирует лабиринт с алгоритмом 'Growing Tree'."""
    game_map = initialize_empty_map(width, height)

    # Начальная точка
    start_x, start_y = random.randrange(1, width, 2), random.randrange(1, height, 2)
    game_map[start_y][start_x] = "."
    active_cells = [(start_x, start_y)]

    while active_cells:
        current_x, current_y = random.choice(active_cells)

        neighbors = get_neighbors(current_x, current_y, width, height, step=2)
        unvisited = [(nx, ny) for nx, ny in neighbors if game_map[ny][nx] == "#"]

        if unvisited:
            next_x, next_y = random.choice(unvisited)
            wall_x, wall_y = (current_x + next_x) // 2, (current_y + next_y) // 2

            # Пробиваем путь
            game_map[wall_y][wall_x] = "."
            game_map[next_y][next_x] = "."

            # Увеличиваем ширину путей с вероятностью 90%
            if random.random() < 0.9:
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if 1 <= next_x + dx < width - 1 and 1 <= next_y + dy < height - 1:
                            if random.random() < 0.5:
                                game_map[next_y + dy][next_x + dx] = "."

            active_cells.append((next_x, next_y))
        else:
            active_cells.remove((current_x, current_y))

    # Добавляем дополнительные проходы
    add_extra_passages(game_map, width, height)

    return game_map


def add_extra_passages(game_map, width, height, extra_passages=15):
    """Добавляет дополнительные проходы для большей связанности."""
    for _ in range(extra_passages):
        x, y = random.randrange(1, width - 1), random.randrange(1, height - 1)
        if game_map[y][x] == "#":
            neighbors = get_neighbors(x, y, width, height, step=1)
            if sum(1 for nx, ny in neighbors if game_map[ny][nx] == ".") >= 2:
                game_map[y][x] = "."


def generate_map(width, height):
    """Создаёт лабиринт, добавляет дерево, игрока и ворон."""
    game_map = generate_labyrinth(width, height)

    # Убедимся, что по краям всегда есть стены
    for x in range(width):
        game_map[0][x] = "#"
        game_map[height - 1][x] = "#"
    for y in range(height):
        game_map[y][0] = "#"
        game_map[y][width - 1] = "#"

    # Расположение дерева (T)
    while True:
        tree_x, tree_y = random.randint(1, width - 2), random.randint(1, height - 2)
        if game_map[tree_y][tree_x] == ".":
            game_map[tree_y][tree_x] = "T"
            break

    # Расположение игрока (@)
    while True:
        player_x, player_y = random.randint(1, width - 2), random.randint(1, height - 2)
        if game_map[player_y][player_x] == ".":
            game_map[player_y][player_x] = "@"
            break

        # Размещение ворон с начальным здоровьем
    crow_positions = []
    for _ in range(5):  # Количество ворон
        while True:
            crow_x, crow_y = random.randint(1, width - 2), random.randint(1, height - 2)
            if game_map[crow_y][crow_x] == ".":
                game_map[crow_y][crow_x] = "C"
                crow_positions.append((crow_x, crow_y, 3))  # Начальное здоровье 3
                break

    return game_map, (player_x, player_y), crow_positions
