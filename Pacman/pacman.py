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

    menu = Menu(screen, lambda: change_state("game"))
    game = Game(screen, lambda: change_state("menu"))

    # Включаем музыку для запуска игры и меню
    play_music("Sounds/persevere.mp3")

    def change_state(new_state):
        nonlocal state
        state = new_state
        if state == "game":
            play_music("Sounds/ni_idea.wav")  # Музыка для самой игры
        elif state == "menu":
            play_music("Sounds/persevere.mp3")  # Музыка при запуске и в меню

    running = True
    while running:
        if state == "menu":
            menu.run()  # Запуск меню
        elif state == "game":
            game.run_game()  # Запуск игры

main()
