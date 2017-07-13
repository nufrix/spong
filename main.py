# -*- coding: utf-8 -*-
import random
import pygame

from exceptions import GameOverException
from objects import MiddleLine, Paddle, Frame, Ball, Score

pygame.init()

# Colors
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)
DARK_GREY = (40, 40, 40)

# Keys
A_BUTTON = 97
Q_BUTTON = 113
UP_BUTTON = 273
DOWN_BUTTON = 274

# Mouse button types
LEFT_MOUSE = 1
RIGHT_MOUSE = 3

# Sizes
POD_WIDTH = 32
POD_HEIGHT = 145
POD_OFFSET = 32  # How many pixels is between the side and the pod
BALL_WIDTH = BALL_HEIGHT = 16
SCORE_WIDTH = 256
SCORE_HEIGHT = 256


class Pong(object):
    def __init__(self):
        # Screen settings
        display = pygame.display.Info()
        self.screen_width = int(display.current_w / 2)
        self.screen_height = int(display.current_h / 2)

        # screen = pygame.display.set_mode([screen_width,screen_height], pygame.FULLSCREEN, 32)
        self.screen = pygame.display.set_mode([self.screen_width, self.screen_height])

        # Font and images
        self.sprite = pygame.sprite.Sprite()
        image = pygame.image.load("seznam_icon.png")
        scaled_image = pygame.transform.smoothscale(image, (BALL_WIDTH, BALL_HEIGHT))  # or scale
        self.sprite.image = scaled_image
        self.sprite.rect = self.sprite.image.get_rect()
        self.sprite.rect.topleft = (int(self.screen_width / 2) - 32, random.randint(0, self.screen_height) - 32)  # Place the ball somewhere in the middle

        # State
        self.state = {
            'player1': {
                'score': 0,
                'moving_up': False,
                'moving_down': False,
                'movement_speed': 6
            },
            'player2': {
                'score': 0,
                'moving_up': False,
                'moving_down': False,
                'movement_speed': 6
            }
        }

        self.clock = pygame.time.Clock()

        # Initialize game objects
        self._initialize_game_objects()

    def _compute_player_pods_initial_positions(self):
        position1 = (POD_OFFSET, int(self.screen.get_height() / 2) - int(POD_HEIGHT / 2))
        position2 = (self.screen.get_width() - (POD_WIDTH + POD_OFFSET), int(self.screen.get_height() / 2) - int(POD_HEIGHT / 2))
        return position1, position2

    def _compute_player_score_positions(self):
        position1 = (int(self.screen.get_width() / 4) - int(SCORE_WIDTH / 2), int(self.screen.get_height() / 2) - int(SCORE_HEIGHT / 2))
        position2 = (int(self.screen.get_width() / 4) * 3 - int(SCORE_WIDTH / 2), int(self.screen.get_height() / 2) - int(SCORE_HEIGHT / 2))
        return position1, position2

    def _initialize_game_objects(self):
        self.screen.fill(BLACK)
        self.line = MiddleLine(GREY, self.screen, (int(self.screen_width / 2), 0), 1, self.screen_height)
        pod_player1_position, pod_player2_position = self._compute_player_pods_initial_positions()
        self.pod_player1 = Paddle('seznam_logo.png', self.screen, pod_player1_position, POD_WIDTH, POD_HEIGHT)
        self.pod_player2 = Paddle('seznam_logo.png', self.screen, pod_player2_position, POD_WIDTH, POD_HEIGHT)
        score_player1_position, score_player2_position = self._compute_player_score_positions()
        self.score_player1 = Score(self.state['player1']['score'], DARK_GREY, self.screen, score_player1_position, width=SCORE_WIDTH, heigth=SCORE_HEIGHT)
        self.score_player2 = Score(self.state['player2']['score'], DARK_GREY, self.screen, score_player2_position, width=SCORE_WIDTH, heigth=SCORE_HEIGHT)
        self.frame = Frame(WHITE, self.screen, (0, 0), self.screen_width, self.screen_height, border=1)
        self.ball = Ball([5, 5], 'seznam_icon.png', self.screen, width=BALL_WIDTH, height=BALL_HEIGHT)
        pygame.display.flip()

    def generate_random_color(self):
        return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

    def run(self):
        running = True
        while running:
            # Reset playground
            self.screen.fill(BLACK)
            self.line.render()
            self.frame.render()
            self.score_player1.render()
            self.score_player2.render()

            # Movement
            #
            # Because we move on the Y axis, we have to have "reversed" movement.
            if self.state['player1']['moving_up']:
                self.pod_player1.move(0, -self.state['player1']['movement_speed'], increment=True)
            if self.state['player1']['moving_down']:
                self.pod_player1.move(0, self.state['player1']['movement_speed'], increment=True)
            if self.state['player2']['moving_up']:
                self.pod_player2.move(0, -self.state['player2']['movement_speed'], increment=True)
            if self.state['player2']['moving_down']:
                self.pod_player2.move(0, self.state['player2']['movement_speed'], increment=True)

            # Events
            for event in pygame.event.get():
                # Cant quit on an event or when Escape button is pressed.
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False

                # Actions
                if event.type == pygame.KEYDOWN and event.key == Q_BUTTON:
                    self.state['player1']['moving_up'] = True
                    self.state['player1']['moving_down'] = False
                if event.type == pygame.KEYDOWN and event.key == UP_BUTTON:
                    self.state['player2']['moving_up'] = True
                    self.state['player2']['moving_down'] = False
                if event.type == pygame.KEYDOWN and event.key == A_BUTTON:
                    self.state['player1']['moving_up'] = False
                    self.state['player1']['moving_down'] = True
                if event.type == pygame.KEYDOWN and event.key == DOWN_BUTTON:
                    self.state['player2']['moving_up'] = False
                    self.state['player2']['moving_down'] = True
                if event.type == pygame.KEYUP and event.key in (A_BUTTON, Q_BUTTON):
                    self.state['player1']['moving_up'] = False
                    self.state['player1']['moving_down'] = False
                if event.type == pygame.KEYUP and event.key in (UP_BUTTON, DOWN_BUTTON):
                    self.state['player2']['moving_up'] = False
                    self.state['player2']['moving_down'] = False

            # Player pads
            self.pod_player1.render()
            self.pod_player2.render()

            # Move the ball
            try:
                self.ball.render([self.pod_player1, self.pod_player2])
            except GameOverException as e:
                # Change the score
                self.state[e.winning_player_info]['score'] += 1

                # Reset the playground
                self._initialize_game_objects()
                continue
            pygame.display.flip()

            self.clock.tick(60)  # 60 FPS

        pygame.quit()


if __name__ == '__main__':
    pong = Pong()
    pong.run()
