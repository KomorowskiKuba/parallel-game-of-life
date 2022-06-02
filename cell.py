import enum


class State(enum.Enum):
    dead = 0
    alive = 1


class Cell:
    def __init__(self):
        self.status = State.dead

    def is_alive(self):
        return self.status == State.alive

    def set_alive(self):
        self.status = State.alive

    def set_dead(self):
        self.status = State.dead