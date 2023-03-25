
from random import randint
import time

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'Dot({self.x}, {self.y})'


class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску! Попробуйте еще."

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку."

class BoardWrongShipException(BoardException):
    pass


class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l
    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i
            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots

class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid

        self.count = 0

        self.field = [["O"]*self.size for _ in range(self.size)]
        self.busy = []
        self.ships = []

    def __str__(self):
        titul = " | ".join(list(map(str, [i for i in range(1, self.size + 1)])))
        res = ""
        res += f'  | {titul} |'
        for i, row in enumerate(self.field):
            res += f"\n{i+1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "O")
        return res

    def out(self, d):
        return not((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1,1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)
        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()
        if d in self.busy:
            raise BoardUsedException()
        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль подбит!")
                    return True
        self.field[d.x][d.y] = "T"
        print("Мимо")
        return False

    def begin(self):
        self.busy = []

class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class AI(Player):
    def ask(self):
        time.sleep(4)
        d = Dot(randint(0, (self.board.size - 1)), randint(0, (self.board.size - 1)))
        print(f"Ход компьютера: {d.x+1} {d.y+1} ")
        return d

class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print("Введите 2 координаты ")
                continue

            x, y = cords
            if not(x.isdigit()) or not(y.isdigit()):
                print("Введите числа")
                continue

            x, y = int(x), int(y)
            return Dot(x-1, y-1)


class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True
        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def try_board(self):
        lens = [[3, 2, 2, 1, 1, 1, 1],
                [3, 2, 2, 2, 1, 1, 1],
                [3, 3, 2, 2, 1, 1, 1],
                [4, 3, 2, 2, 1, 1, 1]]
        board = Board(size=self.size)
        attempts = 0
        for l in lens[self.size - 6]:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board


    def print_desk(self):
        print("Поле Компьютера")
        print(self.ai.board)
        print("Поле Игрока")
        print(self.us.board)



    def loop(self):
        num = 0
        while True:
            self.print_desk()
            if num % 2 == 0:
                print("Ходит игрок")
                repeat = self.us.move()
            else:
                print("Ходит компьютер")
                repeat = self.ai.move()
            if repeat:
                num -= 1
            if self.ai.board.count == 7:
                print("Игрок выиграл!!")
                break
            if self.us.board.count == 7:
                print("Компьютер выиграл :(")
                break
            num += 1


def start():
    print(f'|  Приветствуем в игре  |')
    print(f'|     МОРСКОЙ БОЙ       |')
    print(f'|     ввод: x и y       |')
    print(f'|x - строки, y - столбцы|')
    while True:
        try:
            a = int(input("Выберите длину стороны (от 6 до 9):  "))
            if 6 <= a <= 9:
                break
        except ValueError:
            print("Введите число")
            continue
        else:
            print("Некорректный ввод :(")
    g = Game(size=a)
    g.loop()
    b = input("Хотите сыграть еще раз(Y/N):  ")
    if b.lower() == "y":
        start()
    else:
        print("До свидания")

if __name__=="__main__":
    start()

