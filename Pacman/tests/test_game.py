import sys
import os
import pytest
import pygame
from unittest.mock import patch

# Add project root to sys.path so Python can find game.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game import Game, Pacman, Board

@pytest.fixture
def game_instance():
    screen = pygame.Surface((720, 780))

    # Mock pygame.image.load to return a dummy surface instead of loading real files
    with patch('pygame.image.load', return_value=pygame.Surface((33, 33))):
        return Game(screen, exit_callback=lambda: None, current_level=1)

@pytest.fixture
def pacman_instance(game_instance):
    return game_instance.pacman

@pytest.fixture
def board_instance(game_instance):
    return game_instance.board


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
    pacman_instance.x = 691
    pacman_instance.direction = 0  # Move right
    pacman_instance.turns_allowed = [True, True, True, True]
    pacman_instance.move()
    assert pacman_instance.x == -35

    pacman_instance.x = -38
    pacman_instance.direction = 1  # Move left
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
