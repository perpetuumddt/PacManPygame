import pygame
import pygame.mixer
from menu import Menu
from game import Game

pygame.init()
pygame.mixer.init()

# Creating screen
screen = pygame.display.set_mode((720, 780))
pygame.display.set_caption("Pac-Man")

# Play music track
def play_music(track):
    pygame.mixer.music.load(track)
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)  # Infinite play

def main():
    state = "menu"
    game = None

    def start_game(level):
        nonlocal state, game
        game = Game(screen, lambda: change_state("menu"), current_level=level)
        state = "game"
        play_music("Sounds/ni_idea.wav")

    menu = Menu(screen, start_game)

    play_music("Sounds/persevere.mp3")

    def change_state(new_state):
        nonlocal state
        state = new_state
        if state == "menu":
            play_music("Sounds/persevere.mp3")

    running = True
    while running:
        if state == "menu":
            menu.run()
        elif state == "game" and game is not None:
            game.run_game()

main()
