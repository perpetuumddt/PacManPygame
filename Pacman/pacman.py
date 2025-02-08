from json.encoder import encode_basestring

from board import boards
import pygame
import math

pygame.init()

height = 780
width = 720
screen = pygame.display.set_mode([width, height])
timer = pygame.time.Clock()
fps = 60
font = pygame.font.Font('freesansbold.ttf', 20)
level = boards
color = 'blue'
PI = math.pi
pacman_images = []
for i in range(1, 5):
    pacman_images.append(pygame.transform.scale(pygame.image.load(f'Sprites/Entities/Character/Pacman{i}.png'), (33, 33)))

pacman_x = 360
pacman_y = 522
direction = 0
counter = 0
flicker = False
turns_allowed = [False, False, False, False]
direction_command = 0
pacman_speed = 2
score = 0
powerup = False
power_counter = 0
eaten_ghost = [False, False, False, False]
moving = False
startup_counter = 0
lives = 3


def draw_misc():
    score_text = font.render(f'Score: {score}', True, 'white')
    screen.blit(score_text, (10, 740))
    if powerup:
        pygame.draw.circle(screen, 'blue', (140, 750), 12)
    for i in range(lives):
        screen.blit(pygame.transform.scale(pacman_images[1], (30, 30)), (500 + i * 40, 735))


def check_collisions(scor, power, power_count, eaten_ghosts):
    num1 = (height - 50) // 32
    num2 = width // 30
    if 0 < pacman_x < 691:
        if level[center_y // num1][center_x // num2] == 1:
            level[center_y // num1][center_x // num2] = 0
            scor += 10
        if level[center_y // num1][center_x // num2] == 2:
            level[center_y // num1][center_x // num2] = 0
            scor += 50
            power = True
            power_count = 0
            eaten_ghosts = [False, False, False, False]

    return scor, power, power_count, eaten_ghosts

def draw_board():
    num1 = ((height - 50) // 32)
    num2 = (width // 30)
    for i in range(len(level)):
        for j in range(len(level[i])):
            if level[i][j] == 1:
                pygame.draw.circle(screen, 'white', (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 3)
            if level[i][j] == 2 and not flicker:
                pygame.draw.circle(screen, (255,255,155), (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 6)
            if level[i][j] == 3:
                pygame.draw.line(screen, color, (j * num2 + (0.5 * num2), i * num1),
                                 (j * num2 + (0.5 * num2), i * num1 + num1), 3)
            if level[i][j] == 4:
                pygame.draw.line(screen, color, (j * num2, i * num1 + (0.5 * num1)),
                                 (j * num2 + num2, i * num1 + (0.5 * num1)), 3)
            if level[i][j] == 5:
                pygame.draw.arc(screen, color, [(j * num2 - (num2 * 0.4)) - 2, (i * num1 + (0.5 * num1)), num2, num1],
                                0, PI / 2, 2)
            if level[i][j] == 6:
                pygame.draw.arc(screen, color,[(j * num2 + (num2 * 0.5)), (i * num1 + (0.5 * num1)), num2, num1],
                                 PI / 2, PI, 2)
            if level[i][j] == 7:
                pygame.draw.arc(screen, color, [(j * num2 + (num2 * 0.5)), (i * num1 - (0.4 * num1)), num2, num1],
                                PI, 3 * PI / 2, 2)
            if level[i][j] == 8:
                pygame.draw.arc(screen, color,[(j * num2 - (num2 * 0.35)) - 2, (i * num1 - (0.4 * num1)), num2, num1],
                                 3 * PI / 2, 2 * PI, 2)
            if level[i][j] == 9:
                pygame.draw.line(screen, 'white', (j * num2, i * num1 + (0.5 * num1)),
                                 (j * num2 + num2, i * num1 + (0.5 * num1)), 3)

def draw_pacman():
    # 0-right, 1-left, 2-up, 3-down,
    if direction == 0:
        screen.blit(pacman_images[counter // 5], (pacman_x, pacman_y))
    elif direction == 1:
        screen.blit(pygame.transform.flip(pacman_images[counter // 5], True, False), (pacman_x, pacman_y))
    elif direction == 2:
        screen.blit(pygame.transform.rotate(pacman_images[counter // 5], 90), (pacman_x, pacman_y))
    elif direction == 3:
        screen.blit(pygame.transform.rotate(pacman_images[counter // 5], 270), (pacman_x, pacman_y))

def check_position(centerx, centery):
    turns = [False, False, False, False]
    num1 = ((height - 50) // 32)
    num2 = (width // 30)
    num3 = 12

    if centerx // 30 < 29:
        if direction == 0:
            if level[centery // num1][(centerx - num3) // num2] < 3:
                turns[1] = True
        if direction == 1:
            if level[centery // num1][(centerx - num3) // num2] < 3:
                turns[0] = True
        if direction == 2:
            if level[(centery + num3) // num1][centerx // num2] < 3:
                turns[3] = True
        if direction == 3:
            if level[(centery - num3) // num1][centerx // num2] < 3:
                turns[2] = True

        if direction == 2 or direction == 3:
            if 9 <= centerx % num2 <= 15:
                if level[(centery + num3) // num1][centerx // num2] < 3:
                    turns[3] = True
                if level[(centery - num3) // num1][centerx // num2] < 3:
                    turns[2] = True
            if 9 <= centery % num1 <= 15:
                if level[centery // num1][(centerx - num2) // num2] < 3:
                    turns[1] = True
                if level[centery // num1][(centerx + num2) // num2] < 3:
                    turns[0] = True

        if direction == 0 or direction == 1:
            if 9 <= centerx % num2 <= 15:
                if level[(centery + num1) // num1][centerx // num2] < 3:
                    turns[3] = True
                if level[(centery - num1) // num1][centerx // num2] < 3:
                    turns[2] = True
            if 9 <= centery % num1 <= 15:
                if level[centery // num1][(centerx - num3) // num2] < 3:
                    turns[1] = True
                if level[centery // num1][(centerx + num3) // num2] < 3:
                    turns[0] = True


    else:
        turns[0] = True
        turns[1] = True
    return turns

def move_pacman(pac_x, pac_y):
    # 0-r, 1-l, 2-u, 3-down
    if direction == 0 and turns_allowed[0]:
        pac_x += pacman_speed
    elif direction == 1 and turns_allowed[1]:
        pac_x -= pacman_speed
    elif direction == 2 and turns_allowed[2]:
        pac_y -= pacman_speed
    elif direction == 3 and turns_allowed[3]:
        pac_y += pacman_speed
    return pac_x, pac_y



run = True
while run:
    timer.tick(fps)
    if counter < 19:
        counter += 1
        if counter > 9:
            flicker = False
    else:
        counter = 0
        flicker = True

    if powerup and power_counter < 600:
        power_counter += 1
    elif powerup and power_counter >= 600:
        power_counter = 0
        powerup = False
        eaten_ghost = [False, False, False, False]

    if startup_counter < 180:
        moving = False
        startup_counter += 1
    else:
        moving = True

    screen.fill('black')
    draw_board()
    draw_pacman()
    draw_misc()
    center_x = pacman_x + 16
    center_y = pacman_y + 17
    turns_allowed = check_position(center_x, center_y)
    if moving:
        pacman_x, pacman_y = move_pacman(pacman_x, pacman_y)
    score, powerup, power_counter, eaten_ghost = check_collisions(score, powerup, power_counter, eaten_ghost)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                direction_command = 0
            if event.key == pygame.K_LEFT:
                direction_command = 1
            if event.key == pygame.K_UP:
                direction_command = 2
            if event.key == pygame.K_DOWN:
                direction_command = 3

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT and direction_command == 0:
                direction_command = direction
            if event.key == pygame.K_LEFT and direction_command == 1:
                direction_command = direction
            if event.key == pygame.K_UP and direction_command == 2:
                direction_command = direction
            if event.key == pygame.K_DOWN and direction_command == 3:
                direction_command = direction

    for i in range(4):
        if direction_command == i and turns_allowed[i]:
            direction = i

    if pacman_x > 720:
        pacman_x = -35
    elif pacman_x < -38:
        pacman_x = 717


    pygame.display.flip()

pygame.quit()