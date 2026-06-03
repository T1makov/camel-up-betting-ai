import unittest
from colorama import Fore, Back, Style, init
import random
from copy import deepcopy
import os, sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.join(current_dir, '..')
sys.path.append(parent_dir)

Pyramid = None
if not Pyramid:
    from Pyramid import Pyramid as Pyramid 

class Test_Pyramid(unittest.TestCase):
    def setUp(self):
        """runs before each test"""
        self.camel_styles= {
            "r": Back.RED+Style.BRIGHT,
            "b": Back.BLUE+Style.BRIGHT,
            "g": Back.GREEN+Style.BRIGHT,
            "y": Back.YELLOW+Style.BRIGHT,
            "p": Back.MAGENTA
        }
        self.pyramid = Pyramid(self.camel_styles)

    def test_pyramid_data_attributes(self):
        """Pyramid- Data Types"""
        self.assertIsInstance(self.pyramid.DIE_VALUES, list, "Pyramid.DIE_VALUES should return a list")
        self.assertEqual(self.pyramid.DIE_VALUES, [1, 2, 3], "Pyramid.DIE_VALUES should be [1, 2, 3]")
        self.assertIsInstance(self.pyramid.DIE_COLORS, list, "Pyramid.DIE_COLORS should return a list")
        self.assertEqual(set(self.pyramid.DIE_COLORS), set(self.camel_styles.keys()), "Pyramid.DIE_COLORS should be a list of the camel colors")
        self.assertIsInstance(self.pyramid.remaining_dice, list, "Pyramid.remaining_dice should return a list") 
        self.assertIsInstance(self.pyramid.STYLES, dict, "Pyramid.STYLES should return a dict")
        self.assertEqual(self.pyramid.STYLES, self.camel_styles, "Pyramid.STYLES should be a dict of the camel styles") 
        self.assertIsInstance(self.pyramid.shake(), tuple, "Pyramid.shake should return a tuple")
        self.assertIsInstance(self.pyramid.shake()[0], str, "Pyramid.shake should return a tuple with first element str")
        self.assertIsInstance(self.pyramid.shake()[1], int, "Pyramid.shake should return a tuple with second element int")
        
    def test_only_returns_valid_color_value(self):
        """Pyramid-- die value is 1, 2, or 3 and die color is a valid camel color"""
        for _ in range(100):
            pyramid = Pyramid(self.camel_styles)
            die = pyramid.shake()
            color, value = die
            self.assertIn(color, self.camel_styles.keys(), f"All rolled die should exist in {{self.camel_styles.keys()}}")
            self.assertIn(value, [1,2, 3], f"All rolled die should exist in {[1, 2, 3]}")

    def test_rolled_die_removed_from_pyramid(self):
        """Pyramid-- die color exists in and is removed from pyramid w/ multiple dice"""
        for _ in range(100):
            pyramid = Pyramid(self.camel_styles)
            #reset pyramid to a random number of dice
            #randomly select a number of dice to add to the pyramid
            total_die = random.choice([1, 2, 3, 4, 5]) 
            die_colors = random.sample(list(self.camel_styles.keys()), total_die) #start with a random collection of colors
            pyramid.remaining_dice = die_colors.copy()
            self.assertTrue(len(pyramid.remaining_dice)==total_die, "pyramid.remaining_dice should have length equal to total_die")
            die = pyramid.shake()
            self.assertTrue(len(pyramid.remaining_dice)==total_die-1, "pyramid whould have length reduced by 1 after rolling")
            self.assertNotIn(die[0], pyramid.remaining_dice, "Rolled die should be removed from board.pyramid")

    def test_shaking_empty_pyramid(self):
        """Pyramid-- shaking empty pyramid returns ("", 0) and has no other effect"""
        pyramid = Pyramid(self.camel_styles)
        pyramid.remaining_dice = []
        die = pyramid.shake()
        self.assertIsInstance(die, tuple, "An empty pyramid should roll a tuple")
        self.assertTrue(len(die)==2, "An empty pyramid should roll a tuple of length 2")
        self.assertEqual(die[0], "", 'An empty pyramid should roll ("", 0)')
        self.assertEqual(die[1], 0, 'An empty pyramid should roll ("", 0)')

    def test_reset_leg(self):
        """Pyramid-- rolled die is placed in dice tents"""
        for _ in range(100):
            pyramid = Pyramid(self.camel_styles)
            total_die = random.choice([1, 2, 3, 4, 5]) 
            die_colors = random.sample(list(self.camel_styles.keys()), total_die) #start with a random collection of colors
            pyramid.remaining_dice = die_colors.copy()
            pyramid.reset_leg()
            self.assertIsInstance(pyramid.remaining_dice, list, "Pyramid.reset_leg should return a list")
            self.assertEqual(set(pyramid.remaining_dice), set(self.camel_styles.keys()), "Pyramid.reset_leg should return a list of the camel colors")
            self.assertEqual(len(pyramid.remaining_dice), len(self.camel_styles.keys()), "Pyramid.reset_leg should return a list of the camel colors")

if __name__ == "__main__":
    unittest.main()