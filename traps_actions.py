import random

def trigger_bomb_trap(game_map, x, y, crow_health, add_message):
    """Обрабатывает взрыв ловушки-бомбы."""
    if game_map[y][x] == "B":
        damage = 3 if crow_health > 1 else 1
        crow_health -= damage
        game_map[y][x] = "." if crow_health <= 0 else "B"
        add_message(f"Ловушка-бомба нанесла {damage} урона вороне.")
    return crow_health

def trigger_shooter_trap(game_map, x, y, crows, add_message):
    """Обрабатывает стрельбу ловушки в радиусе."""
    for crow_x, crow_y, health in crows:
        if abs(crow_x - x) <= 3 and abs(crow_y - y) <= 3:  # Радиус стрельбы
            health -= 1
            add_message(f"Стрелковая ловушка нанесла 1 урона вороне на ({crow_x}, {crow_y}).")
            if health <= 0:
                game_map[crow_y][crow_x] = "."
            break

def trigger_freeze_trap(game_map, x, y, crows, add_message):
    """Замораживает ворон в радиусе."""
    for crow_x, crow_y, _ in crows:
        if abs(crow_x - x) <= 5 and abs(crow_y - y) <= 5:
            add_message(f"Замораживающая ловушка активирована. Все вороны заморожены на 5 секунд!")
            return True
    return False

def trigger_bait_trap(game_map, x, y, crows, add_message):
    """Привлекает ворон к приманке."""
    for crow_x, crow_y, _ in crows:
        if abs(crow_x - x) <= 5 and abs(crow_y - y) <= 5:
            add_message("Приманка привлекла ворону!")
            game_map[crow_y][crow_x] = "."
            game_map[y][x] = "P"
            break

def trigger_heal_rune(game_map, tree_health, player_health, add_message):
    """Лечит дерево или игрока."""
    target = random.choice(["tree", "player"])
    if target == "tree" and tree_health < 10:
        tree_health += 1
        add_message("Исцеляющая руна восстановила 1 здоровье дереву!")
    elif target == "player" and player_health < 4:
        player_health += 1
        add_message("Исцеляющая руна восстановила 1 здоровье игроку!")
    return tree_health, player_health
