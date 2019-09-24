## Requirements: curses, msvcrt. Runs only on Windows
from enum import Enum
from random import randrange
import threading
from queue import Queue
import msvcrt
import time
import curses

GAME_DELAY = 0.25
BOARD_WIDTH = 24
BOARD_HEIGHT = 24


class OBJECTS_SYMBOLS(Enum):
    WALL = '■'
    SNAKE = '•'
    APPLE = 'Ó'


class DIRECTION(Enum):
    LEFT = 75
    RIGHT = 77
    UP = 72
    DOWN = 80


class Board():
    # nXm board
    def __init__(self, n, m):
        self.board = []
        self.create_empty_board(n, m)
        self.create_walls(n, m)

    def create_empty_board(self, n, m):
        for i in range(m):
            self.board.append([])

        for i in range(m):
            for j in range(n):
                self.board[i].append(0)

    def create_walls(self, n, m):
        for i in range(m):
            self.board[i][0] = OBJECTS_SYMBOLS.WALL.value
            self.board[i][n - 1] =  OBJECTS_SYMBOLS.WALL.value

        for j in range(n):
            self.board[0][j] = OBJECTS_SYMBOLS.WALL.value
            self.board[m - 1][j] = OBJECTS_SYMBOLS.WALL.value

    def __str__(self):
        s = ""
        s1 = ""

        for row in self.board:
            for elem in row:
                if elem == 0:
                    elem = " "
                s1 += "{}".format(elem)
            s = "{}\n".format(s1) + s
            s1 = ""
        return s


class Node():
    def __init__(self, x, y, next=None):
        self.x = x
        self.y = y
        self.next = next

    def __str__(self):
        return str((self.x, self.y))


class Snake:
    def __init__(self, board):
        self.head = Node(1, 2)
        self.tail = Node(1, 1, self.head)
        self.board = board

    def eat_apple(self, node):
        self.board[node.x][node.y] = OBJECTS_SYMBOLS.SNAKE.value
        self.head.next = node
        self.head = self.head.next

    def move(self, direction):
        new_head = None

        if direction == DIRECTION.UP.value:
            new_head = Node(self.head.x + 1, self.head.y)
        elif direction == DIRECTION.DOWN.value:
            new_head = Node(self.head.x - 1, self.head.y)
        elif direction == DIRECTION.LEFT.value:
            new_head = Node(self.head.x, self.head.y - 1)
        elif direction == DIRECTION.RIGHT.value:
            new_head = Node(self.head.x, self.head.y + 1)

        value = self.board[new_head.x][new_head.y]

        if value == OBJECTS_SYMBOLS.WALL.value or value == OBJECTS_SYMBOLS.SNAKE.value:
            return False

        elif value == OBJECTS_SYMBOLS.APPLE.value:
            self.eat_apple(new_head)
            return OBJECTS_SYMBOLS.APPLE.value

        else:
            self.board[new_head.x][new_head.y] = OBJECTS_SYMBOLS.SNAKE.value
            self.board[self.tail.x][self.tail.y] = 0
            self.head.next = new_head
            self.tail = self.tail.next
            self.head = self.head.next
            return True


class Game():
    def __init__(self):
        self.score = 0
        self.n = BOARD_HEIGHT
        self.m = BOARD_WIDTH
        self.board_tbl = Board(self.n, self.m)
        self.board = self.board_tbl.board
        self.snake = Snake(self.board)
        self.board[self.snake.tail.x][self.snake.tail.y] = OBJECTS_SYMBOLS.SNAKE.value
        self.board[self.snake.head.x][self.snake.head.y] = OBJECTS_SYMBOLS.SNAKE.value
        self.direction = DIRECTION.RIGHT.value
        self.directions = Queue()
        self.th = threading.Thread(target=self.add_directions_to_queue, args=(self.directions,))

    def generate_apple(self):
        apple_loc = Node(randrange(1, self.m - 1), randrange(1, self.n - 1))
        while self.board[apple_loc.x][apple_loc.y]:
            apple_loc = Node(randrange(1, self.m - 1), randrange(1, self.n - 1))
        self.board[apple_loc.x][apple_loc.y] = OBJECTS_SYMBOLS.APPLE.value
        return apple_loc

    def add_directions_to_queue(self, directions):
        while True:
            x = int.from_bytes(msvcrt.getch(), "big")
            if x == ord('e'):
                exit(0)

            x = int.from_bytes(msvcrt.getch(), "big")
            if not directions.empty() and directions.queue[0] == x:
                pass
            else:
                directions.put(x)

    def start(self):
        self.th.start()
        screen = curses.initscr()
        self.generate_apple()

        while True:
            screen.clear()

            screen.addstr("#### score:{} ####\n".format(self.score))
            if not self.directions.empty():
                self.direction = self.directions.get_nowait()

            result = self.snake.move(self.direction)
            screen.addstr(self.board_tbl.__str__())

            if result == OBJECTS_SYMBOLS.APPLE.value:
                self.score += 1
                self.generate_apple()

            if result == False:
                screen.addstr("GAME OVER, press [e] for exit")
                screen.refresh()
                break

            screen.refresh()

            time.sleep(GAME_DELAY)


if __name__ == "__main__":
    g = Game()
    g.start()
