def move_player(game_map, player_pos, direction, mana, previous_tile):
    """Перемещение игрока с сохранением ловушек и корректным восстановлением клетки."""
    from mana import collect_mana

    x, y = player_pos
    dx, dy = direction
    new_x, new_y = x + dx, y + dy

    # Разрешённые клетки для движения (включая "s" — разряженную стрелковую ловушку)
    passable_tiles = [".", "*", "B", "B2", "S", "s", "F", "P", "R"]

    # Проверяем границы карты
    if 0 <= new_x < len(game_map[0]) and 0 <= new_y < len(game_map):
        target_cell = game_map[new_y][new_x]

        if target_cell in passable_tiles:
            # Подбор маны
            if target_cell == "*":
                mana = collect_mana(game_map, (new_x, new_y), mana)

            # Перезарядка стрелковой ловушки, если игрок встал на "s"
            if target_cell == "s":
                game_map[new_y][new_x] = "S"  # Возвращаем в заряженное состояние

            # Восстанавливаем клетку, на которой стоял игрок
            if game_map[y][x] == "@":
                game_map[y][x] = previous_tile

            # Запоминаем клетку, на которую встаёт игрок
            previous_tile = target_cell if target_cell in ["B", "B2", "S", "s", "F", "P", "R"] else "."

            # Перемещаем игрока
            player_pos = (new_x, new_y)
            game_map[new_y][new_x] = "@"

            return player_pos, mana, previous_tile

    return player_pos, mana, previous_tile  # Если движение невозможно
