import pygame

TRAPS = {
    "bomb": {"cost": 20, "health": 2, "symbol": "B", "color": (255, 255, 0)},
    "shooter": {"cost": 50, "health": 3, "symbol": "S", "color": (0, 255, 0), "shots_left": 5, "reload_cost": 10},
    "freeze": {"cost": 100, "health": 5, "symbol": "F", "color": (0, 0, 255), "cooldown": 25, "last_used": 0, "active": False},
    "bait": {"cost": 25, "health": 2, "symbol": "P", "color": (255, 182, 193)},
    "heal_rune": {"cost": 80, "health": 1, "symbol": "R", "color": (0, 255, 255), "last_heal": 0, "heal_interval": 5},
}


def place_trap(game_map, player_pos, mana, traps, add_message, selected_trap):
    """Устанавливает ловушку под игроком."""
    x, y = player_pos
    trap = TRAPS[selected_trap]

    if mana >= trap["cost"]:
        if game_map[y][x] in [".", "@"]:  # Проверка на свободное место
            game_map[y][x] = trap["symbol"]
            traps[selected_trap] += 1
            mana -= trap["cost"]
            add_message(f"Ловушка {selected_trap.capitalize()} установлена на ({x}, {y}).")
        else:
            add_message(f"Нельзя установить ловушку на ({x}, {y}): клетка занята.")
    else:
        add_message(f"Недостаточно маны для установки ловушки {selected_trap.capitalize()}.")

    return mana

import time

def update_traps(game_map, player_pos, tree_health, player_health, crow_positions, add_message, mana, step_count, projectiles):
    """Обновляет состояние ловушек, включая стрельбу, заморозку, приманку и лечение."""
    current_time = time.time()

    if not isinstance(projectiles, list):
        projectiles = []

    if not isinstance(step_count, int):
        step_count = 0

    new_projectiles = []  # Новый список для обновлённых снарядов

    for y, row in enumerate(game_map):
        for x, cell in enumerate(row):

            # --- Стрелковая ловушка (Shooter Trap) ---
            if cell in ["S", "s"]:
                trap = TRAPS["shooter"]

                # Если патроны кончились, но ещё не сменился символ - меняем на "s"
                if trap["shots_left"] == 0 and game_map[y][x] == "S":
                    game_map[y][x] = "s"

                # Стреляет раз в 90 кадров (1.5 секунды)
                if trap["shots_left"] > 0 and step_count % 90 == 0:
                    for i, (crow_x, crow_y, health) in enumerate(crow_positions):
                        if abs(crow_x - x) <= 3 and abs(crow_y - y) <= 3:
                            trap["shots_left"] -= 1
                            new_projectiles.append({"x": x, "y": y, "tx": crow_x, "ty": crow_y, "start_time": time.time()})
                            break

                # Перезарядка "s" возможна только если игрок встал на неё
                if game_map[player_pos[1]][player_pos[0]] == "s" and trap["shots_left"] == 0:
                    trap["shots_left"] = 5
                    game_map[player_pos[1]][player_pos[0]] = "S"
                    add_message("Стрелковая ловушка перезарядилась!")

            # --- Замораживающая ловушка (Freeze Trap) ---
            elif cell == "F":
                trap = TRAPS["freeze"]
                if not trap["active"] and current_time - trap["last_used"] > trap["cooldown"]:
                    trap["active"] = True
                    trap["last_used"] = current_time
                    add_message("Замораживающая ловушка активирована! Вороны заморожены на 5 секунд.")

                    for i, (cx, cy, health) in enumerate(crow_positions):
                        if abs(cx - x) <= 3 and abs(cy - y) <= 3:
                            crow_positions[i] = (cx, cy, health, "frozen")

            # --- Приманка (Bait Trap) ---
            elif cell == "P":
                for i, (cx, cy, health) in enumerate(crow_positions):
                    if abs(cx - x) <= 7 and abs(cy - y) <= 7:
                        if step_count % 20 == 0:
                            new_x = cx + (x - cx) // max(1, abs(x - cx))
                            new_y = cy + (y - cy) // max(1, abs(y - cy))
                            crow_positions[i] = (new_x, new_y, health)

            # --- Исцеляющая руна (Healing Rune) ---
            elif cell == "R":
                trap = TRAPS["heal_rune"]
                if current_time - trap["last_heal"] > trap["heal_interval"]:
                    trap["last_heal"] = current_time
                    if tree_health < 10:
                        tree_health += 1
                        add_message("Исцеляющая руна восстановила 1 здоровье дереву!")
                    elif player_health < 4:
                        player_health += 1
                        add_message("Исцеляющая руна восстановила 1 здоровье игроку!")

    # Обновление анимации снарядов (сильное замедление)
    updated_projectiles = []
    for proj in projectiles + new_projectiles:
        px, py, target_x, target_y, start_time = proj["x"], proj["y"], proj["tx"], proj["ty"], proj["start_time"]
        progress = min(1, (time.time() - start_time) * 0.01)  # Ещё большее замедление

        proj_x = int(px + (target_x - px) * progress)
        proj_y = int(py + (target_y - py) * progress)

        # Проверяем столкновение с препятствием
        if game_map[proj_y][proj_x] in ["#", "B", "B2", "S", "s", "F", "P", "R", "@"]:
            continue  # Если снаряд врезался во что-то, он пропадает

        # Если снаряд достиг цели
        if proj_x == target_x and proj_y == target_y:
            for i, (cx, cy, health) in enumerate(crow_positions):
                if cx == proj_x and cy == proj_y:
                    crow_positions[i] = (cx, cy, health - 1)  # Наносим урон вороне
                    add_message(f"Ворона получила урон от стрелковой ловушки! Осталось здоровья: {health-1}")
                    if health - 1 <= 0:
                        game_map[cy][cx] = "."  # Убираем ворону с карты
                        crow_positions.pop(i)
            continue  # Удаляем снаряд
        else:
            updated_projectiles.append({"x": proj_x, "y": proj_y, "tx": target_x, "ty": target_y, "start_time": start_time})

    return tree_health, player_health, mana, updated_projectiles

def draw_trap_interface(screen, traps, selected_trap):
    """Отрисовывает интерфейс для ловушек с подсветкой выбранной ловушки."""
    font = pygame.font.SysFont("Courier", 16)
    start_x = 1200 - 200  # Начальная позиция для отображения ловушек
    start_y = 10

    # Отображаем каждую ловушку с её статусом
    for idx, (trap_name, trap_data) in enumerate(TRAPS.items(), start=1):
        color = trap_data["color"]
        if trap_name == selected_trap:  # Подсветка выбранной ловушки
            color = (255, 255, 255)  # Белый цвет для выделения
            background_rect = pygame.Rect(start_x - 5, start_y - 2, 180, 22)
            pygame.draw.rect(screen, (50, 50, 50), background_rect)  # Фон подсветки

        # Проверяем, есть ли ловушка в `traps`, если нет - ставим 0
        trap_count = traps.get(trap_name, 0)

        trap_text = f"{idx}. {trap_name.capitalize()} ({trap_count} шт.)"
        text_surface = font.render(trap_text, True, color)
        screen.blit(text_surface, (start_x, start_y))
        start_y += 25  # Смещаем вниз для следующей строки
