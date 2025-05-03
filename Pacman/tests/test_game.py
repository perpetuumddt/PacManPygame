import sys
import os
import pytest
import pygame
from unittest.mock import patch

# Add project root to sys.path so Python can find game.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game import Game, Pacman

@pytest.fixture
def game_instance():
    screen = pygame.Surface((720, 780))

    # Mock pygame.image.load to return a dummy surface instead of loading real files
    with patch('pygame.image.load', return_value=pygame.Surface((33, 33))):
        return Game(screen, exit_callback=lambda: None, current_level=1)

@pytest.fixture
def pacman_instance(game_instance):
    return game_instance.pacman

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
