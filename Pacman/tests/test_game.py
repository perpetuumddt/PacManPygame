import sys
import os
import pytest
import pygame

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game import Game

#fixture creates a new instance of the game class before each test
@pytest.fixture
def game_instance():
    screen = pygame.Surface((720, 780))
    return Game(screen, exit_callback=lambda: None, current_level=1)

#Test: Game initialization should set default values.
def test_game_initialization(game_instance):
    assert game_instance.lives == 3
    assert game_instance.score == 0
    assert not game_instance.powerup

#Test: Reset game method should reset game attributes
# simulates attribute change, then restarts game state and checks values
def test_reset_game_state(game_instance):
    game_instance.lives = 1
    game_instance.score = 100
    game_instance.powerup = True
    game_instance.reset_game_state()
    assert game_instance.lives == 3
    assert game_instance.score == 0
    assert not game_instance.powerup