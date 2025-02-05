from board import boards
import pygame
import math

pygame.init()

height = 780
width = 720
screen = pygame.display.set_mode([width, height])

timer = pygame.time.Clock()
fps = 60

#States
MENU = "menu"
GAME = "game"
state = MENU

font = pygame.font.Font('freesansbold.ttf', 20)
level = boards
color = 'blue'
PI = math.pi

def draw_menu():
    screen.fill(color="black")
    text = font.render("Press ENTER to Start", True, "white")
    screen.blit(text, (width // 2 - text.get_width() // 2, height // 2))
    pygame.display.flip()

def draw_board():
    num1 = ((height - 50) // 32)
    num2 = (width // 30)
    for i in range(len(level)):
        for j in range(len(level[i])):
            if level[i][j] == 1:
                pygame.draw.circle(screen, 'white', (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 4)
            if level[i][j] == 2:
                pygame.draw.circle(screen, (255,255,155), (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 10)
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


running = True
while running:
    timer.tick(fps)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if state == MENU and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            state = GAME

    if state == MENU:
        draw_menu()
    elif state == GAME:
        screen.fill('black')
        draw_board()

pygame.quit()