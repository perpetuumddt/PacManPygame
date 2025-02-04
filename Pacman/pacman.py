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

def draw_board():
    num1 = ((height - 50) // 32)
    num2 = (width // 30)
    for i in range(len(level)):
        for j in range(len(level[i])):
            if level[i][j] == 1:
                pygame.draw.circle(screen, 'white', (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 3)
            if level[i][j] == 2 and not flicker:
                pygame.draw.circle(screen, (255,255,155), (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 7)
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
            if level[centery // num1][(centerx - num3) // num2] < 1:
                turns[1] = True
        if direction == 1:
            if level[centery // num1][(centerx - num3) // num2] < 1:
                turns[0] = True
        if direction == 2:
            if level[(centery + num3) // num1][centerx // num2] < 1:
                turns[3] = True
        if direction == 3:
            if level[(centery - num3) // num1][centerx // num2] < 1:
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
            if 12 <= centerx % num2 <= 18:
                if level[(centery + num1) // num1][centerx // num2] < 3:
                    turns[3] = True
                if level[(centery - num1) // num1][centerx // num2] < 3:
                    turns[2] = True
            if 12 <= centery % num1 <= 18:
                if level[centery // num1][(centerx - num3) // num2] < 3:
                    turns[1] = True
                if level[centery // num1][(centerx + num3) // num2] < 3:
                    turns[0] = True


    else:
        turns[0] = True
        turns[1] = True
    return turns


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

    screen.fill('black')
    draw_board()
    draw_pacman()
    center_x = pacman_x + 16
    center_y = pacman_y + 17
    turns_allowed = check_position(center_x, center_y)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                direction = 0
            if event.key == pygame.K_LEFT:
                direction = 1
            if event.key == pygame.K_UP:
                direction = 2
            if event.key == pygame.K_DOWN:
                direction = 3

    pygame.display.flip()

pygame.quit()