import pygame

class Menu:
    def __init__(self, screen, start_game_callback):
        self.screen = screen
        self.start_game_callback = start_game_callback
        self.font = pygame.font.SysFont('Arial', 50)
        self.clock = pygame.time.Clock()

        # Loading images
        self.title_img = pygame.image.load("Sprites/UI/Title_1.png")
        self.start_button_img = pygame.image.load("Sprites/UI/Button_Start.png")
        self.info_button_img = pygame.image.load("Sprites/UI/Button_Info.png")
        self.level_select_1_img = pygame.image.load("Sprites/UI/Lvl_1.png")
        self.level_select_2_img = pygame.image.load("Sprites/UI/Lvl_2.png")
        self.level_select_3_img = pygame.image.load("Sprites/UI/Lvl_3.png")

        #transforming images scale
        #multiplying img scale by 3
        self.title_img = pygame.transform.scale(self.title_img, (570, 150))
        self.start_button_img = pygame.transform.scale(self.start_button_img, (228, 87))
        self.level_select_1_img = pygame.transform.scale(self.level_select_1_img, (228, 87))
        self.level_select_2_img = pygame.transform.scale(self.level_select_2_img, (228, 87))
        self.level_select_3_img = pygame.transform.scale(self.level_select_3_img, (228, 87))
        # adjusting image coordinates
        self.title_rect = self.title_img.get_rect(center=(self.screen.get_width() // 2, 100))
        # Button coordinates
        self.start_button_rect = self.start_button_img.get_rect(center=(360, 360))
        self.level_select_1_rect = self.level_select_1_img.get_rect(center=(120, 500))
        self.level_select_2_rect = self.level_select_2_img.get_rect(center=(360, 500))
        self.level_select_3_rect = self.level_select_3_img.get_rect(center=(600, 500))

    def draw_text(self, text, x, y, color="white"):
        text_obj = self.font.render(text, True, color)
        text_rect = text_obj.get_rect(center=(x, y))
        self.screen.blit(text_obj, text_rect)

    def run(self):
        running = True
        while running:
            self.screen.fill("black")
            self.screen.blit(self.title_img, self.title_rect.topleft)
            self.screen.blit(self.start_button_img, self.start_button_rect.topleft)  # Start button
            self.screen.blit(self.level_select_1_img, self.level_select_1_rect.topleft)
            self.screen.blit(self.level_select_2_img, self.level_select_2_rect.topleft)
            self.screen.blit(self.level_select_3_img, self.level_select_3_rect.topleft)

            pygame.display.flip()
            self.clock.tick(30)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.start_button_rect.collidepoint(event.pos):
                        self.start_game_callback()  # Start game
                        running = False