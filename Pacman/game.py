import pygame
import math
from board import boards
from menu import Menu

class Game:
    def __init__(self, screen, exit_callback):
        pygame.init()
        self.height = 780
        self.width = 720
        self.screen = screen
        self.exit_callback = exit_callback
        self.clock = pygame.time.Clock()
        self.timer = pygame.time.Clock()
        self.running = False
        self.fps = 60
        self.font = pygame.font.Font('freesansbold.ttf', 20)
        self.level = boards
        self.color = 'blue'
        self.PI = math.pi
        self.score = 0
        self.powerup = False
        self.power_counter = 0
        self.eaten_ghost = [False, False, False, False]
        self.moving = False
        self.startup_counter = 0
        self.lives = 3
        self.pacman = Pacman(self)
        self.board = Board(self)
        self.misc = Misc(self)
        self.ghost = Ghost(self, 0, 0, (0, 0), 0, 0, 0, False, False, 0)


        self.blinky = Ghost(self, self.ghost.blinky_x, self.ghost.blinky_y, self.ghost.targets[0], self.ghost.ghost_speed, self.ghost.blinky_image, self.ghost.blinky_direction, self.ghost.blinky_dead,
                       self.ghost.blinky_box, 0)
        self.inky = Ghost(self, self.ghost.inky_x, self.ghost.inky_y, self.ghost.targets[1], self.ghost.ghost_speed, self.ghost.inky_image, self.ghost.inky_direction, self.ghost.inky_dead,
                     self.ghost.inky_box, 1)
        self.pinky = Ghost(self, self.ghost.pinky_x, self.ghost.pinky_y, self.ghost.targets[2], self.ghost.ghost_speed, self.ghost.pinky_image, self.ghost.pinky_direction, self.ghost.pinky_dead,
                      self.ghost.pinky_box, 2)
        self.clyde = Ghost(self, self.ghost.clyde_x, self.ghost.clyde_y, self.ghost.targets[3], self.ghost.ghost_speed, self.ghost.clyde_image, self.ghost.clyde_direction, self.ghost.clyde_dead,
                      self.ghost.clyde_box, 3)




    def run_game(self):
        self.running = True
        while self.running:
            self.timer.tick(self.fps)
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        self.exit_callback()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
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

            # Отримуємо цілі для привидів
            targets = self.get_targets(self.blinky.x_pos, self.blinky.y_pos,
                                       self.inky.x_pos, self.inky.y_pos,
                                       self.pinky.x_pos, self.pinky.y_pos,
                                       self.clyde.x_pos, self.clyde.y_pos)

            # Оновлюємо цілі для кожного привида
            self.blinky.target = targets[0]
            self.inky.target = targets[1]
            self.pinky.target = targets[2]
            self.clyde.target = targets[3]

            self.check_pacman_ghosts_collision()

            if self.blinky.in_box and self.blinky.dead:
                self.blinky.dead = False
            if self.inky.in_box and self.inky.dead:
                self.inky.dead = False
            if self.pinky.in_box and self.pinky.dead:
                self.pinky.dead = False
            if self.clyde.in_box and self.clyde.dead:
                self.clyde.dead = False

            if not self.blinky.dead and not self.blinky.in_box:
                self.blinky.move_blinky()
            else:
                self.blinky.move_clyde()
            if not self.pinky.dead and not self.pinky.in_box:
                self.pinky.move_pinky()
            else:
                self.pinky.move_clyde()
            if not self.inky.dead and not self.inky.in_box:
                self.inky.move_inky()
            else:
                self.inky.move_clyde()

            self.clyde.move_clyde()

        self.pacman.update()
        self.blinky.update()
        self.inky.update()
        self.pinky.update()
        self.clyde.update()
        self.board.update()
        self.misc.update()

    def draw(self):
        self.screen.fill('black')
        self.board.draw()
        self.pacman.draw()

        self.blinky.draw()
        self.inky.draw()
        self.pinky.draw()
        self.clyde.draw()

        self.misc.draw()

    def get_targets(self, blink_x, blink_y, ink_x, ink_y, pink_x, pink_y, clyd_x, clyd_y):
        if self.pacman.x < 360:
            runaway_x = 720
        else:
            runaway_x = 0
        if self.pacman.y < 371:
            runaway_y = 780
        else:
            runaway_y = 0
        return_target = (253, 330)
        if self.powerup:
            if not self.blinky.dead and not self.eaten_ghost[0]:
                blink_target = (runaway_x, runaway_y)
            elif not self.blinky.dead and self.eaten_ghost[0]:
                if 280 < blink_x < 440 and 300 < blink_y < 360:
                    blink_target = (320, 82)
                else:
                    blink_target = (self.pacman.x, self.pacman.y)
            else:
                blink_target = return_target
            if not self.inky.dead and not self.eaten_ghost[1]:
                ink_target = (runaway_x, self.pacman.y)
            elif not self.inky.dead and self.eaten_ghost[1]:
                if 280 < ink_x < 440 and 300 < ink_y < 360:
                    ink_target = (320, 82)
                else:
                    ink_target = (self.pacman.x, self.pacman.y)
            else:
                ink_target = return_target
            if not self.pinky.dead:
                pink_target = (self.pacman.x, runaway_y)
            elif not self.pinky.dead and self.eaten_ghost[2]:
                if 280 < pink_x < 440 and 300 < pink_y < 360:
                    pink_target = (320, 82)
                else:
                    pink_target = (self.pacman.x, self.pacman.y)
            else:
                pink_target = return_target
            if not self.clyde.dead and not self.eaten_ghost[3]:
                clyd_target = (360, 371)
            elif not self.clyde.dead and self.eaten_ghost[3]:
                if 280 < clyd_x < 440 and 300 < clyd_y < 460:
                    clyd_target = (320, 82)
                else:
                    clyd_target = (self.pacman.x, self.pacman.y)
            else:
                clyd_target = return_target
        else:
            if not self.blinky.dead:
                if 272 < blink_x < 448 and 280 < blink_y < 413:
                    blink_target = (320, 82)
                else:
                    blink_target = (self.pacman.x, self.pacman.y)
            else:
                blink_target = return_target
            if not self.inky.dead:
                if 272 < ink_x < 448 and 280 < ink_y < 413:
                    ink_target = (320, 82)
                else:
                    ink_target = (self.pacman.x, self.pacman.y)
            else:
                ink_target = return_target
            if not self.pinky.dead:
                if 272 < pink_x < 448 and 280 < pink_y < 413:
                    pink_target = (320, 82)
                else:
                    pink_target = (self.pacman.x, self.pacman.y)
            else:
                pink_target = return_target
            if not self.clyde.dead:
                if 272 < clyd_x < 448 and 280 < clyd_y < 413:
                    clyd_target = (320, 82)
                else:
                    clyd_target = (self.pacman.x, self.pacman.y)
            else:
                clyd_target = return_target
        return [blink_target, ink_target, pink_target, clyd_target]

    def check_pacman_ghosts_collision(self):
        player_rect = self.pacman.get_player_rect()
        if not self.powerup:
            if (player_rect.colliderect(self.blinky.rect) and not self.blinky.dead) or \
                    (player_rect.colliderect(self.inky.rect) and not self.inky.dead) or \
                    (player_rect.colliderect(self.pinky.rect) and not self.pinky.dead) or \
                    (player_rect.colliderect(self.clyde.rect) and not self.clyde.dead):
                if self.lives > 0:
                    self.lives -= 1
                    self.startup_counter = 0
                    self.powerup = False
                    self.power_counter = 0
                    self.pacman.x = 360
                    self.pacman.y = 522
                    self.pacman.direction = 0
                    self.pacman.direction_command = 0
                    self.blinky.x_pos = 45
                    self.blinky.y_pos = 46
                    self.blinky.direction = 0
                    self.inky.x_pos = 352
                    self.inky.y_pos = 305
                    self.inky.direction = 2
                    self.pinky.x_pos = 352
                    self.pinky.y_pos = 345
                    self.pinky.direction = 2
                    self.clyde.x_pos = 352
                    self.clyde.y_pos = 345
                    self.clyde.direction = 2
                    self.eaten_ghost = [False, False, False, False]
                    self.blinky.dead = False
                    self.inky.dead = False
                    self.clyde.dead = False
                    self.pinky.dead = False
        if self.powerup and player_rect.colliderect(self.blinky.rect) and self.eaten_ghost[0] and not self.blinky.dead:
            if self.lives > 0:
                self.powerup = False
                self.power_counter = 0
                self.lives -= 1
                self.startup_counter = 0
                self.pacman.x = 360
                self.pacman.y = 522
                self.pacman.direction = 0
                self.pacman.direction_command = 0
                self.blinky.x_pos = 45
                self.blinky.y_pos = 46
                self.blinky.direction = 0
                self.inky.x_pos = 352
                self.inky.y_pos = 305
                self.inky.direction = 2
                self.pinky.x_pos = 352
                self.pinky.y_pos = 345
                self.pinky.direction = 2
                self.clyde.x_pos = 352
                self.clyde.y_pos = 345
                self.clyde.direction = 2
                self.eaten_ghost = [False, False, False, False]
                self.blinky.dead = False
                self.inky.dead = False
                self.clyde.dead = False
                self.pinky.dead = False
        if self.powerup and player_rect.colliderect(self.inky.rect) and self.eaten_ghost[1] and not self.inky.dead:
            if self.lives > 0:
                self.lives -= 1
                self.startup_counter = 0
                self.powerup = False
                self.power_counter = 0
                self.pacman.x = 360
                self.pacman.y = 522
                self.pacman.direction = 0
                self.pacman.direction_command = 0
                self.blinky.x_pos = 45
                self.blinky.y_pos = 46
                self.blinky.direction = 0
                self.inky.x_pos = 352
                self.inky.y_pos = 305
                self.inky.direction = 2
                self.pinky.x_pos = 352
                self.pinky.y_pos = 345
                self.pinky.direction = 2
                self.clyde.x_pos = 352
                self.clyde.y_pos = 345
                self.clyde.direction = 2
                self.eaten_ghost = [False, False, False, False]
                self.blinky.dead = False
                self.inky.dead = False
                self.clyde.dead = False
                self.pinky.dead = False
        if self.powerup and player_rect.colliderect(self.pinky.rect) and self.eaten_ghost[2] and not self.pinky.dead:
            if self.lives > 0:
                self.lives -= 1
                self.startup_counter = 0
                self.powerup = False
                self.power_counter = 0
                self.pacman.x = 360
                self.pacman.y = 522
                self.pacman.direction = 0
                self.pacman.direction_command = 0
                self.blinky.x_pos = 45
                self.blinky.y_pos = 46
                self.blinky.direction = 0
                self.inky.x_pos = 352
                self.inky.y_pos = 305
                self.inky.direction = 2
                self.pinky.x_pos = 352
                self.pinky.y_pos = 345
                self.pinky.direction = 2
                self.clyde.x_pos = 352
                self.clyde.y_pos = 345
                self.clyde.direction = 2
                self.eaten_ghost = [False, False, False, False]
                self.blinky.dead = False
                self.inky.dead = False
                self.clyde.dead = False
                self.pinky.dead = False
        if self.powerup and player_rect.colliderect(self.clyde.rect) and self.eaten_ghost[3] and not self.clyde.dead:
            if self.lives > 0:
                self.lives -= 1
                self.startup_counter = 0
                self.powerup = False
                self.power_counter = 0
                self.pacman.x = 360
                self.pacman.y = 522
                self.pacman.direction = 0
                self.pacman.direction_command = 0
                self.blinky.x_pos = 45
                self.blinky.y_pos = 46
                self.blinky.direction = 0
                self.inky.x_pos = 352
                self.inky.y_pos = 305
                self.inky.direction = 2
                self.pinky.x_pos = 352
                self.pinky.y_pos = 345
                self.pinky.direction = 2
                self.clyde.x_pos = 352
                self.clyde.y_pos = 345
                self.clyde.direction = 2
                self.eaten_ghost = [False, False, False, False]
                self.blinky.dead = False
                self.inky.dead = False
                self.clyde.dead = False
                self.pinky.dead = False
        if self.powerup and player_rect.colliderect(self.blinky.rect) and not self.blinky.dead and not self.eaten_ghost[0]:
            self.blinky.dead = True
            self.eaten_ghost[0] = True
            self.score += (2 ** self.eaten_ghost.count(True)) * 100
        if self.powerup and player_rect.colliderect(self.inky.rect) and not self.inky.dead and not self.eaten_ghost[1]:
            self.inky.dead = True
            self.eaten_ghost[1] = True
            self.score += (2 ** self.eaten_ghost.count(True)) * 100
        if self.powerup and player_rect.colliderect(self.pinky.rect) and not self.pinky.dead and not self.eaten_ghost[2]:
            self.pinky.dead = True
            self.eaten_ghost[2] = True
            self.score += (2 ** self.eaten_ghost.count(True)) * 100
        if self.powerup and player_rect.colliderect(self.clyde.rect) and not self.clyde.dead and not self.eaten_ghost[3]:
            self.clyde.dead = True
            self.eaten_ghost[3] = True
            self.score += (2 ** self.eaten_ghost.count(True)) * 100

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

    def get_player_rect(self):
        center_x = self.x + 16
        center_y = self.y + 17
        return pygame.Rect(center_x - 16, center_y - 16, 32, 32)

    def draw(self):
        if self.direction == 0:
            self.game.screen.blit(self.images[self.counter // 5], (self.x, self.y))
        elif self.direction == 1:
            self.game.screen.blit(pygame.transform.flip(self.images[self.counter // 5], True, False), (self.x, self.y))
        elif self.direction == 2:
            self.game.screen.blit(pygame.transform.rotate(self.images[self.counter // 5], 90), (self.x, self.y))
        elif self.direction == 3:
            self.game.screen.blit(pygame.transform.rotate(self.images[self.counter // 5], 270), (self.x, self.y))

class Ghost:
    def __init__(self, game, x_coord, y_coord, target, speed, img, direct, dead, box, id):
        self.game = game
        self.blinky_image = [pygame.transform.scale(pygame.image.load(f'Sprites/Entities/Enemies/Red/GhostRed{i}.png'), (33, 33))  for i in range(1, 5)]
        self.pinky_image = [pygame.transform.scale(pygame.image.load(f'Sprites/Entities/Enemies/Pink/GhostPink{i}.png'), (33, 33))  for i in range(1, 5)]
        self.inky_image = [pygame.transform.scale(pygame.image.load(f'Sprites/Entities/Enemies/Blue/GhostBlue{i}.png'), (33, 33))  for i in range(1, 5)]
        self.clyde_image = [pygame.transform.scale(pygame.image.load(f'Sprites/Entities/Enemies/Orange/GhostOrange{i}.png'), (33, 33))  for i in range(1, 5)]
        self.spooked_image = [pygame.transform.scale(pygame.image.load(f'Sprites/Entities/Enemies/Scared/GhostScared{i}.png'), (33, 33))  for i in range(1, 5)]
        self.dead_image = [pygame.transform.scale(pygame.image.load(f'Sprites/Entities/Enemies/Dead/GhostDead{i}.png'), (33, 33))  for i in range(1, 5)]
        self.blinky_x = 45
        self.blinky_y = 46
        self.blinky_direction = 0
        self.pinky_x = 352
        self.pinky_y = 345
        self.pinky_direction = 2
        self.inky_x = 352
        self.inky_y = 305
        self.inky_direction = 2
        self.clyde_x = 352
        self.clyde_y = 345
        self.clyde_direction = 2
        self.targets = [(self.game.pacman.x, self.game.pacman.y), (self.game.pacman.x, self.game.pacman.y), (self.game.pacman.x, self.game.pacman.y), (self.game.pacman.x, self.game.pacman.y)]
        self.blinky_dead = False
        self.pinky_dead = False
        self.inky_dead = False
        self.clyde_dead = False
        self.blinky_box = False
        self.pinky_box = False
        self.inky_box = False
        self.clyde_box = False
        self.ghost_speed = 2
        self.counter = 0
        self.x_pos = x_coord
        self.y_pos = y_coord
        self.center_x = self.x_pos + 16
        self.center_y = self.y_pos + 17
        self.target = target
        self.speed = speed
        self.img = img
        self.direction = direct
        self.dead = dead
        self.in_box = box
        self.id = id
        self.turns, self.in_box = self.check_collisions()
        self.rect = pygame.Rect((self.center_x - 13, self.center_y - 13), (26, 26))


    def update(self):
        if self.counter < 19:
            self.counter += 1
        else:
            self.counter = 0

        self.center_x = int(self.x_pos) + 16
        self.center_y = int(self.y_pos) + 17
        self.rect.topleft = (self.center_x - 13, self.center_y - 13)

    def draw(self):
        # Перевірка на наявність атрибутів
        if not hasattr(self.game, 'powerup'):
            self.game.powerup = False
        if not hasattr(self.game, 'eaten_ghost'):
            self.game.eaten_ghost = [False, False, False, False]

        if (not self.game.powerup and not self.dead) or (self.game.eaten_ghost[self.id] and self.game.powerup and not self.dead):
            if self.img:  # Перевірка на наявність зображення
                if self.id == 0:
                    self.game.screen.blit(self.blinky_image[self.counter // 5], (self.x_pos, self.y_pos))
                elif self.id == 1:
                    self.game.screen.blit(self.inky_image[self.counter // 5], (self.x_pos, self.y_pos))
                elif self.id == 2:
                    self.game.screen.blit(self.pinky_image[self.counter // 5], (self.x_pos, self.y_pos))
                elif self.id == 3:
                    self.game.screen.blit(self.clyde_image[self.counter // 5], (self.x_pos, self.y_pos))
        elif self.game.powerup and not self.dead and not self.game.eaten_ghost[self.id]:
            if hasattr(self, 'spooked_image') and self.spooked_image:
                self.game.screen.blit(self.spooked_image[self.counter // 5], (self.x_pos, self.y_pos))
        else:
            if hasattr(self, 'dead_image') and self.dead_image:
                self.game.screen.blit(self.dead_image[self.counter // 5], (self.x_pos, self.y_pos))


    def check_collisions(self):
        num1 = ((self.game.height - 50) // 32)
        num2 = (self.game.width // 30)
        num3 = 12
        self.turns = [False, False, False, False]
        if 0 < self.center_x // 30 < 29:
            if self.game.level[(self.center_y - num3) // num1][self.center_x // num2] == 9:
                self.turns[2] = True
            if self.game.level[self.center_y // num1][(self.center_x - num3) // num2] < 3 \
                    or (self.game.level[self.center_y // num1][(self.center_x - num3) // num2] == 9 and (
                    self.in_box or self.dead)):
                self.turns[1] = True
            if self.game.level[self.center_y // num1][(self.center_x + num3) // num2] < 3 \
                    or (self.game.level[self.center_y // num1][(self.center_x + num3) // num2] == 9 and (
                    self.in_box or self.dead)):
                self.turns[0] = True
            if self.game.level[(self.center_y + num3) // num1][self.center_x // num2] < 3 \
                    or (self.game.level[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (
                    self.in_box or self.dead)):
                self.turns[3] = True
            if self.game.level[(self.center_y - num3) // num1][self.center_x // num2] < 3 \
                    or (self.game.level[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (
                    self.in_box or self.dead)):
                self.turns[2] = True

            if self.direction == 2 or self.direction == 3:
                if 9 <= self.center_x % num2 <= 15:
                    if self.game.level[(self.center_y + num3) // num1][self.center_x // num2] < 3 \
                            or (self.game.level[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[3] = True
                    if self.game.level[(self.center_y - num3) // num1][self.center_x // num2] < 3 \
                            or (self.game.level[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[2] = True
                if 9 <= self.center_y % num1 <= 15:
                    if self.game.level[self.center_y // num1][(self.center_x - num2) // num2] < 3 \
                            or (self.game.level[self.center_y // num1][(self.center_x - num2) // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[1] = True
                    if self.game.level[self.center_y // num1][(self.center_x + num2) // num2] < 3 \
                            or (self.game.level[self.center_y // num1][(self.center_x + num2) // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[0] = True

            if self.direction == 0 or self.direction == 1:
                if 9 <= self.center_x % num2 <= 15:
                    if self.game.level[(self.center_y + num3) // num1][self.center_x // num2] < 3 \
                            or (self.game.level[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[3] = True
                    if self.game.level[(self.center_y - num3) // num1][self.center_x // num2] < 3 \
                            or (self.game.level[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[2] = True
                if 9 <= self.center_y % num1 <= 15:
                    if self.game.level[self.center_y // num1][(self.center_x - num3) // num2] < 3 \
                            or (self.game.level[self.center_y // num1][(self.center_x - num3) // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[1] = True
                    if self.game.level[self.center_y // num1][(self.center_x + num3) // num2] < 3 \
                            or (self.game.level[self.center_y // num1][(self.center_x + num3) // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[0] = True
        else:
            self.turns[0] = True
            self.turns[1] = True
        if 280 < self.x_pos < 440 and 300 < self.y_pos < 360:
            self.in_box = True
        else:
            self.in_box = False
        return self.turns, self.in_box


    def move_clyde(self):
        # r, l, u, d
        # clyde is going to turn whenever advantageous for pursuit
        self.turns, self.in_box = self.check_collisions()
        if self.direction == 0:
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:
                    self.x_pos += self.speed
        elif self.direction == 1:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.direction = 3
            elif self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:
                    self.x_pos -= self.speed
        elif self.direction == 2:
            if self.target[0] < self.x_pos and self.turns[1]:
                self.direction = 1
                self.x_pos -= self.speed
            elif self.target[1] < self.y_pos and self.turns[2]:
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos -= self.speed
        elif self.direction == 3:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos += self.speed
        if self.x_pos > 691:
            self.x_pos = -35
        elif self.x_pos < -38:
            self.x_pos = 691
        return self.x_pos, self.y_pos, self.direction

    def move_blinky(self):
        # r, l, u, d
        # blinky is going to turn whenever colliding with walls, otherwise continue straight
        self.turns, self.in_box = self.check_collisions()
        if self.direction == 0:
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:
                self.x_pos += self.speed
        elif self.direction == 1:
            if self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]:
                self.x_pos -= self.speed
        elif self.direction == 2:
            if self.target[1] < self.y_pos and self.turns[2]:
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[2]:
                self.y_pos -= self.speed
        elif self.direction == 3:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[3]:
                self.y_pos += self.speed
        if self.x_pos > 691:
            self.x_pos = -35
        elif self.x_pos < -38:
            self.x_pos = 691
        return self.x_pos, self.y_pos, self.direction

    def move_inky(self):
        # r, l, u, d
        # inky turns up or down at any point to pursue, but left and right only on collision
        self.turns, self.in_box = self.check_collisions()
        if self.direction == 0:
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:
                    self.x_pos += self.speed
        elif self.direction == 1:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.direction = 3
            elif self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:
                    self.x_pos -= self.speed
        elif self.direction == 2:
            if self.target[1] < self.y_pos and self.turns[2]:
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[2]:
                self.y_pos -= self.speed
        elif self.direction == 3:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[3]:
                self.y_pos += self.speed
        if self.x_pos > 691:
            self.x_pos = -35
        elif self.x_pos < -38:
            self.x_pos = 691
        return self.x_pos, self.y_pos, self.direction

    def move_pinky(self):
        # r, l, u, d
        # pinky is going to turn left or right whenever advantageous, but only up or down on collision
        self.turns, self.in_box = self.check_collisions()
        if self.direction == 0:
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:
                self.x_pos += self.speed
        elif self.direction == 1:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.direction = 3
            elif self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]:
                self.x_pos -= self.speed
        elif self.direction == 2:
            if self.target[0] < self.x_pos and self.turns[1]:
                self.direction = 1
                self.x_pos -= self.speed
            elif self.target[1] < self.y_pos and self.turns[2]:
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos -= self.speed
        elif self.direction == 3:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos += self.speed
        if self.x_pos > 691:
            self.x_pos = -35
        elif self.x_pos < -38:
            self.x_pos = 691
        return self.x_pos, self.y_pos, self.direction

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