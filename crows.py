import random
import time


def handle_trap_interaction(game_map, x, y, health, trap_type, add_message, frozen_crows):
    """Обрабатывает взаимодействие вороны с различными типами ловушек."""

    if trap_type == "B":  # Ловушка-бомба (первое срабатывание)
        health -= 3
        game_map[y][x] = "B2"  # Меняем состояние ловушки
        add_message(f"Ловушка-бомба нанесла 3 урона вороне. Осталось здоровья: {health}")

    elif trap_type == "B2":  # Ловушка-бомба (второе срабатывание)
        health -= 1
        game_map[y][x] = "."  # Удаляем ловушку
        add_message(f"Ловушка-бомба нанесла 1 урон вороне и исчезла. Осталось здоровья: {health}")

    elif trap_type == "S":  # Стрелковая ловушка
        health -= 1
        add_message(f"Стрелковая ловушка нанесла 1 урон вороне. Осталось здоровья: {health}")

    elif trap_type == "F":  # Замораживающая ловушка
        frozen_crows[(x, y)] = time.time()  # Добавляем ворону в список замороженных
        add_message("Замораживающая ловушка активирована! Ворона заморожена на 5 секунд.")

    elif trap_type == "P":  # Приманка
        add_message("Ворона привлеклась к приманке.")

    elif trap_type == "R":  # Исцеляющая руна
        add_message("Исцеляющая руна не влияет на ворон.")

    return health


def move_crows(game_map, crow_positions, tree_pos, add_message, step_count, tree_health, frozen_crows):
    """Движение ворон с учётом ловушек, атак дерева, замораживания и приманок."""
    new_positions = []
    tree_x, tree_y = tree_pos
    dead_crow_count = 0  # Счётчик убитых ворон

    # Замедляем движение ворон: двигаются каждые 15 кадров
    if step_count % 15 != 0:
        return crow_positions, tree_health, frozen_crows

    for crow in crow_positions:
        crow_x, crow_y, health = crow

        # Проверяем, заморожена ли ворона
        if (crow_x, crow_y) in frozen_crows:
            if time.time() - frozen_crows[(crow_x, crow_y)] < 5:  # Заморожена на 5 секунд
                new_positions.append((crow_x, crow_y, health))
                continue
            else:
                del frozen_crows[(crow_x, crow_y)]  # Разморозка

        # Если ворона находится на соседней клетке дерева
        if abs(crow_x - tree_x) <= 1 and abs(crow_y - tree_y) <= 1:
            tree_health -= 1
            add_message(f"Ворона атаковала дерево! У дерева осталось {tree_health} здоровья.")
            health -= 1
            if health <= 0:
                add_message("Ворона погибла, атаковав дерево!")
                dead_crow_count += 1
                game_map[crow_y][crow_x] = "."  # Убираем ворону с карты
                continue
            # Перемещаем ворону на случайное место в пределах 4 клеток
            for _ in range(10):
                offset_x = random.randint(-4, 4)
                offset_y = random.randint(-4, 4)
                new_x, new_y = crow_x + offset_x, crow_y + offset_y
                if 0 <= new_x < len(game_map[0]) and 0 <= new_y < len(game_map) and game_map[new_y][new_x] == ".":
                    game_map[crow_y][crow_x] = "."
                    game_map[new_y][new_x] = "C"
                    new_positions.append((new_x, new_y, health))
                    break
            else:
                new_positions.append((crow_x, crow_y, health))
            continue

        # Приманка: ворон тянет к приманке в радиусе 5 клеток
        for y, row in enumerate(game_map):
            for x, cell in enumerate(row):
                if cell == "P" and abs(crow_x - x) <= 5 and abs(crow_y - y) <= 5:
                    move_x = 1 if x > crow_x else -1 if x < crow_x else 0
                    move_y = 1 if y > crow_y else -1 if y < crow_y else 0
                    crow_x += move_x
                    crow_y += move_y
                    add_message(f"Ворона движется к приманке на ({x}, {y})")
                    break

        # Случайное перемещение (50% шанс)
        if random.random() < 0.5:
            for _ in range(10):
                offset_x = random.randint(-2, 2)
                offset_y = random.randint(-2, 2)
                new_x, new_y = crow_x + offset_x, crow_y + offset_y
                if 0 <= new_x < len(game_map[0]) and 0 <= new_y < len(game_map) and game_map[new_y][new_x] == ".":
                    game_map[crow_y][crow_x] = "."
                    game_map[new_y][new_x] = "C"
                    new_positions.append((new_x, new_y, health))
                    break
            else:
                new_positions.append((crow_x, crow_y, health))
            continue

        # Движение к дереву
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        valid_moves = []
        for dx, dy in directions:
            nx, ny = crow_x + dx, crow_y + dy
            if 0 <= nx < len(game_map[0]) and 0 <= ny < len(game_map) and game_map[ny][nx] not in ["#", "T"]:
                valid_moves.append((nx, ny))

        if valid_moves:
            closest_move = min(valid_moves, key=lambda pos: abs(pos[0] - tree_x) + abs(pos[1] - tree_y))
            nx, ny = closest_move

            # Проверяем взаимодействие с ловушкой
            if game_map[ny][nx] in ["B", "B2", "S", "F", "P", "R"]:
                trap_type = game_map[ny][nx]
                health = handle_trap_interaction(game_map, nx, ny, health, trap_type, add_message, frozen_crows)
                if health <= 0:
                    add_message("Ворона погибла от ловушки!")
                    game_map[crow_y][crow_x] = "."
                    dead_crow_count += 1
                    continue

            # Перемещаем ворону
            game_map[crow_y][crow_x] = "."
            game_map[ny][nx] = "C"
            new_positions.append((nx, ny, health))
        else:
            new_positions.append((crow_x, crow_y, health))

    # Появление новой вороны при смерти 2
    if dead_crow_count >= 2 and random.random() < 0.5:
        for _ in range(10):
            edge_x = random.choice([0, len(game_map[0]) - 1])
            edge_y = random.choice([0, len(game_map) - 1])
            if game_map[edge_y][edge_x] == ".":
                game_map[edge_y][edge_x] = "C"
                new_positions.append((edge_x, edge_y, 3))
                add_message("На краю карты появилась новая ворона!")
                break

    # Появление босса или новых ворон при смерти всех
    if not new_positions and random.random() < 0.7:  # 70% шанс босса
        new_positions.append((random.randint(1, len(game_map[0]) - 2), random.randint(1, len(game_map) - 2), 5))
        add_message("Появилась босс-ворона с 5 здоровьем!")
    elif not new_positions:
        new_positions.extend([(random.randint(1, len(game_map[0]) - 2), random.randint(1, len(game_map) - 2), 3) for _ in range(3)])
        add_message("Все вороны исчезли. Появилось 3 новых вороны!")

    return new_positions, tree_health, frozen_crows
