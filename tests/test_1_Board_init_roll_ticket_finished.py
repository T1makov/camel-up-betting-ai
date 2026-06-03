import unittest
from colorama import Fore, Back, Style, init
import random
from copy import deepcopy
import os, sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.join(current_dir, '..')
sys.path.append(parent_dir)

Board = None
if not Board:
    from Board import Board as Board 

class Test_Board_init_roll_ticket_finished(unittest.TestCase):
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
    
    def test_Board_init(self):
        """Board- __init__"""
        self.assertIsInstance(self.board, object, "Board should be an object")
        self.assertIsInstance(self.board.TRACK_LENGTH, int, "Track length should be an integer")
        self.assertEqual(self.board.TRACK_LENGTH, 16, "Track length should be 16")
        self.assertIsInstance(self.board.STYLES, dict, "STYLES should be a dictionary")
        self.assertEqual(self.board.STYLES, self.camel_styles, "STYLES should match the camel_styles")
        self.assertIsInstance(self.board.track, list, "Track should be a list") 
        self.assertEqual(len(self.board.track), self.board.TRACK_LENGTH, f"Track should have {self.board.TRACK_LENGTH} positions")
        for camel in self.camel_styles:
            self.assertIn(camel, self.board.track[0], f"Camel {camel} should be in the first position of the track")
        self.assertIsInstance(self.board.pyramid, object, "Pyramid should be a Pyramid object")
        self.assertIsInstance(self.board.ticket_tents, dict, "Ticket tents should be a dictionary")
        self.assertEqual(len(self.board.ticket_tents), 5, "Ticket tents should have 5 colors")
        for color in self.board.ticket_tents:
            self.assertIn(color, self.camel_styles, f"Ticket tent color {color} should be in camel_styles")
            self.assertIsInstance(color, str, f"Ticket tent color {color} should be a string")         
            self.assertIsInstance(self.board.ticket_tents[color], list, f"Ticket tent for {color} should be a list")
            self.assertEqual(len(self.board.ticket_tents[color]), 4, f"Ticket tent for {color} should have 4 tickets")
            self.assertEqual(self.board.ticket_tents[color], [5, 3, 2, 2], f"Ticket tent for {color} should have tickets [5, 3, 2, 2]")
        self.assertIsInstance(self.board.dice_tents, list, "Dice tents should be a list")
        self.assertEqual(len(self.board.dice_tents), 0, "Dice tents should be empty")
    
    def test_Board_roll(self):
        """Board- roll_die"""
        for _ in range(5):
            rolled_die = self.board.roll_die()
            self.assertTrue(rolled_die[0] in self.board.pyramid.DIE_COLORS, f"Die should be one of {self.board.pyramid.DIE_COLORS}")
            self.assertTrue(rolled_die not in self.board.pyramid.remaining_dice, "Rolled die should be removed from remaining_dic in pyramid")
            self.assertIn(rolled_die, self.board.dice_tents, f"Rolled die {rolled_die} should be added to dice_tents {self.board.dice_tents}")
        self.assertTrue(len(self.board.pyramid.remaining_dice) == 0, "All dice should be removed from remaining_dice after rolling all dice")
        self.assertTrue(len(self.board.dice_tents) == 5, "All dice should be added to dice_tents after rolling all dice")
    
    def test_Board_take_ticket(self):
        """Board- take_ticket"""
        ticket_values= [5, 3, 2, 2]
        for color in self.board.ticket_tents:
            for i in range(5):
                ticket = self.board.take_ticket(color)
                if i < 4:
                    self.assertEqual(ticket[0], color, f"Ticket color should be {color} but got {ticket[0]}")
                    self.assertEqual(ticket[1], ticket_values[i], f"Ticket value should be {ticket_values[i]} but got {ticket[1]}")
                    self.assertEqual(len(self.board.ticket_tents[color]), 4-(i+1), f"Ticket tents for {color} should have {4-i} tickets left but got {len(self.board.ticket_tents[color])}")
                else:
                    self.assertEqual(ticket[0], color, f"Ticket color should be {color} but got {ticket[0]}")
                    self.assertEqual(ticket[1], 0, f"Ticket value should be {0} but got {ticket[1]}")
           
    def test_Board_is_finished_5_die(self):
        """Board- is_finished"""
        self.board.dice_tents=[('r', 3), ('b', 3), ('g', 1), ('y', 1), ('p', 2)]
        self.board.pyramid.remaining_dice = []
        self.assertTrue(self.board.is_leg_finished(), "Full dice_tents should result in board.is_leg_finished -> True ")
        for _ in range(5):
            removed_die = self.board.dice_tents.pop()
            self.board.pyramid.remaining_dice.append(removed_die)
            self.assertFalse(self.board.is_leg_finished(), f"DIce tents w/ length {len(self.board.dice_tents)} should result in board.is_leg_finished -> False ")
    

if __name__ == "__main__":
    unittest.main()