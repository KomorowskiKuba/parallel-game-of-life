from random import randint

import pygame.draw

from cell import Cell
from settings import CELL_SIZE, CELL_COLOR


class Map:
    def __init__(self, amount_of_rows, amount_of_columns):
        self.amount_of_rows = amount_of_rows
        self.amount_of_columns = amount_of_columns
        self.map = [[Cell() for _ in range(amount_of_columns)] for _ in range(amount_of_rows)]
        self.generate()

    def generate(self):
        for row in self.map:
            for cell in row:
                if randint(0, 2) == 1:
                    cell.set_alive()

    def draw(self, screen):
        for row_index in range(self.amount_of_rows):
            for col_index in range(self.amount_of_columns):
                if self.map[row_index][col_index].is_alive():
                    print(row_index, col_index)
                    pygame.draw.rect(
                        screen,
                        CELL_COLOR,
                        pygame.Rect(row_index * CELL_SIZE, col_index * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                    pygame.display.update()

    def check_neighbours(self, check_row_index, check_column_index):
        search_min = -1
        search_max = 2

        neighbours = []

        for row_index in range(search_min, search_max):
            for col_index in range(search_min, search_max):
                neighbour_row_index = check_row_index + row_index
                neighbour_col_index = check_column_index + col_index

                valid_neighbour = True

                if (neighbour_row_index == check_row_index and neighbour_col_index == check_column_index) or \
                        (neighbour_row_index < 0 or neighbour_row_index >= self.amount_of_rows) or\
                        (neighbour_col_index < 0 or neighbour_col_index >= self.amount_of_columns):
                    valid_neighbour = False

                if valid_neighbour:
                    neighbours.append(self.map[neighbour_row_index][neighbour_col_index])

        return neighbours

    def update(self):
        to_kill = []
        to_resurrect = []

        for row_index in range(len(self.map)):
            for col_index in range(len(self.map[row_index])):
                alive_count = 0
                neighbours = self.check_neighbours(row_index, col_index)

                for neighbour in neighbours:
                    if neighbour.is_alive():
                        alive_count += 1

                current_cell = self.map[row_index][col_index]
                current_cell_status = current_cell.is_alive()

                if current_cell_status:
                    if alive_count < 2 or alive_count > 3:
                        to_kill.append(current_cell)

                    elif alive_count == 3 or alive_count == 2:
                        to_resurrect.append(current_cell)

                else:
                    if alive_count == 3:
                        to_resurrect.append(current_cell)

        for cell in to_resurrect:
            cell.set_alive()

        for cell in to_kill:
            cell.set_dead()
