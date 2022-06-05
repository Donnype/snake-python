import os
import random
import sys
import termios
import time
import tty
from dataclasses import dataclass
from enum import Enum
from threading import Thread
from typing import List


class CHAR(Enum):
    HEAD = "\033[1;34mO\033[0m"
    BODY = "\033[1;34mo\033[0m"
    APPLE = "\033[0;31mA\033[0m"

    BOARDER = "\033[0;36m#\033[0m"
    EMPTY = " "


@dataclass
class Board:
    data: List[List[str]]


@dataclass
class Position:
    x: int
    y: int

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


@dataclass
class Game:
    snake: List[Position]  # First position is the head
    snake_direction: str
    apple: Position
    board_size: int


def determine_char(position: Position, game: Game):
    if position == game.apple:
        return CHAR.APPLE

    for i, segment in enumerate(game.snake):
        if position == segment:
            return CHAR.HEAD if i == 0 else CHAR.BODY

    return CHAR.EMPTY


def board_from_game(game: Game):
    data = []

    for i in range(game.board_size):
        line = []
        for j in range(game.board_size):
            line.append(determine_char(Position(j, i), game).value)

        data.append(line)

    return Board(data=data)


def print_board(board: Board):
    content = (len(board.data[0]) + 2)*CHAR.BOARDER.value + "\n"

    for line in board.data:
        content += CHAR.BOARDER.value + "".join(line) + CHAR.BOARDER.value + "\n"

    content += (len(board.data[0]) + 2)*CHAR.BOARDER.value

    os.system("clear")
    sys.stdout.write(content)
    sys.stdout.flush()


def advance(game: Game):
    head, *body, tail = game.snake

    if game.snake_direction == "up":
        new_head = Position(head.x, (head.y - 1) % game.board_size)

    if game.snake_direction == "down":
        new_head = Position(head.x, (head.y + 1) % game.board_size)

    if game.snake_direction == "left":
        new_head = Position((head.x - 1) % game.board_size, head.y)

    if game.snake_direction == "right":
        new_head = Position((head.x + 1) % game.board_size, head.y)

    assert new_head not in body, "Game over!"

    if new_head == game.apple:
        game.apple = new_apple(game.snake, game.board_size)
        body.append(tail)  # Move snake head to the apple but keep the tail

    return Game(
        snake=[new_head, head] + body,
        snake_direction=game.snake_direction,
        apple=game.apple,
        board_size=game.board_size,
    )


def main_loop(step_size):
    global game

    while True:
        try:
            game = advance(game)
        except AssertionError:
            print("\n\nGAME OVER\n")
            print(f"Points: {len(game.snake)}\n\n")
            break

        board = board_from_game(game)
        print_board(board)
        time.sleep(step_size)


def key_listener():
    global game
   
    up, down, right, left = "A", "B", "C", "D"  # Arrow characters on macOS

    def determine_direction(char: str):
        if char == up and game.snake_direction != "down":
            return "up"

        if char == down and game.snake_direction != "up":
            return "down"

        if char == left and game.snake_direction != "right":
            return "left"

        if char == right and game.snake_direction != "left":
            return "right"


    while True:
        if not bytes(sys.stdin.read(1), "utf-8") == b"\x1b":  # blocking read call
            continue

        char = sys.stdin.read(1)

        if not char == "[":
            continue

        char = sys.stdin.read(1)
        game.snake_direction = determine_direction(char) or game.snake_direction


def random_position(board_size: int) -> Position:
    return Position(x=random.randint(1, board_size-1), y=random.randint(1, board_size-1))


def new_apple(snake: List[Position], board_size: int) -> Position:
    apple = random_position(board_size)

    while apple in snake:
        apple = random_position(board_size)

    return apple


if __name__ == "__main__":
    tattr = termios.tcgetattr(sys.stdin.fileno()) 
    tty.setcbreak(sys.stdin.fileno(), termios.TCSANOW)  # Disable stdin line buffering
 
    board_size = 25
    snake = [
        Position(2, 3),
        Position(3, 3),
        Position(4, 3),
        Position(5, 3),
    ]

    def main_with_step():
        return main_loop(step_size=0.15)

    game = Game(
        snake=snake,
        snake_direction="up",
        apple=new_apple(snake, board_size),
        board_size=board_size,
    )

    Thread(target=main_with_step).start()
    Thread(target=key_listener).start()

