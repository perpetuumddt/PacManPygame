import pygame
from menu import Menu
from game import Game

pygame.init()
screen = pygame.display.set_mode((720, 780))
pygame.display.set_caption("Pac-Man")

def main():
    state = "menu"

    menu = Menu(screen, lambda: change_state("game"))
    game = Game(screen, lambda: change_state("menu"))

    def change_state(new_state):
        nonlocal state
        state = new_state

    running = True
    while running:
        if state == "menu":
            menu.run()  # Start menu
        elif state == "game":
            game.run_game()  # Start game

main()
