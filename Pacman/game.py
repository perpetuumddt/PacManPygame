import copy
import pygame
import math
from menu import Menu

class Game:
    def __init__(self, screen, exit_callback, current_level=1):
        self.current_level = current_level
        self.force_win = False
        pygame.init()
        # Screen
        self.height = 780
        self.width = 720
        self.screen = screen
        self.exit_callback = exit_callback
        # Action processing
        self.timer = pygame.time.Clock()
        self.running = False
        self.fps = 60
        # Misc
        self.font = pygame.font.Font('freesansbold.ttf', 20)
        self.color = 'blue'
        self.PI = math.pi

        #loading levels
        from boards import board1, board2, board3
        if current_level == 1:
            self.level = copy.deepcopy(board1)
        elif current_level == 2:
            self.level = copy.deepcopy(board2)
        elif current_level == 3:
            self.level = copy.deepcopy(board3)

        self.score = 0
        self.powerup = False
        self.power_counter = 0
        self.eaten_ghost = [False, False, False, False]
        self.moving = False
        self.startup_counter = 0
        self.lives = 3

        self.game_over = False
        self.game_won = False

        # Objects
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
                key = event.key

                if key == pygame.K_RIGHT:
                    self.pacman.direction_command = 0
                elif key == pygame.K_LEFT:
                    self.pacman.direction_command = 1
                elif key == pygame.K_UP:
                    self.pacman.direction_command = 2
                elif key == pygame.K_DOWN:
                    self.pacman.direction_command = 3

                elif key == pygame.K_SPACE:
                    if self.game_over:
                        self.lives = 3
                        self.reload_level()
                        self.reset_game_state(reset_lives=False)
                        self.game_over = False
                    elif self.game_won:
                        self.running = False
                        self.exit_callback()

                elif key == pygame.K_w:
                    self.force_win = True

            elif event.type == pygame.KEYUP:
                self.moving = False
                direction_map = {
                    pygame.K_RIGHT: 0,
                    pygame.K_LEFT: 1,
                    pygame.K_UP: 2,
                    pygame.K_DOWN: 3
                }
                if event.key in direction_map and self.pacman.direction_command == direction_map[event.key]:
                    self.pacman.direction_command = self.pacman.direction

    def reset_game_state(self, reset_lives=True):
        self.powerup = False
        self.power_counter = 0
        self.startup_counter = 0
        self.pacman.x = 360
        self.pacman.y = 522
        self.pacman.direction = 0
        self.pacman.direction_command = 0

        ghost_reset = [
            (self.blinky, 45, 46, 0),
            (self.inky, 352, 305, 2),
            (self.pinky, 352, 345, 2),
            (self.clyde, 352, 345, 2)
        ]

        for ghost, x, y, direction in ghost_reset:
            ghost.x_pos = x
            ghost.y_pos = y
            ghost.direction = direction
            ghost.dead = False

        self.eaten_ghost = [False] * 4

        if reset_lives:
            self.lives = 3

        self.score = 0
        self.game_won = False
        self.force_win = False
        self.moving = False

    def reload_level(self):
        from boards import board1, board2, board3
        if self.current_level == 1:
            self.level = copy.deepcopy(board1)
        elif self.current_level == 2:
            self.level = copy.deepcopy(board2)
        elif self.current_level == 3:
            self.level = copy.deepcopy(board3)

    def lose_life(self):
        self.lives -= 1
        if self.lives <= 0:
            self.game_over = True
            self.moving = False
        else:
            self.reset_game_state(reset_lives=False)

    def update(self):
        # Delay before game starts
        if self.startup_counter < 180 and not self.game_over and not self.game_won:
            self.moving = False
            self.startup_counter += 1
        else:
            self.moving = True

        # Core movement and game logic
        if self.moving:
            self.pacman.move()

            # Ghost movement logic
            targets = self.get_targets()
            for ghost, target in zip([self.blinky, self.inky, self.pinky, self.clyde], targets):
                ghost.target = target

            self.check_pacman_ghosts_collision()  # Check collisions

            # Revive ghosts after they returned to the box
            for ghost in [self.blinky, self.inky, self.pinky, self.clyde]:
                if ghost.in_box and ghost.dead:
                    ghost.dead = False

            self.update_ghost_speeds()
            self.update_ghost_movement()

        # Update all game objects
        self.pacman.update()
        for ghost in [self.blinky, self.inky, self.pinky, self.clyde]:
            ghost.update()
        self.board.update()
        self.misc.update()

        # Determine if player has won the level
        self.game_won = True
        for row in self.level:
            if 1 in row or 2 in row:
                self.game_won = False
                break
        if self.force_win:
            self.game_won = True

        # Save progress if the level is completed
        if self.game_won and self.current_level < 3:
            from save_data import save_progress
            save_progress(self.current_level + 1)

    def update_ghost_speeds(self):
        base_speed = 0.5 if self.powerup else 1
        ghost_speeds = [base_speed] * 4

        for i, ghost in enumerate([self.blinky, self.inky, self.pinky, self.clyde]):
            if self.eaten_ghost[i] or not self.powerup:
                ghost_speeds[i] = 1
            if ghost.dead:
                ghost_speeds[i] = 4

        self.blinky.speed, self.inky.speed, self.pinky.speed, self.clyde.speed = ghost_speeds

    def update_ghost_movement(self):
        ghosts = [self.blinky, self.inky, self.pinky, self.clyde]
        for ghost in ghosts:
            if not ghost.dead and not ghost.in_box:
                if ghost == self.blinky:
                    ghost.move_blinky()
                elif ghost == self.inky:
                    ghost.move_inky()
                elif ghost == self.pinky:
                    ghost.move_pinky()
                elif ghost == self.clyde:
                    ghost.move_clyde()
            else:
                ghost.move_clyde()

    def draw(self):
        self.screen.fill('black')
        self.board.draw()
        self.pacman.draw()

        self.blinky.draw()
        self.inky.draw()
        self.pinky.draw()
        self.clyde.draw()

        self.misc.draw()

    def get_targets(self):
        def in_box(x, y, w1, w2, h1, h2):
            return w1 < x < w2 and h1 < y < h2

        runaway_x = 0 if self.pacman.x >= 360 else 720
        runaway_y = 0 if self.pacman.y >= 371 else 780
        return_target = (253, 330)

        def decide_target(ghost, eaten, gx, gy, alt_target):
            if self.powerup:
                if not ghost.dead and not eaten:
                    return alt_target
                elif not ghost.dead and eaten:
                    return (320, 82) if in_box(gx, gy, 280, 440, 300, 360) else (self.pacman.x, self.pacman.y)
                else:
                    return return_target
            else:
                if not ghost.dead:
                    return (320, 82) if in_box(gx, gy, 272, 448, 280, 413) else (self.pacman.x, self.pacman.y)
                return return_target

        return [
            decide_target(self.blinky, self.eaten_ghost[0], self.blinky.x_pos, self.blinky.y_pos,
                          (runaway_x, runaway_y)),
            decide_target(self.inky, self.eaten_ghost[1], self.inky.x_pos, self.inky.y_pos, (runaway_x, self.pacman.y)),
            decide_target(self.pinky, self.eaten_ghost[2], self.pinky.x_pos, self.pinky.y_pos,
                          (self.pacman.x, runaway_y)),
            decide_target(self.clyde, self.eaten_ghost[3], self.clyde.x_pos, self.clyde.y_pos, (360, 371))
        ]

    def check_pacman_ghosts_collision(self):
        player_rect = self.pacman.get_player_rect()

        ghosts = [
            (self.blinky, 0),
            (self.inky, 1),
            (self.pinky, 2),
            (self.clyde, 3)
        ]

        for ghost, index in ghosts:
            if not self.powerup and player_rect.colliderect(ghost.rect) and not ghost.dead:
                self.lose_life()
            elif self.powerup and player_rect.colliderect(ghost.rect):
                if self.eaten_ghost[index] and not ghost.dead:
                    self.lose_life()
                elif not self.eaten_ghost[index] and not ghost.dead:
                    ghost.dead = True
                    self.eaten_ghost[index] = True
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
        if self.game.game_over:
            pygame.draw.rect(self.game.screen, 'white', [50, 200, 600, 300], 0, 10)
            pygame.draw.rect(self.game.screen, 'dark gray', [70, 220, 560, 260], 0, 10)
            gameover_text = self.game.font.render('Game over! Space bar to restart!', True, 'red')
            self.game.screen.blit(gameover_text, (120, 300))
        if self.game.game_won:
            pygame.draw.rect(self.game.screen, 'white', [50, 200, 600, 300], 0, 10)
            pygame.draw.rect(self.game.screen, 'dark gray', [70, 220, 560, 260], 0, 10)
            gameover_text = self.game.font.render('Victory! Space bar to main menu!', True, 'green')
            self.game.screen.blit(gameover_text, (120, 300))