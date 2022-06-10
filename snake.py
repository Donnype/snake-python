import os, random, sys, termios, time, tty
from dataclasses import dataclass
from enum import Enum
from threading import Thread
from typing import List, Tuple, Optional

tattr = termios.tcgetattr(sys.stdin.fileno()) 
tty.setcbreak(sys.stdin.fileno(), termios.TCSANOW)  # Disable stdin line buffering

class CHAR(Enum):
    HEAD = "\033[1;34mO\033[0m"  # Some coloring
    BODY = "\033[1;34mo\033[0m"
    APPLE = "\033[0;31mA\033[0m"
    BOARDER = "\033[0;36m#\033[0m"
    EMPTY = " "

@dataclass
class Position:
    x: int
    y: int

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def translate(self, translation: Tuple[int, int], mod: int):
        return Position((self.x + translation[0]) % mod, (self.y + translation[1]) % mod)

@dataclass
class Game:
    snake: List[Position]  # First position is the head
    snake_direction: str
    apple: Position
    board_size: int

def determine_character_to_write(position: Position, game: Game) -> CHAR:
    for i, segment in enumerate(game.snake):
        if position == segment:
            return CHAR.HEAD if i == 0 else CHAR.BODY

    return CHAR.APPLE if position == game.apple else CHAR.EMPTY

def print_game(game: Game):
    content = (game.board_size + 2) * CHAR.BOARDER.value + "\n"

    for i in range(game.board_size):
        line = [determine_character_to_write(Position(j, i), game).value for j in range(game.board_size)]
        content += CHAR.BOARDER.value + "".join(line) + CHAR.BOARDER.value + "\n"

    os.system("clear")  # Clears the "frame"
    sys.stdout.write(content + (game.board_size + 2) * CHAR.BOARDER.value)  # Writes the new content

def advance(game: Game):
    old_head, *body, tail = game.snake
    translations = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}

    new_head = old_head.translate(translations[game.snake_direction], game.board_size)
    assert new_head not in body  # Else: game over...

    if new_head == game.apple:  # Snake eats an apple and grows in size
        game.apple = new_apple(game.snake, game.board_size)
        body.append(tail)  # Move snake head to the apple but keep the tail

    game.snake = [new_head, old_head] + body

def main_loop(step_size: float):
    while True:
        try:
            advance(game)
        except AssertionError:
            print(f"\n\nGAME OVER\nPoints: {len(game.snake)}\n\n")
            break

        print_game(game)
        time.sleep(step_size)

def key_listener():
    char_to_direction = {"A": "up", "B": "down", "C": "right", "D": "left"}  # Arrow characters
    char_to_forbidden_direction = {"A": "down", "B": "up", "C": "left", "D": "right"}  # Snake cannot turn 180 degrees

    def determine_direction(char):
        return None if game.snake_direction == char_to_forbidden_direction.get(char) else char_to_direction.get(char)

    while True:
        if bytes(sys.stdin.read(1), "utf-8") == b"\x1b" and sys.stdin.read(1) == "[":  # blocking arrow key checks
            game.snake_direction = determine_direction(sys.stdin.read(1)) or game.snake_direction

def new_apple(snake: List[Position], board_size: int) -> Position:
    apple = Position(x=random.randint(1, board_size-1), y=random.randint(1, board_size-1))

    while apple in snake:
        apple = Position(x=random.randint(1, board_size-1), y=random.randint(1, board_size-1))

    return apple

snake = [Position(i, 3) for i in [2, 3, 4, 5]]
game = Game(snake=snake, snake_direction="up", apple=new_apple(snake, 25), board_size=25)

Thread(target=main_loop, kwargs={"step_size": 0.15}).start()
Thread(target=key_listener).start()
