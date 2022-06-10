import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'

import sys
import time
import pygame
import numpy as np

from mpi4py import MPI

from settings import *

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

start = time.time()

amount_of_sub_rows = NUMBER_OF_ROWS // size + 2


def exchange_boundaries_up(_sub_grid):
    comm.send(_sub_grid[amount_of_sub_rows - 2, :], dest=rank + 1)
    _sub_grid[amount_of_sub_rows - 1, :] = comm.recv(source=rank + 1)


def exchange_boundaries_down(_sub_grid):
    comm.send(_sub_grid[1, :], dest=rank - 1)
    _sub_grid[0, :] = comm.recv(source=rank - 1)


def compute_new_grid(_sub_grid):
    temp_grid = np.copy(_sub_grid)

    for row_index in range(1, amount_of_sub_rows - 1):
        for col_index in range(1, NUMBER_OF_COLUMNS - 1):
            neighbour_sum = (_sub_grid[row_index - 1, col_index - 1] + _sub_grid[row_index - 1, col_index] +
                             _sub_grid[row_index - 1, col_index + 1] + _sub_grid[row_index, col_index - 1] +
                             _sub_grid[row_index, col_index + 1] + _sub_grid[row_index + 1, col_index - 1] +
                             _sub_grid[row_index + 1, col_index] + _sub_grid[row_index + 1, col_index + 1])

            if _sub_grid[row_index, col_index] == 1:
                if neighbour_sum < 2 or neighbour_sum > 3:
                    temp_grid[row_index, col_index] = 0
                else:
                    temp_grid[row_index, col_index] = 1
            elif _sub_grid[row_index, col_index] == 0:
                if neighbour_sum == 3:
                    temp_grid[row_index, col_index] = 1
                else:
                    temp_grid[row_index, col_index] = 0

    return temp_grid


def draw(_screen, _map):
    for row_index in range(len(_map)):
        for col_index in range(len(_map[0])):
            if _map[row_index][col_index] == 1:
                pygame.draw.rect(
                    _screen,
                    CELL_COLOR,
                    pygame.Rect(row_index * CELL_SIZE, col_index * CELL_SIZE, CELL_SIZE, CELL_SIZE))

                pygame.display.update()


rand_grid = np.random.binomial(1, RANDOM_INIT, size=(amount_of_sub_rows + 2) * NUMBER_OF_COLUMNS)
sub_grid = np.reshape(rand_grid, (amount_of_sub_rows + 2, NUMBER_OF_COLUMNS))

sub_grid[:, 0] = 0
sub_grid[:, -1] = 0
sub_grid[0, :] = 1

if rank == 0:
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

oldGrid = comm.gather(sub_grid[1: amount_of_sub_rows - 1, :], root=0)

for i in range(1, AMOUNT_OF_ITERATIONS):
    sub_grid = compute_new_grid(sub_grid)

    if rank == 0:
        exchange_boundaries_up(sub_grid)
    elif rank == size - 1:
        exchange_boundaries_down(sub_grid)
    else:
        exchange_boundaries_up(sub_grid)
        exchange_boundaries_down(sub_grid)

    newGrid = comm.gather(sub_grid[1:amount_of_sub_rows - 1, :], root=0)

    if rank == 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                end = time.time()
                print('Time:', end - start)

                sys.stdout.flush()
                MPI.COMM_WORLD.Abort()
                pygame.quit()
                sys.exit()

        result = np.vstack(newGrid)
        screen.fill(BACKGROUND_COLOR)
        draw(screen, result)
        clock.tick(FPS)

if rank == 0:
    end = time.time()
    print('Time:', end - start)
