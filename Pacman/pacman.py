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