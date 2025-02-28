import pygame
import sys

class Menu:
    def __init__(self, screen, start_game_callback):
        self.screen = screen
        self.start_game_callback = start_game_callback
        self.font = pygame.font.SysFont('Arial', 50)
        self.clock = pygame.time.Clock()

        #Loading images
        title_img = pygame.image.load("Sprites/UI/Title_1.png")
        start_button_img = pygame.image.load("Sprites/UI/Button_Start.png")
        info_button_img = pygame.image.load("Sprites/UI/Button_Info.png")

        #Menu objects coordinates
        self.start_button_rect = start_button_img.get_rect(center=(360, 360))

        def draw_text(self, text, x, y, color="white"):
            text_obj = self.font.render(text, True, color)
            text_rect = text_obj.get_rect(center=(x, y))
            self.screen.blit(text_obj, text_rect)


        def run(self):
            running = True
            while running:
                self.screen.fill("black")
                self.screen.blit(self.title_img, (160, 50))
                self.screen.blit(self.start_button_img, self.start_button_rect.topleft)  # Start button
                self.draw_text("PAC-MAN", 360, 100, "yellow")

                pygame.display.flip()
                self.clock.tick(30)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.start_button_rect.collidepoint(event.pos):
                            running = False  # Exit menu
                            self.start_game_callback()  # Start game