import unittest
from colorama import Fore, Back, Style, init
import os, sys
import math

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.join(current_dir, '..')
sys.path.append(parent_dir)

AI = None
if not AI:
    from AI import AI as AI 

Board = None
if not Board:
    from Board import Board as Board 

class Test_AI_roll_sequence(unittest.TestCase):
    def setUp(self):
        """runs before each test"""
        self.camel_styles= {
            "r": Back.RED+Style.BRIGHT,
            "b": Back.BLUE+Style.BRIGHT,
            "g": Back.GREEN+Style.BRIGHT,
            "y": Back.YELLOW+Style.BRIGHT,
            "p": Back.MAGENTA
        }
        self.board = Board(self.camel_styles)
        self.AI = AI(self.board)
    
    def test_0(self):
        """get_all_dice_roll_sequences- Data Type of attributes"""
        actual = self.AI.get_all_roll_sequences()
        self.assertIsInstance(actual, set, "get_all_dice_roll_sequences should return a set")
        for roll_sequence in actual:
            self.assertIsInstance(roll_sequence, tuple, "get_all_dice_roll_sequences should return a set of tuples")
            for roll in roll_sequence:
                self.assertIsInstance(roll, tuple, "get_all_dice_roll_sequences should return a set of tuple of tuple")
                self.assertTrue(len(roll)==2, "get_all_dice_roll_sequences should return a set of tuple of tuples of length 2")
                self.assertIsInstance(roll[0], str, "get_all_dice_roll_sequences should return a set of tuple of tuple with first element str")
                self.assertIsInstance(roll[1], int, "get_all_dice_roll_sequences should return a set of tuple of tuple with second element int")
    
    def test_1(self):
        """get_all_roll_sequences- 1 die color"""
        n = 1
        dice_colors=['y']
        self.board.pyramid.remaining_dice=dice_colors
        actual = self.AI.get_all_roll_sequences()
        expected = {(('y', 1),), (('y', 3),), (('y', 2),)}
        self.assertTrue(len(actual) == math.factorial(n)*3**(n), f"There should be {n}!*3^{n} possible dice roll sequences with {n} die.")
        for sequence in actual:
            self.assertIn(sequence, expected, "The full set of dice sequences should be generated.")
    
    def test_2(self):
        """get_all_roll_sequences- 2 dice colors"""
        n = 2
        dice_colors=['g','y']
        self.board.pyramid.remaining_dice=dice_colors
        actual = self.AI.get_all_roll_sequences()
        expected = {(('g', 3), ('y', 2)), (('y', 2), ('g', 1)), (('y', 3), ('g', 1)), (('g', 2), ('y', 2)), (('g', 2), ('y', 3)), (('y', 2), 
                    ('g', 2)), (('y', 1), ('g', 2)), (('g', 3), ('y', 1)), (('g', 2), ('y', 1)), (('g', 3), ('y', 3)), (('y', 3), ('g', 2)), 
                    (('y', 2), ('g', 3)), (('g', 1), ('y', 2)), (('y', 3), ('g', 3)), (('g', 1), ('y', 3)), (('y', 1), ('g', 1)), (('g', 1), 
                    ('y', 1)), (('y', 1), ('g', 3))}
        self.assertTrue(len(actual) == math.factorial(n)*3**(n), f"There should be {n}!*3^{n} possible dice roll sequences with {n} die.")
        self.assertEqual(actual, expected, "The full set of dice sequences should be generated.")
    
    def test_3(self):
        """get_all_roll_sequences- 3 dice colors"""
        n = 3
        dice_colors=['g','y','r']
        self.board.pyramid.remaining_dice=dice_colors
        actual = self.AI.get_all_roll_sequences()
        expected = {(('g', 2), ('y', 2), ('r', 2)), (('y', 3), ('g', 3), ('r', 3)), (('y', 3), ('g', 2), ('r', 3)), (('g', 3), ('y', 2), ('r', 1)), 
                    (('r', 1), ('g', 2), ('y', 3)), (('r', 3), ('y', 1), ('g', 3)), (('g', 3), ('y', 3), ('r', 2)), (('y', 2), ('r', 2), ('g', 3)), 
                    (('y', 3), ('r', 2), ('g', 1)), (('r', 2), ('g', 2), ('y', 3)), (('r', 3), ('y', 3), ('g', 3)), (('g', 1), ('r', 2), ('y', 2)),
                    (('g', 3), ('r', 3), ('y', 3)), (('r', 2), ('y', 1), ('g', 1)), (('y', 2), ('r', 3), ('g', 3)), (('y', 3), ('r', 3), ('g', 1)), 
                    (('r', 2), ('g', 3), ('y', 3)), (('y', 1), ('r', 2), ('g', 3)), (('g', 1), ('y', 2), ('r', 1)), (('g', 2), ('r', 3), ('y', 1)), 
                    (('g', 1), ('y', 2), ('r', 2)), (('r', 1), ('g', 3), ('y', 1)), (('g', 1), ('r', 1), ('y', 1)), (('r', 1), ('y', 1), ('g', 3)), 
                    (('y', 1), ('r', 3), ('g', 3)), (('g', 3), ('r', 1), ('y', 3)), (('y', 3), ('g', 1), ('r', 2)), (('y', 2), ('r', 1), ('g', 3)), 
                    (('r', 2), ('g', 2), ('y', 2)), (('g', 1), ('r', 3), ('y', 3)), (('y', 3), ('g', 2), ('r', 1)), (('y', 3), ('g', 3), ('r', 2)), 
                    (('r', 3), ('g', 1), ('y', 1)), (('r', 1), ('y', 2), ('g', 3)), (('y', 1), ('g', 3), ('r', 3)), (('g', 3), ('r', 3), ('y', 2)), 
                    (('r', 3), ('g', 3), ('y', 1)), (('r', 3), ('y', 1), ('g', 2)), (('g', 2), ('y', 1), ('r', 3)), (('y', 2), ('r', 2), ('g', 2)), 
                    (('r', 2), ('g', 3), ('y', 2)), (('r', 3), ('y', 3), ('g', 2)), (('g', 2), ('y', 3), ('r', 3)), (('y', 1), ('r', 1), ('g', 3)), 
                    (('g', 1), ('r', 2), ('y', 1)), (('g', 2), ('r', 1), ('y', 1)), (('g', 3), ('y', 2), ('r', 2)), (('y', 3), ('r', 1), ('g', 3)), 
                    (('r', 2), ('g', 1), ('y', 3)), (('g', 3), ('r', 2), ('y', 3)), (('r', 3), ('y', 2), ('g', 3)), (('r', 1), ('y', 3), ('g', 1)), 
                    (('y', 1), ('r', 2), ('g', 2)), (('g', 3), ('r', 1), ('y', 2)), (('y', 2), ('g', 1), ('r', 3)), (('r', 3), ('g', 2), ('y', 3)), 
                    (('r', 1), ('g', 1), ('y', 1)), (('g', 1), ('r', 3), ('y', 2)), (('y', 2), ('g', 3), ('r', 3)), (('y', 2), ('g', 2), ('r', 3)), 
                    (('r', 1), ('y', 1), ('g', 2)), (('r', 1), ('g', 2), ('y', 1)), (('y', 1), ('r', 3), ('g', 2)), (('r', 3), ('y', 1), ('g', 1)), 
                    (('y', 2), ('r', 2), ('g', 1)), (('y', 2), ('r', 1), ('g', 2)), (('r', 2), ('g', 2), ('y', 1)), (('r', 3), ('y', 3), ('g', 1)), 
                    (('y', 3), ('r', 2), ('g', 3)), (('y', 1), ('g', 1), ('r', 3)), (('y', 1), ('g', 3), ('r', 1)), (('g', 2), ('y', 1), ('r', 1)), 
                    (('r', 1), ('y', 3), ('g', 2)), (('y', 1), ('g', 2), ('r', 3)), (('r', 2), ('g', 1), ('y', 2)), (('g', 2), ('y', 1), ('r', 2)), 
                    (('g', 3), ('r', 2), ('y', 2)), (('y', 2), ('r', 3), ('g', 1)), (('g', 2), ('y', 3), ('r', 1)), (('r', 2), ('y', 1), ('g', 3)), 
                    (('y', 1), ('r', 2), ('g', 1)), (('y', 3), ('g', 2), ('r', 2)), (('y', 1), ('r', 1), ('g', 2)), (('r', 3), ('g', 2), ('y', 2)), 
                    (('g', 2), ('r', 2), ('y', 3)), (('r', 2), ('y', 2), ('g', 3)), (('r', 1), ('y', 1), ('g', 1)), (('r', 3), ('y', 2), ('g', 2)), 
                    (('g', 2), ('y', 2), ('r', 3)), (('y', 2), ('g', 1), ('r', 1)), (('y', 1), ('r', 3), ('g', 1)), (('g', 3), ('r', 1), ('y', 1)), 
                    (('r', 2), ('y', 3), ('g', 3)), (('y', 2), ('r', 1), ('g', 1)), (('y', 2), ('g', 3), ('r', 1)), (('y', 2), ('g', 2), ('r', 1)), 
                    (('g', 1), ('r', 3), ('y', 1)), (('g', 3), ('y', 3), ('r', 3)), (('y', 2), ('r', 3), ('g', 2)), (('r', 1), ('y', 2), ('g', 1)), 
                    (('g', 1), ('y', 1), ('r', 1)), (('r', 3), ('g', 1), ('y', 3)), (('g', 1), ('y', 3), ('r', 1)), (('y', 1), ('g', 1), ('r', 1)), 
                    (('r', 3), ('g', 3), ('y', 3)), (('y', 1), ('r', 1), ('g', 1)), (('y', 1), ('g', 2), ('r', 1)), (('y', 3), ('r', 1), ('g', 1)), 
                    (('g', 2), ('r', 2), ('y', 2)), (('r', 2), ('g', 1), ('y', 1)), (('g', 1), ('y', 1), ('r', 3)), (('r', 3), ('y', 2), ('g', 1)), 
                    (('g', 2), ('r', 1), ('y', 3)), (('r', 1), ('g', 3), ('y', 2)), (('g', 1), ('y', 3), ('r', 3)), (('r', 1), ('y', 2), ('g', 2)), 
                    (('y', 1), ('g', 3), ('r', 2)), (('g', 3), ('r', 3), ('y', 1)), (('g', 2), ('y', 2), ('r', 1)), (('r', 2), ('y', 2), ('g', 2)), 
                    (('r', 1), ('g', 1), ('y', 3)), (('r', 2), ('g', 3), ('y', 1)), (('g', 2), ('y', 3), ('r', 2)), (('y', 3), ('r', 3), ('g', 3)), 
                    (('r', 3), ('g', 1), ('y', 2)), (('r', 2), ('y', 3), ('g', 2)), (('g', 3), ('y', 1), ('r', 3)), (('g', 3), ('y', 3), ('r', 1)), 
                    (('y', 3), ('r', 1), ('g', 2)), (('r', 3), ('g', 3), ('y', 2)), (('g', 2), ('r', 3), ('y', 3)), (('r', 1), ('g', 3), ('y', 3)), 
                    (('g', 1), ('r', 1), ('y', 3)), (('y', 2), ('g', 1), ('r', 2)), (('g', 2), ('r', 1), ('y', 2)), (('g', 3), ('y', 2), ('r', 3)), 
                    (('y', 2), ('g', 3), ('r', 2)), (('y', 2), ('g', 2), ('r', 2)), (('g', 2), ('r', 2), ('y', 1)), (('r', 2), ('y', 2), ('g', 1)), 
                    (('g', 1), ('y', 1), ('r', 2)), (('r', 1), ('g', 1), ('y', 2)), (('y', 3), ('r', 2), ('g', 2)), (('g', 1), ('y', 3), ('r', 2)), 
                    (('y', 1), ('g', 1), ('r', 2)), (('r', 2), ('y', 3), ('g', 1)), (('r', 1), ('g', 2), ('y', 2)), (('y', 3), ('g', 1), ('r', 1)), 
                    (('y', 1), ('g', 2), ('r', 2)), (('g', 1), ('r', 2), ('y', 3)), (('g', 3), ('r', 2), ('y', 1)), (('y', 3), ('g', 3), ('r', 1)), 
                    (('g', 2), ('r', 3), ('y', 2)), (('g', 1), ('y', 2), ('r', 3)), (('r', 2), ('y', 1), ('g', 2)), (('y', 3), ('r', 3), ('g', 2)), 
                    (('g', 1), ('r', 1), ('y', 2)), (('g', 3), ('y', 1), ('r', 1)), (('r', 3), ('g', 2), ('y', 1)), (('r', 1), ('y', 3), ('g', 3)), 
                    (('g', 3), ('y', 1), ('r', 2)), (('y', 3), ('g', 1), ('r', 3))}
        self.assertTrue(len(actual) == math.factorial(n)*3**(n), f"There should be {n}!*3^{n} possible dice roll sequences with {n} die.")
        self.assertEqual(actual, expected, "The full set of dice sequences should be generated.")
    
    def test_4(self):
        """get_all_roll_sequences- 4 dice colors"""
        n = 4
        dice_colors=['g','y','r','b']
        self.board.pyramid.remaining_dice=dice_colors
        actual = self.AI.get_all_roll_sequences()
        expected = [
            (('r', 1), ('g', 2), ('b', 2), ('y', 1)),
            (('y', 2), ('g', 3), ('r', 3), ('b', 1)),
            (('g', 3), ('b', 3), ('y', 1), ('r', 1)),
            (('b', 3), ('r', 2), ('g', 1), ('y', 1)),
            (('b', 1), ('y', 1), ('r', 2), ('g', 2))
        ]
        self.assertTrue(len(actual) == math.factorial(n)*3**(n), f"There should be {n}!*3^{n} possible dice roll sequences with {n} die.")
        for sequence in expected:
            self.assertIn(sequence, actual, f"full set of dice sequences should be generated.")
    
    def test_5(self):
        """get_all_roll_sequences- 5 dice colors"""
        n = 5
        dice_colors=['g','y','r','b', 'p']
        self.board.pyramid.remaining_dice=dice_colors
        actual = self.AI.get_all_roll_sequences()
        expected = [
            (('p', 3), ('r', 1), ('g', 2), ('b', 2), ('y', 1)),
            (('y', 2), ('g', 3), ('p', 2),  ('r', 3), ('b', 1)),
            (('g', 3), ('b', 3), ('y', 1), ('r', 1), ('p', 1)),
            (('b', 3), ('r', 2), ('g', 1), ('p', 3), ('y', 1)),
            (('b', 1), ('p', 2), ('y', 1), ('r', 2), ('g', 2))
        ]
        self.assertTrue(len(actual) == math.factorial(n)*3**(n), f"There should be {n}!*3^{n} possible dice roll sequences with {n} die.")
        for sequence in expected:
            self.assertIn(sequence, actual, f"full set of dice sequences should be generated.")
    
    def test_6(self):
        """get_all_roll_sequences- 0 dice"""
        n = 0
        dice_colors={}
        self.board.pyramid.remaining_dice=dice_colors
        actual = self.AI.get_all_roll_sequences()
        expected = set()
        self.assertTrue(len(actual) == 0, f"There should be no possible dice roll sequences with {n} die.")
        self.assertEqual(actual, expected, "The full set of dice sequences should be generated.")


if __name__ == "__main__":
    unittest.main()