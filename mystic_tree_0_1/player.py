def move_player(game_map, player_pos, direction):
    """Перемещение игрока с учётом обхода стен."""
    x, y = player_pos
    dx, dy = direction
    new_x, new_y = x + dx, y + dy

    # Проверяем, можно ли переместиться вперёд
    if 0 <= new_x < len(game_map[0]) and 0 <= new_y < len(game_map):  # Границы карты
        if game_map[new_y][new_x] in [".", "^"]:  # Пустая клетка или ловушка
            # Сохраняем символ ловушки, если игрок её покидает
            if game_map[y][x] == "@":
                game_map[y][x] = "^" if game_map[y][x] == "^" else "."
            # Перемещаем игрока
            player_pos = (new_x, new_y)
            # Если игрок встал на ловушку, ловушка остаётся
            if game_map[new_y][new_x] == "^":
                game_map[new_y][new_x] = "^"
            else:
                game_map[new_y][new_x] = "@"
            return player_pos

    # Если перед нами стена, проверяем возможность обхода
    if game_map[new_y][new_x] == "#":
        side_directions = [(-dy, dx), (dy, -dx)]  # Слева и справа
        for side_dx, side_dy in side_directions:
            side_x, side_y = x + side_dx, y + side_dy
            if (
                0 <= side_x < len(game_map[0])
                and 0 <= side_y < len(game_map)
                and game_map[side_y][side_x] in [".", "^"]
            ):
                if game_map[y][x] == "@":
                    game_map[y][x] = "^" if game_map[y][x] == "^" else "."
                player_pos = (side_x, side_y)
                # Сохраняем ловушку, если она на новой клетке
                if game_map[side_y][side_x] == "^":
                    game_map[side_y][side_x] = "^"
                else:
                    game_map[side_y][side_x] = "@"
                return player_pos

    return player_pos  # Если движение невозможно
