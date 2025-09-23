"""
Unit tests for board.
"""

import numpy as np

from gym_collabsort.board.board import Board


def test_board() -> None:
    board = Board()
    assert len(board.objects) == 0

    board.populate(rng=np.random.default_rng())
    assert len(board.objects) == board.config.n_objects

    board.draw()
    frame = board.get_frame()
    assert frame.ndim == 3
    assert frame.shape[0] == board.config.window_dimensions[1]
    assert frame.shape[1] == board.config.board_width
