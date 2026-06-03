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

class Test_Board_rankings_reset(unittest.TestCase):
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

    def test_Board_rankings_data_types(self):
        """Board- get_rankings data types"""
        actual = self.board.get_rankings()
        self.assertIsInstance(actual, tuple, "get_rankings should return a tuple")
        self.assertTrue(len(actual)==2, "get_rankings should return a tuple of length 2")
        self.assertIsInstance(actual[0], str, "get_rankings should return a tuple with first element str")
        self.assertIsInstance(actual[1], str, "get_rankings should return a tuple with second element str")
    
    def test_Board_rankings_solo_1st_solo_2nd(self):
        """Board- get_rankings solo 1st, solo 2nd"""
        track = [[] for i in range(self.board.TRACK_LENGTH)]
        camels = list(self.board.STYLES.keys())
        random.shuffle(camels)
        first = camels[3]
        second = camels[2]
        track[12]= [first]
        track[10]= [second]
        track[9] = camels[:2]
        track[7] = [camels[4]]
        self.board.track = track
        
        rankings = self.board.get_rankings()
        self.assertEqual(rankings[0], first, "The top camel should come in first when all camels are stacked on the same track position")
        self.assertEqual(rankings[1], second, "The second-from-the-top camel should come in second when all camels are stacked on the same track position")

    def test_Board_rankings_solo_1st_stacked_2nd(self):
        """Board- get_rankings - solo 1st, stacked 2nd"""
        track = [[] for i in range(self.board.TRACK_LENGTH)]
        camels = list(self.board.STYLES.keys())
        random.shuffle(camels)
        first = camels[3]
        second = camels[2]
        track[9]= [first]
        track[8] = camels[:3]
        track[3] = [camels[4]]
        self.board.track = track
        
        rankings = self.board.get_rankings()
        self.assertEqual(rankings[0], first, "The top camel should come in first when all camels are stacked on the same track position")
        self.assertEqual(rankings[1], second, "The second-from-the-top camel should come in second when all camels are stacked on the same track position")

    def test_Board_rankings_stacked_1st_2nd(self):
        """Board- get_rankings - stacked 1st, 2nd"""
        track = [[] for i in range(self.board.TRACK_LENGTH)]
        camels = list(self.board.STYLES.keys())
        random.shuffle(camels)
        first = camels[3]
        second = camels[2]
        track[5]= camels[2:4]
        track[4] = camels[0:2] + [camels[4]]
        
        self.board.track = track
        
        rankings = self.board.get_rankings()
        self.assertEqual(rankings[0], first, "The top camel should come in first when all camels are stacked on the same track position")
        self.assertEqual(rankings[1], second, "The second-from-the-top camel should come in second when all camels are stacked on the same track position")

    def test_Board_rankings_all_stacked_camels(self):
        """Board- get_rankings - all stacked camels"""
        for spot in [1,2,3,4,5,6,7,8,9]:
            self.board.track= [[] for i in range(self.board.TRACK_LENGTH)]
            self.board.track[spot]=list(self.board.STYLES.keys())
            random.shuffle(self.board.track[spot]) 
            first = self.board.track[spot][4]
            second = self.board.track[spot][3]
            rankings = self.board.get_rankings()
            self.assertEqual(rankings[0], first, "The top camel should come in first when all camels are stacked on the same track position")
            self.assertEqual(rankings[1], second, "The second-from-the-top camel should come in second when all camels are stacked on the same track position")

    def test_Board_reset_leg(self):
        """Board- reset_leg"""
        self.board.ticket_tents['r'] = [2,2]
        self.board.ticket_tents['b'] = [3, 2, 2]
        self.board.dice_tents = [('r', 1), ('b', 2), ('g', 3), ('y', 1), ('p', 2)]
        self.board.pyramid.remaining_dice = []

        self.board.reset_leg()
        for die in self.board.STYLES.keys():
            self.assertEqual(self.board.ticket_tents[die], [5, 3, 2, 2], "reset_leg should reset the ticket tents to their original values")
        self.assertEqual(self.board.dice_tents, [], "reset_leg should empty the dice tents")
        self.assertEqual(self.board.pyramid.remaining_dice, list(self.board.STYLES.keys()), "reset_leg should reset the pyramid")

if __name__ == "__main__":
    unittest.main()
        