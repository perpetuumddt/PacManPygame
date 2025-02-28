import pygame
from menu import Menu
from game import Game

pygame.init()
screen = pygame.display.set_mode((720, 780))
pygame.display.set_caption("Pac-Man")

# Game state
MENU = "menu"
GAME = "game"
state = MENU

while True:
    if state == MENU:
        menu = Menu(screen, lambda: setattr(globals(), "state", GAME))
        menu.run()
    elif state == GAME:
        game = Game(screen)
        game.run()