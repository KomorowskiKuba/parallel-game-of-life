import pygame
import sys

from map import Map
from settings import AMOUNT_OF_ROWS, AMOUNT_OF_COLUMNS, BACKGROUND_COLOR, SCREEN_WIDTH, SCREEN_HEIGHT, FPS

clock = pygame.time.Clock()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

game_map = Map(AMOUNT_OF_ROWS, AMOUNT_OF_COLUMNS)

game_map.draw(screen)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill(BACKGROUND_COLOR)

    game_map.update()
    game_map.draw(screen)

    clock.tick(FPS)
