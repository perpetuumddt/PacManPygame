import pygame
import math
from board import boards

class Game:
    def __init__(self):
        pygame.init()
        self.height = 780
        self.width = 720
        self.screen = pygame.display.set_mode([self.width, self.height])
        self.timer = pygame.time.Clock()
        self.fps = 60
        self.font = pygame.font.Font('freesansbold.ttf', 20)
        self.level = boards
        self.color = 'blue'
        self.PI = math.pi
        self.pacman = Pacman(self)
        self.board = Board(self)
        self.misc = Misc(self)
        self.score = 0
        self.powerup = False
        self.power_counter = 0
        self.eaten_ghost = [False, False, False, False]
        self.moving = False
        self.startup_counter = 0
        self.lives = 3
        self.run = True

    def run_game(self):
        while self.run:
            self.timer.tick(self.fps)
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False
            if event.type == pygame.KEYDOWN:
                self.moving = True
                if event.key == pygame.K_RIGHT:
                    self.pacman.direction_command = 0
                if event.key == pygame.K_LEFT:
                    self.pacman.direction_command = 1
                if event.key == pygame.K_UP:
                    self.pacman.direction_command = 2
                if event.key == pygame.K_DOWN:
                    self.pacman.direction_command = 3

            if event.type == pygame.KEYUP:
                self.moving = False
                if event.key == pygame.K_RIGHT and self.pacman.direction_command == 0:
                    self.pacman.direction_command = self.pacman.direction
                if event.key == pygame.K_LEFT and self.pacman.direction_command == 1:
                    self.pacman.direction_command = self.pacman.direction
                if event.key == pygame.K_UP and self.pacman.direction_command == 2:
                    self.pacman.direction_command = self.pacman.direction
                if event.key == pygame.K_DOWN and self.pacman.direction_command == 3:
                    self.pacman.direction_command = self.pacman.direction

    def update(self):
        if self.startup_counter < 180:
            self.moving = False
            self.startup_counter += 1
        else:
            self.moving = True

        if self.moving:
            self.pacman.move()

        self.pacman.update()
        self.board.update()
        self.misc.update()

    def draw(self):
        self.screen.fill('black')
        self.board.draw()
        self.pacman.draw()
        self.misc.draw()

class Pacman:
    def __init__(self, game):
        self.game = game
        self.images = [pygame.transform.scale(pygame.image.load(f'Sprites/Entities/Character/Pacman{i}.png'), (33, 33)) for i in range(1, 5)]
        self.x = 360
        self.y = 522
        self.direction = 0
        self.direction_command = 0
        self.counter = 0
        self.speed = 2
        self.turns_allowed = [False, False, False, False]
        self.flicker = False  # Add the flicker attribute

    def update(self):
        if self.counter < 19:
            self.counter += 1
        else:
            self.counter = 0

        center_x = self.x + 16
        center_y = self.y + 17
        self.turns_allowed = self.game.board.check_position(center_x, center_y)

        # Update direction based on direction_command
        if self.turns_allowed[self.direction_command]:
            self.direction = self.direction_command

    def move(self):
        if self.direction == 0 and self.turns_allowed[0]:
            self.x += self.speed
        elif self.direction == 1 and self.turns_allowed[1]:
            self.x -= self.speed
        elif self.direction == 2 and self.turns_allowed[2]:
            self.y -= self.speed
        elif self.direction == 3 and self.turns_allowed[3]:
            self.y += self.speed

        if self.x > 691:
            self.x = -35
        elif self.x < -38:
            self.x = 691

    def draw(self):
        if self.direction == 0:
            self.game.screen.blit(self.images[self.counter // 5], (self.x, self.y))
        elif self.direction == 1:
            self.game.screen.blit(pygame.transform.flip(self.images[self.counter // 5], True, False), (self.x, self.y))
        elif self.direction == 2:
            self.game.screen.blit(pygame.transform.rotate(self.images[self.counter // 5], 90), (self.x, self.y))
        elif self.direction == 3:
            self.game.screen.blit(pygame.transform.rotate(self.images[self.counter // 5], 270), (self.x, self.y))

class Board:
    def __init__(self, game):
        self.game = game

    def update(self):
        self.game.score, self.game.powerup, self.game.power_counter, self.game.eaten_ghost = self.check_collisions()

    def draw(self):
        num1 = (self.game.height - 50) // 32
        num2 = self.game.width // 30
        for i in range(len(self.game.level)):
            for j in range(len(self.game.level[i])):
                if self.game.level[i][j] == 1:
                    pygame.draw.circle(self.game.screen, 'white', (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 3)
                if self.game.level[i][j] == 2 and not self.game.pacman.flicker:
                    pygame.draw.circle(self.game.screen, (255, 255, 155), (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 6)
                if self.game.level[i][j] == 3:
                    pygame.draw.line(self.game.screen, self.game.color, (j * num2 + (0.5 * num2), i * num1),
                                     (j * num2 + (0.5 * num2), i * num1 + num1), 3)
                if self.game.level[i][j] == 4:
                    pygame.draw.line(self.game.screen, self.game.color, (j * num2, i * num1 + (0.5 * num1)),
                                     (j * num2 + num2, i * num1 + (0.5 * num1)), 3)
                if self.game.level[i][j] == 5:
                    pygame.draw.arc(self.game.screen, self.game.color, [(j * num2 - (num2 * 0.4)) - 2, (i * num1 + (0.5 * num1)), num2, num1],
                                    0, self.game.PI / 2, 2)
                if self.game.level[i][j] == 6:
                    pygame.draw.arc(self.game.screen, self.game.color, [(j * num2 + (num2 * 0.5)), (i * num1 + (0.5 * num1)), num2, num1],
                                     self.game.PI / 2, self.game.PI, 2)
                if self.game.level[i][j] == 7:
                    pygame.draw.arc(self.game.screen, self.game.color, [(j * num2 + (num2 * 0.5)), (i * num1 - (0.4 * num1)), num2, num1],
                                    self.game.PI, 3 * self.game.PI / 2, 2)
                if self.game.level[i][j] == 8:
                    pygame.draw.arc(self.game.screen, self.game.color, [(j * num2 - (num2 * 0.35)) - 2, (i * num1 - (0.4 * num1)), num2, num1],
                                     3 * self.game.PI / 2, 2 * self.game.PI, 2)
                if self.game.level[i][j] == 9:
                    pygame.draw.line(self.game.screen, 'white', (j * num2, i * num1 + (0.5 * num1)),
                                     (j * num2 + num2, i * num1 + (0.5 * num1)), 3)

    def check_collisions(self):
        num1 = (self.game.height - 50) // 32
        num2 = self.game.width // 30
        center_x = self.game.pacman.x + 16
        center_y = self.game.pacman.y + 17
        if 0 < self.game.pacman.x < 691:
            if self.game.level[center_y // num1][center_x // num2] == 1:
                self.game.level[center_y // num1][center_x // num2] = 0
                self.game.score += 10
            if self.game.level[center_y // num1][center_x // num2] == 2:
                self.game.level[center_y // num1][center_x // num2] = 0
                self.game.score += 50
                self.game.powerup = True
                self.game.power_counter = 0
                self.game.eaten_ghost = [False, False, False, False]

        return self.game.score, self.game.powerup, self.game.power_counter, self.game.eaten_ghost

    def check_position(self, centerx, centery):
        turns = [False, False, False, False]
        num1 = (self.game.height - 50) // 32
        num2 = self.game.width // 30
        num3 = 12

        if centerx // 30 < 29:
            if self.game.pacman.direction == 0:
                if self.game.level[centery // num1][(centerx - num3) // num2] < 3:
                    turns[1] = True
            if self.game.pacman.direction == 1:
                if self.game.level[centery // num1][(centerx - num3) // num2] < 3:
                    turns[0] = True
            if self.game.pacman.direction == 2:
                if self.game.level[(centery + num3) // num1][centerx // num2] < 3:
                    turns[3] = True
            if self.game.pacman.direction == 3:
                if self.game.level[(centery - num3) // num1][centerx // num2] < 3:
                    turns[2] = True

            if self.game.pacman.direction == 2 or self.game.pacman.direction == 3:
                if 9 <= centerx % num2 <= 15:
                    if self.game.level[(centery + num3) // num1][centerx // num2] < 3:
                        turns[3] = True
                    if self.game.level[(centery - num3) // num1][centerx // num2] < 3:
                        turns[2] = True
                if 9 <= centery % num1 <= 15:
                    if self.game.level[centery // num1][(centerx - num2) // num2] < 3:
                        turns[1] = True
                    if self.game.level[centery // num1][(centerx + num2) // num2] < 3:
                        turns[0] = True

            if self.game.pacman.direction == 0 or self.game.pacman.direction == 1:
                if 9 <= centerx % num2 <= 15:
                    if self.game.level[(centery + num1) // num1][centerx // num2] < 3:
                        turns[3] = True
                    if self.game.level[(centery - num1) // num1][centerx // num2] < 3:
                        turns[2] = True
                if 9 <= centery % num1 <= 15:
                    if self.game.level[centery // num1][(centerx - num3) // num2] < 3:
                        turns[1] = True
                    if self.game.level[centery // num1][(centerx + num3) // num2] < 3:
                        turns[0] = True
        else:
            turns[0] = True
            turns[1] = True
        return turns

class Misc:
    def __init__(self, game):
        self.game = game

    def update(self):
        if self.game.powerup and self.game.power_counter < 600:
            self.game.power_counter += 1
        elif self.game.powerup and self.game.power_counter >= 600:
            self.game.power_counter = 0
            self.game.powerup = False
            self.game.eaten_ghost = [False, False, False, False]

    def draw(self):
        score_text = self.game.font.render(f'Score: {self.game.score}', True, 'white')
        self.game.screen.blit(score_text, (10, 740))
        if self.game.powerup:
            pygame.draw.circle(self.game.screen, 'blue', (140, 750), 12)
        for i in range(self.game.lives):
            self.game.screen.blit(pygame.transform.scale(self.game.pacman.images[1], (30, 30)), (500 + i * 40, 735))

if __name__ == "__main__":
    game = Game()
    game.run_game()