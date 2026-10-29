import pygame
import time
from game_config import *
from game_interface import draw_interface, draw_ascii_map, draw_terminal
from map_generator import generate_map
from player import move_player
from crows import move_crows
from traps import place_trap, draw_trap_interface, update_traps
from mana import collect_mana, spawn_mana


def main():
    global selected_trap, TREE_HEALTH, PLAYER_HEALTH, PLAYER_MANA

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Mystic Tree Roguelike")
    clock = pygame.time.Clock()
    pygame.key.set_repeat(1, 100)

    game_map, player_pos, crow_positions = generate_map(WINDOW_WIDTH // CELL_SIZE, WINDOW_HEIGHT // CELL_SIZE)
    tree_pos = [(x, y) for y, row in enumerate(game_map) for x, char in enumerate(row) if char == "T"][0]

    traps = {k: 0 for k in trap_keys.values()}
    messages = []
    step_count = 0
    frozen_crows = {}
    projectiles = []
    previous_tile = '.'  # Инициализация предыдущей клетки

    def add_message(message):
        messages.append(message)
        if len(messages) > 10:
            messages.pop(0)

    current_direction = None
    game_over = False
    running = True

    while running:
        keys = pygame.key.get_pressed()
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key in directions:
                    current_direction = directions[event.key]
                elif event.key in trap_keys:
                    selected_trap = trap_keys[event.key]
                    add_message(f"Выбрана ловушка: {selected_trap.capitalize()}")
                elif event.key == pygame.K_f:
                    PLAYER_MANA = place_trap(game_map, player_pos, PLAYER_MANA, traps, add_message, selected_trap)

            elif event.type == pygame.KEYUP:
                if event.key in directions:
                    current_direction = None

        if not running:
            break

        if current_direction:
            # Обновленный вызов move_player с передачей всех аргументов
            player_pos, PLAYER_MANA, previous_tile = move_player(game_map, player_pos, current_direction, PLAYER_MANA, previous_tile)

        # Проверка здоровья дерева
        if TREE_HEALTH <= 0:
            add_message("Дерево уничтожено! Игра окончена.")
            game_over = True
            running = False

        PLAYER_MANA = collect_mana(game_map, player_pos, PLAYER_MANA)

        if game_map[player_pos[1]][player_pos[0]] == "s":
            TRAPS["shooter"]["shots_left"] = 5
            game_map[player_pos[1]][player_pos[0]] = "S"
            add_message("Стрелковая ловушка перезарядилась!")

        TREE_HEALTH, PLAYER_HEALTH, PLAYER_MANA, projectiles = update_traps(
            game_map, player_pos, TREE_HEALTH, PLAYER_HEALTH, crow_positions, add_message, PLAYER_MANA, step_count,
            projectiles
        )

        if step_count % (FPS * 15) == 0:
            spawn_mana(game_map)

        crow_positions, TREE_HEALTH, frozen_crows = move_crows(
            game_map, crow_positions, tree_pos, add_message, step_count, TREE_HEALTH, frozen_crows
        )
        if not game_over:
            draw_interface(screen, TREE_HEALTH, PLAYER_HEALTH, PLAYER_MANA)
            draw_trap_interface(screen, traps, selected_trap)
            draw_ascii_map(screen, game_map, crow_positions, projectiles)
            draw_terminal(screen, messages)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()

if __name__ == "__main__":
    main()
