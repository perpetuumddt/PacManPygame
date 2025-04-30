import pytest
import pygame
from game import Game

@pytest.fixture
def game_instance():
    screen = pygame.Surface((720, 780))
    return Game(screen, exit_callback=lambda: None, current_level=1)

def test_game_initialization(game_instance):
    assert game_instance.lives == 3
    assert game_instance.score == 0
    assert not game_instance.powerup

def test_reset_game_state(game_instance):
    game_instance.lives = 1
    game_instance.score = 100
    game_instance.powerup = True
    game_instance.reset_game_state()
    assert game_instance.lives == 3
    assert game_instance.score == 0
    assert not game_instance.powerup