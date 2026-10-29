import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).parents[1]))
import pygame
import game_logic


class StartupTests(unittest.TestCase):
    def test_main_can_start_and_close_without_a_display(self):
        with patch('pygame.event.get', return_value=[pygame.event.Event(pygame.QUIT)]):
            game_logic.main()
        self.assertFalse(pygame.get_init())


if __name__ == '__main__':
    unittest.main()
