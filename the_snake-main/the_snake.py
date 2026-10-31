from random import choice, randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Центральная точка игрового поля:
SCREEN_CENTER = (
    (SCREEN_WIDTH // 2) // GRID_SIZE * GRID_SIZE,
    (SCREEN_HEIGHT // 2) // GRID_SIZE * GRID_SIZE,
)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Словарь допустимых переходов направления по нажатой клавише:
DIRECTION_MAP = {
    (pygame.K_UP, LEFT): UP,
    (pygame.K_UP, RIGHT): UP,
    (pygame.K_DOWN, LEFT): DOWN,
    (pygame.K_DOWN, RIGHT): DOWN,
    (pygame.K_LEFT, UP): LEFT,
    (pygame.K_LEFT, DOWN): LEFT,
    (pygame.K_RIGHT, UP): RIGHT,
    (pygame.K_RIGHT, DOWN): RIGHT,
}

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()

# Множество всех ячеек игрового поля (для быстрого выбора свободной ячейки):
ALL_CELLS = set(
    (x * GRID_SIZE, y * GRID_SIZE)
    for x in range(GRID_WIDTH)
    for y in range(GRID_HEIGHT)
)


class GameObject:
    """Базовый класс для игровых объектов на поле."""

    def __init__(self, body_color=None):
        """Инициализирует позицию объекта в центре поля и его цвет."""
        self.position = SCREEN_CENTER
        self.body_color = body_color

    def draw(self):
        """Отрисовывает объект на игровом поле.

        Переопределяется в дочерних классах.
        """
        pass

    def draw_cell(self, position, color=None):
        """Закрашивает одну ячейку игрового поля заданным цветом."""
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, color or self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Класс, описывающий яблоко и действия с ним."""

    def __init__(self, occupied_cells=None):
        """Задаёт цвет яблока и устанавливает случайную позицию."""
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position(occupied_cells or (self.position,))

    def randomize_position(self, occupied_cells):
        """Устанавливает случайную позицию яблока вне занятых ячеек."""
        self.position = choice(tuple(ALL_CELLS - set(occupied_cells)))

    def draw(self):
        """Отрисовывает яблоко на игровом поле."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Класс, описывающий змейку и её поведение."""

    def __init__(self):
        """Инициализирует начальное состояние змейки."""
        super().__init__(body_color=SNAKE_COLOR)
        self.reset()

    def update_direction(self, new_direction):
        """Обновляет направление движения змейки."""
        self.direction = new_direction

    def move(self):
        """Обновляет позицию змейки: добавляет новую голову и удаляет хвост.

        Если змейка не увеличилась в длину, последний сегмент удаляется;
        при выходе за границу поля змейка появляется с противоположной
        стороны.
        """
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT,
        )

        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self):
        """Отрисовывает змейку, затирая след последнего сегмента."""
        self.draw_cell(self.positions[0])

        if self.last:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR)

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        self.length = 1
        self.positions = [SCREEN_CENTER]
        self.direction = choice((UP, DOWN, LEFT, RIGHT))
        self.last = None
        screen.fill(BOARD_BACKGROUND_COLOR)


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш и завершение работы программы."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit
            new_direction = DIRECTION_MAP.get(
                (event.key, game_object.direction), game_object.direction
            )
            game_object.update_direction(new_direction)


def main():
    """Запускает инициализацию и основной игровой цикл."""
    pygame.init()
    snake = Snake()
    apple = Apple(snake.positions)
    record_length = snake.length

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)
        elif snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(snake.positions)

        record_length = max(record_length, snake.length)
        pygame.display.set_caption(f'Змейка | Рекорд: {record_length}')

        snake.draw()
        apple.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()