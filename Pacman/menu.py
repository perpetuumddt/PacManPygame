import pygame
import sys

def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(x, y))
    surface.blit(text_obj, text_rect)


def main_menu():
    pygame.init()
    screen = pygame.display.set_mode((720, 780))
    pygame.display.set_caption("Pac-Man Menu")
    font = pygame.font.Font(None, 50)

    clock = pygame.time.Clock()

    while True:
        screen.fill("black")
        draw_text("PAC-MAN", font, "yellow", screen, 360, 100)
        draw_text("Start Game", font, "white", screen, 360, 300)
        pygame.display.flip()
        clock.tick(30)


if __name__ == "__main__":
    main_menu()
