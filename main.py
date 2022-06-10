import numpy as np
from mpi4py import MPI
import pygame
from settings import *

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()
p = 0.5
n_of_sub_rows = NUMBER_OF_ROWS // size + 2

def exchange_boundaries_up(sub_grid):
        comm.send(sub_grid[n_of_sub_rows - 2, :], dest=rank + 1)
        sub_grid[n_of_sub_rows - 1, :]=comm.recv(source=rank + 1)
        return 0

def exchange_boundaries_down(sub_grid):
        comm.send(sub_grid[1, :], dest=rank - 1)
        sub_grid[0, :] = comm.recv(source=rank - 1)
        return 0

def compute_new_grid(sub_grid):
    temp_grid = np.copy(sub_grid)
    for row_index in range(1, n_of_sub_rows - 1):
        for col_index in range(1, NUMBER_OF_COLUMNS - 1):
            neighbour_sum = (sub_grid[row_index - 1, col_index - 1] + sub_grid[row_index - 1, col_index] + sub_grid[row_index - 1, col_index + 1] + sub_grid[row_index, col_index - 1] + sub_grid[row_index, col_index + 1] + sub_grid[row_index + 1, col_index - 1] + sub_grid[row_index + 1, col_index] + sub_grid[row_index + 1, col_index + 1])
            if sub_grid[row_index, col_index] == 1:
                if neighbour_sum < 2:
                    temp_grid[row_index, col_index] = 0
                elif neighbour_sum > 3:
                    temp_grid[row_index, col_index] = 0
                else:
                    temp_grid[row_index, col_index] = 1
            if sub_grid[row_index, col_index] == 0:
                if neighbour_sum == 3:
                    temp_grid[row_index, col_index] = 1
                else:
                    temp_grid[row_index, col_index] = 0
    sub_grid = np.copy(temp_grid)
    return sub_grid

def draw(screen, map):
    for row_index in range(len(map)):
        for col_index in range(len(map[0])):
            if map[row_index][col_index] == 1:
                # print(row_index, col_index)
                pygame.draw.rect(
                    screen,
                    CELL_COLOR,
                    pygame.Rect(row_index * CELL_SIZE, col_index * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                pygame.display.update()

rand_grid = np.random.binomial(1, p, size=(n_of_sub_rows + 2) * NUMBER_OF_COLUMNS)
sub_grid = np.reshape(rand_grid, (n_of_sub_rows + 2, NUMBER_OF_COLUMNS))

sub_grid[:, 0] = 0
sub_grid[:, -1] = 0

if rank == 0:
    sub_grid[0, :] = 1

oldGrid = comm.gather(sub_grid[1:n_of_sub_rows - 1, :], root=0)
for i in range(1,100):
    sub_grid = compute_new_grid(sub_grid)
    if rank == 0:
        exchange_boundaries_up(sub_grid)
    elif rank == size-1:
        exchange_boundaries_down(sub_grid)
    else:
        exchange_boundaries_up(sub_grid)
        exchange_boundaries_down(sub_grid)
    newGrid = comm.gather(sub_grid[1:n_of_sub_rows - 1, :], root=0)
    if rank == 0:
        clock = pygame.time.Clock()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        result= np.vstack(newGrid)
        screen.fill(BACKGROUND_COLOR)
        draw(screen, result)
        clock.tick(FPS)