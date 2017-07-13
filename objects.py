# -*- coding: utf-8 -*-
import pygame
import random

from exceptions import GameOverException, OutOfScreenException


class GameObject(object):
    def __init__(self, screen, position, width, height):
        self.screen = screen
        self.position = position
        self.width = width
        self.height = height
        self.rect = pygame.Rect(position[0], position[1], width, height)

    @property
    def position_x(self):
        return self.position[0]

    @property
    def position_y(self):
        return self.position[1]

    @property
    def screen_width(self):
        return self.screen.get_width()

    @property
    def screen_height(self):
        return self.screen.get_height()

    def calculate_new_position(self, position_x, position_y, increment):
        """
        Calculates the new position of the object where it will be moved.
        """
        if increment:
            new_position_x = self.position_x + position_x
            new_position_y = self.position_y + position_y
        else:
            new_position_x = position_x
            new_position_y = position_y

        if self.will_move_out_of_screen(new_position_x, new_position_y):
            raise OutOfScreenException

        return new_position_x, new_position_y

    def will_move_out_of_screen(self, new_position_x, new_position_y):
        """
        Returns True if any part of the object is out of the screen.
        """
        # Right down part of the object
        if (new_position_x + self.width) > self.screen_width:
            return True
        elif (new_position_y + self.height) > self.screen_height:
            return True
        # Top left part of the object
        elif new_position_x < 0:
            return True
        elif new_position_y < 0:
            return True

        return False

    def move(self, position_x, position_y, increment=False):
        """
        If possible, moves the object to given coordinates. It is possible to
        move the object by given amount of pixels, in this case, the argument
        increment must be set to True.

        When the object can't be moved, exception is raised.
        """
        try:
            new_position_x, new_position_y = self.calculate_new_position(position_x, position_y, increment)
        except OutOfScreenException:
            return  # Log it maybe?
        self.position = (new_position_x, new_position_y)
        self.rect = pygame.Rect(new_position_x, new_position_y, self.width, self.height)

    def render(self):
        """
        Rendering method that must be defined for each object types.
        """
        raise NotImplementedError


class Frame(GameObject):
    """
    Frame that surrounds the screen
    """
    # TODO: Add limit to playground size with respect to the frame.
    def __init__(self, color, screen, position, width=16, heigth=64, border=0):
        self.color = color
        self.border = border
        super(Frame, self).__init__(screen, position, width, heigth)

    def render(self):
        pygame.draw.rect(self.screen,
                         self.color,
                         self.rect,
                         self.border)


class MiddleLine(Frame):
    """
    Line that separates playground into two parts.

    The line is drawn as a rectangle with width equal to 1.
    """
    pass


class SpriteObject(GameObject):
    """
    Ball that bounces around the playground.
    """

    def __init__(self, image_path, screen, position, width, height):
        super(SpriteObject, self).__init__(screen, position, width, height)
        self.sprite = pygame.sprite.Sprite()
        image = pygame.image.load(image_path)
        scaled_image = pygame.transform.smoothscale(image, (width, height))  # or scale
        self.sprite.image = scaled_image
        self.sprite.mask = pygame.mask.from_surface(scaled_image)
        self.sprite.rect = self.sprite.image.get_rect()
        self.sprite.rect.topleft = position

        self.color = (0, 255, 0)

    def pre_render(self, collision_objects):
        pass

    def render(self, collision_objects=[]):
        self.pre_render(collision_objects)
        self.screen.blit(self.sprite.image, self.sprite.rect)

    def move(self, position_x, position_y, increment=False):
        try:
            new_position_x, new_position_y = self.calculate_new_position(position_x, position_y, increment)
        except OutOfScreenException:
            return  # Log it maybe?
        self.position = (new_position_x, new_position_y)
        self.sprite.rect = pygame.Rect(new_position_x, new_position_y, self.width, self.height)


class Ball(SpriteObject):
    """
    Ball that bounces around the playground.

    The ball should bounce like this http://rembound.com/files/pong-ball-paddle-collision.png
    """
    def __init__(self, velocity, image_path, screen, width=64, height=64):
        self.velocity = [random.choice([-1, 1]) * x for x in velocity]  # Randomly choose the initial direction
        position = (int(screen.get_width() / 2) - int(width / 2), random.randint(0, screen.get_height()) - int(height / 2))  # Place the ball somewhere in the middle
        super(Ball, self).__init__(image_path, screen, position, width, height)

    def move_ball(self, collision_objects):
        """
        I want it to move by itself in different manner.

        It doesn't require a precomputed position because it computes its next
        position from given velocity and current position. The ball should bounce
        within the screen.
        """

        # DEBUG
        # pygame.sprite.collide_mask(SpriteLeft, SpriteRight)
        # ball_rect = self.sprite.rect
        # # In most cases, the ball will hit the pod with its left or right side,
        # # so I can make some kind of optimization by not creating other 2 rects
        # # too soon :)
        #
        # left_rect = pygame.Rect(ball_rect.left - 1, ball_rect.top - 1, 1, ball_rect.height)
        # right_rect = pygame.Rect((ball_rect.left + ball_rect.width) - 1, ball_rect.top - 1, 1, ball_rect.height)
        # top_rect = pygame.Rect(ball_rect.left - 1, ball_rect.top - 1, ball_rect.width, 1)
        # bottom_rect = pygame.Rect(ball_rect.left - 1, (ball_rect.top + ball_rect.height) - 1, ball_rect.width, 1)
        # # pygame.draw.rect(self.screen, (0, 0, 255), self.sprite.rect, 1)
        # # pygame.draw.rect(self.screen, (255, 0, 0), topleft, 1)
        # pygame.draw.rect(self.screen, self.color, left_rect, 1)
        # pygame.draw.rect(self.screen, self.color, right_rect, 1)
        # pygame.draw.rect(self.screen, self.color, top_rect, 1)
        # pygame.draw.rect(self.screen, self.color, bottom_rect, 1)
        # /DEBUG

        # Compute the movement

        # Did it hit the player's pods?
        #
        # If the ball collides with the player's pod, bounce the ball of the pod.
        # for collision_object in self.collision_objects:
        for collision_object in collision_objects:
            # Which side of the ball hit the pod?
            #
            # I create temporary rect that represents just the side of the ball's
            # rect and check if this side collides with the pod. I will be able
            # to properly change velocity direction with this information.

            ball_rect = self.sprite.rect
            # In most cases, the ball will hit the pod with its left or right side,
            # so I can make some kind of optimization by not creating other 2 rects
            # too soon :)

            left_rect = pygame.Rect(ball_rect.left - 1, ball_rect.top - 1, 1, ball_rect.height)
            if left_rect.colliderect(collision_object.sprite.rect):
                self.velocity[0] = -self.velocity[0]
                break
            right_rect = pygame.Rect((ball_rect.left + ball_rect.width) - 1, ball_rect.top - 1, 1, ball_rect.height)
            if right_rect.colliderect(collision_object.sprite.rect):
                self.velocity[0] = -self.velocity[0]
                break
            top_rect = pygame.Rect(ball_rect.left - 1, ball_rect.top - 1, ball_rect.width, 1)
            if top_rect.colliderect(collision_object.sprite.rect):
                self.velocity[1] = -self.velocity[1]
                break
            bottom_rect = pygame.Rect(ball_rect.left - 1, (ball_rect.top + ball_rect.height) - 1, ball_rect.width, 1)
            if bottom_rect.colliderect(collision_object.sprite.rect):
                self.velocity[1] = -self.velocity[1]
                break

        # Right side
        if self.sprite.rect.topleft[0] + self.sprite.rect.width >= self.screen_width and self.velocity[0] > 0:
            # self.velocity[0] = -self.velocity[0]
            raise GameOverException('player1')
        # Left side
        if self.sprite.rect.topleft[0] <= 0 and self.velocity[0] < 0:
            # self.velocity[0] = -self.velocity[0]
            raise GameOverException('player2')
        # Bottom side
        if self.sprite.rect.topleft[1] + self.sprite.rect.height >= self.screen_height and self.velocity[1] > 0:
            self.velocity[1] = -self.velocity[1]
        # Top side
        if self.sprite.rect.topleft[1] <= 0 and self.velocity[1] < 0:
            self.velocity[1] = -self.velocity[1]

        # Move the ball
        self.sprite.rect.topleft = (self.sprite.rect.topleft[0] + self.velocity[0],
                                    self.sprite.rect.topleft[1] + self.velocity[1])

    def pre_render(self, collision_objects):
        self.move_ball(collision_objects)

    def render(self, collision_objects):
        """
        Because I have to have list of moved (aka updated) objects, that will
        cause the ball to bounce, I have to change the signature of this method.
        """
        self.pre_render(collision_objects)
        self.screen.blit(self.sprite.image, self.sprite.rect)


class Paddle(SpriteObject):
    """
    Ractangle that is operated by the player and is used to block the ball from
    moving out of the playground.
    """
    pass


class Score(GameObject):
    """
    Current game score for given player
    """
    def __init__(self, score_value, color, screen, position, width=128, heigth=128, font_file='font.ttf'):
        self.score_value = score_value
        self.color = color
        self.font = pygame.font.Font(font_file, max([width, heigth]))
        super(Score, self).__init__(screen, position, width, heigth)

    def render(self):
        text = self.font.render(str(self.score_value), 1, self.color)
        textpos = pygame.Rect(self.position_x, self.position_y, self.width, self.height)
        # textpos.centerx = screen.get_rect().centerx
        self.screen.blit(text, textpos)
