import sys
import os
import pytest
import pygame
from unittest.mock import patch

# Add project root to sys.path so Python can find game.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game import Game, Pacman, Board, Ghost

@pytest.fixture
def game_instance():
    screen = pygame.Surface((720, 780))

    # Mock pygame.image.load to return a dummy surface instead of loading real files
    with patch('pygame.image.load', return_value=pygame.Surface((33, 33))):
        game = Game(screen, exit_callback=lambda: None, current_level=1)
        # Ensure ghosts are initialized after mocking image load
        game.blinky = Ghost(game, 45, 46, (0, 0), 1, None, 0, False, False, 0)
        game.inky = Ghost(game, 352, 305, (0, 0), 1, None, 2, False, False, 1)
        game.pinky = Ghost(game, 352, 345, (0, 0), 1, None, 2, False, False, 2)
        game.clyde = Ghost(game, 352, 345, (0, 0), 1, None, 2, False, False, 3)
        return game

@pytest.fixture
def pacman_instance(game_instance):
    return game_instance.pacman

@pytest.fixture
def board_instance(game_instance):
    return game_instance.board

@pytest.fixture
def blinky_instance(game_instance):
    return game_instance.blinky

@pytest.fixture
def inky_instance(game_instance):
    return game_instance.inky

@pytest.fixture
def pinky_instance(game_instance):
    return game_instance.pinky

@pytest.fixture
def clyde_instance(game_instance):
    return game_instance.clyde

# Test: Initial values should be set properly
def test_game_initialization(game_instance):
    assert game_instance.lives == 3
    assert game_instance.score == 0
    assert not game_instance.powerup

# Test: Resetting game should restore initial state
def test_reset_game_state(game_instance):
    game_instance.lives = 1
    game_instance.score = 100
    game_instance.powerup = True

    game_instance.reset_game_state()

    assert game_instance.lives == 3
    assert game_instance.score == 0
    assert not game_instance.powerup

# Test: Pacman update method
@pytest.mark.parametrize("direction_command, turns_allowed, expected_direction", [
    (0, [True, False, False, False], 0),  # Can turn right
    (1, [False, True, False, False], 1),  # Can turn left
    (2, [True, False, False, False], 0),  # Cant turn up
    (3, [False, False, False, False], 0),  # Cant turn down
])
def test_pacman_update(pacman_instance, direction_command, turns_allowed, expected_direction):
    pacman_instance.direction_command = direction_command
    pacman_instance.turns_allowed = turns_allowed
    pacman_instance.update()
    assert pacman_instance.direction == expected_direction

# Test: Pacman move method
@pytest.mark.parametrize("direction, turns_allowed, expected_x, expected_y", [
    (0, [True, False, False, False], 362, 522),  # Move right
    (1, [False, True, False, False], 358, 522),  # Move left
    (2, [False, False, True, False], 360, 520),  # Move up
    (3, [False, False, False, True], 360, 524),  # Move down
])
def test_pacman_move(pacman_instance, direction, turns_allowed, expected_x, expected_y):
    pacman_instance.direction = direction
    pacman_instance.turns_allowed = turns_allowed
    pacman_instance.move()
    assert pacman_instance.x == expected_x
    assert pacman_instance.y == expected_y

# Test: Pacman screen wrapping
def test_pacman_screen_wrap(pacman_instance):
    pacman_instance.x = 692
    pacman_instance.move()
    assert pacman_instance.x == -35

    pacman_instance.x = -39
    pacman_instance.move()
    assert pacman_instance.x == 691

# Test: Pacman get_player_rect method
def test_pacman_get_player_rect(pacman_instance):
    pacman_instance.x = 100
    pacman_instance.y = 150
    rect = pacman_instance.get_player_rect()
    assert rect.x == 100 + 16 - 16
    assert rect.y == 150 + 17 - 16
    assert rect.width == 32
    assert rect.height == 32

# Test: Board check_position method
@pytest.mark.parametrize("centerx, centery, expected_turns", [
    (116, 117, [False, False, False, False]),  # No turns allowed
    (376, 539, [True, True, False, False]),      # All turns allowed
])
def test_board_check_position(board_instance, centerx, centery, expected_turns):
    turns = board_instance.check_position(centerx, centery)
    assert turns == expected_turns

# Test: Board check_collisions method
def test_board_check_collisions(board_instance, game_instance):
    game_instance.level = [[0] * 30 for _ in range(32)]
    game_instance.level[3][3] = 1  # Place a pellet
    game_instance.pacman.x, game_instance.pacman.y = 66, 68  # Near the pellet
    score, powerup, power_counter, eaten_ghost = board_instance.check_collisions()
    assert score == 10
    assert game_instance.level[3][3] == 0
    assert not powerup
    assert power_counter == 0
    assert eaten_ghost == [False, False, False, False]

def test_ghost_initialization(blinky_instance):
    assert blinky_instance.x_pos == 45
    assert blinky_instance.y_pos == 46
    assert blinky_instance.speed == 1
    assert not blinky_instance.dead
    assert not blinky_instance.in_box
    assert blinky_instance.id == 0
    assert isinstance(blinky_instance.rect, pygame.Rect)

def test_ghost_update(blinky_instance):
    initial_x = blinky_instance.x_pos
    initial_y = blinky_instance.y_pos
    blinky_instance.x_pos += 5
    blinky_instance.y_pos += 5
    blinky_instance.update()
    assert blinky_instance.center_x == blinky_instance.x_pos + 16
    assert blinky_instance.center_y == blinky_instance.y_pos + 17
    assert blinky_instance.rect.topleft == (
    blinky_instance.center_x - 13, blinky_instance.center_y - 13)  # Check rect update

def test_ghost_check_collisions_wall(blinky_instance, game_instance):
    # Mock level to have a wall to the right
    game_instance.level = [[0] * 30 for _ in range(32)]
    game_instance.level[1][2] = 3  # Vertical wall
    blinky_instance.x_pos = 58
    blinky_instance.y_pos = 49
    blinky_instance.direction = 0 # Moving right
    turns, in_box = blinky_instance.check_collisions()
    assert turns[0] # Cannot turn right

def test_ghost_check_collisions_in_box(blinky_instance, game_instance):
    blinky_instance.x_pos = 300
    blinky_instance.y_pos = 320
    turns, in_box = blinky_instance.check_collisions()
    assert in_box

@pytest.mark.parametrize("powerup, pacman_collided, ghost_dead, eaten_ghost_state, lives_before, score_before, lives_after, score_after, ghost_dead_after, eaten_ghost_after", [
    (True, True, False, [False, False, False, False], 3, 0, 3, 200, True, [True, False, False, False]),  # Powerup, collide, eat first ghost
    (True, True, True, [True, False, False, False], 3, 200, 3, 200, True, [True, False, False, False]),  # Powerup, collide with dead ghost, no effect
    (True, True, False, [True, True, False, False], 3, 200, 2, 0, False, [False, True, True, False]),  # Powerup, collide, eat third ghost
])
def test_game_check_pacman_ghosts_collision(game_instance, pacman_instance, blinky_instance, powerup, pacman_collided, ghost_dead, eaten_ghost_state, lives_before, score_before, lives_after, score_after, ghost_dead_after, eaten_ghost_after):
    game_instance.powerup = powerup
    game_instance.lives = lives_before
    game_instance.score = score_before
    game_instance.eaten_ghost = eaten_ghost_state
    blinky_instance.dead = ghost_dead

    if pacman_collided:
        pacman_instance.x = blinky_instance.x_pos
        pacman_instance.y = blinky_instance.y_pos

    game_instance.check_pacman_ghosts_collision()

    assert game_instance.lives == lives_after
    assert game_instance.score == score_after
    assert game_instance.blinky.dead == ghost_dead_after
    assert game_instance.eaten_ghost[0] == eaten_ghost_after[0]

def test_ghost_move_clyde_no_turns(clyde_instance, game_instance):
    game_instance.level = [[0] * 30 for _ in range(32)]
    clyde_instance.x_pos = 100
    clyde_instance.y_pos = 100
    clyde_instance.direction = 0
    clyde_instance.target = (200, 100)
    clyde_instance.speed = 1
    clyde_instance.check_collisions = lambda: ([True, False, False, False], False) # Mock no turns except right
    initial_x = clyde_instance.x_pos
    clyde_instance.move_clyde()
    assert clyde_instance.x_pos > initial_x

def test_ghost_move_blinky_no_turns(blinky_instance, game_instance):
    game_instance.level = [[0] * 30 for _ in range(32)]
    blinky_instance.x_pos = 100
    blinky_instance.y_pos = 100
    blinky_instance.direction = 0
    blinky_instance.target = (200, 100)
    blinky_instance.speed = 1
    blinky_instance.check_collisions = lambda: ([True, False, False, False], False) # Mock no turns except right
    initial_x = blinky_instance.x_pos
    blinky_instance.move_blinky()
    assert blinky_instance.x_pos > initial_x

def test_ghost_move_inky_no_turns(inky_instance, game_instance):
    game_instance.level = [[0] * 30 for _ in range(32)]
    inky_instance.x_pos = 100
    inky_instance.y_pos = 100
    inky_instance.direction = 0
    inky_instance.target = (200, 100)
    inky_instance.speed = 1
    inky_instance.check_collisions = lambda: ([True, False, False, False], False) # Mock no turns except right
    initial_x = inky_instance.x_pos
    inky_instance.move_inky()
    assert inky_instance.x_pos > initial_x

def test_ghost_move_pinky_no_turns(pinky_instance, game_instance):
    game_instance.level = [[0] * 30 for _ in range(32)]
    pinky_instance.x_pos = 100
    pinky_instance.y_pos = 100
    pinky_instance.direction = 0
    pinky_instance.target = (200, 100)
    pinky_instance.speed = 1
    pinky_instance.check_collisions = lambda: ([True, False, False, False], False) # Mock no turns except right
    initial_x = pinky_instance.x_pos
    pinky_instance.move_pinky()
    assert pinky_instance.x_pos > initial_x