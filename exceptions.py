# -*- coding: utf-8 -*-


class OutOfScreenException(Exception):
    pass


class GameOverException(Exception):
    def __init__(self, player_info, *args, **kwargs):
        self.winning_player_info = player_info  # Which player will get the point.
        super(GameOverException, self).__init__(*args, **kwargs)


class UnsupportedPlayerException(Exception):
    pass
