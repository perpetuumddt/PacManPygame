import pygame
import pygame.mixer
from menu import Menu
from game import Game

pygame.init()
pygame.mixer.init()  # Инициализация аудиосистемы

# Создание экрана
screen = pygame.display.set_mode((720, 780))
pygame.display.set_caption("Pac-Man")

# Функция для смены музыки
def play_music(track):
    pygame.mixer.music.load(track)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)  # Бесконечное воспроизведение

def main():
    state = "menu"
    current_level = 1
    game = None

    def start_game(level):
        print(f"Starting game with level: {level}")
        nonlocal state, current_level, game
        current_level = level
        game = Game(screen, lambda: change_state("menu"), current_level=current_level)
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
