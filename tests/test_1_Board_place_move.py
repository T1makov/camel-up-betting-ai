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

class Test_Board_place_move_camel(unittest.TestCase):
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

    def test_Board_place_camels(self):
        """Board - place_camels"""
        top_counts = {"r":0, "b":0, "g":0, "y":0, "p":0}
        bottom_counts = {"r":0, "b":0, "g":0, "y":0, "p":0}
        for _ in range(200):
            self.board.place_camels()

            self.assertEqual(len(self.board.track[0]), 5, "All camels should be placed at the start of the game.")
            self.assertEqual(self.board.track[1:], [[] for i in range(1, self.board.TRACK_LENGTH)], "No camels should be placed beyond the starting position.")
            camels = []
            for stack in self.board.track:
                for camel in stack:
                    camels.append(camel)
            
            top_counts[self.board.track[0][4]] += 1
            bottom_counts[self.board.track[0][0]] += 1
              
            self.assertEqual(sorted(camels), sorted(list(self.camel_styles.keys())), "All camels should be present on the track after being placed.")
            self.board.track = [[] for i in range(self.board.TRACK_LENGTH)] #reset for next time
        for color in self.camel_styles.keys():
            self.assertGreater(top_counts[color], 0, "All camels should appear on the top of the starting stack at some point.")
            self.assertGreater(bottom_counts[color], 0, "All camels should appear on the bottom of the starting stack at some point.")

    def test_Board_move_camel_1(self):
        """Board - move_camel  solo camel into empty spot"""
        track = [[] for i in range(self.board.TRACK_LENGTH)]
        camels = list(self.board.STYLES.keys())
        track[0]= camels[0:4]
        original_spot=1
        camel_color_to_move = camels[4]
        track[original_spot]= [camel_color_to_move]
        for movement in range(1, 4):
            self.board.track=deepcopy(track)
            die = (camel_color_to_move, movement)
            self.board.move_camel(die)
            self.assertEqual(self.board.track[0], camels[0:4], "camels that aren't affected by a die roll shouldn't move.")
            self.assertEqual(self.board.track[original_spot], [], "camels affected by a die roll should no longer occupy the original track position.")
            self.assertEqual(self.board.track[original_spot+movement], [camel_color_to_move], "camels affected by a die roll should move the expected amount.")

    def test_Board_move_camel_2(self):
        """Board - move_camel  top of camel stack into empty spot"""
        track = [[] for i in range(self.board.TRACK_LENGTH)]
        camels = list(self.board.STYLES.keys())
        original_spot=4
        track[original_spot] = camels  #all camels stacked on top of each other
        camel_color_to_move = camels[4]
        
        for movement in range(1, 4):
            self.board.track=deepcopy(track)
            die = (camel_color_to_move, movement)
            self.board.move_camel(die)
            self.assertEqual(self.board.track[original_spot], camels[0:4], "camels that aren't affected by a die roll shouldn't move.")
            self.assertFalse(camel_color_to_move in self.board.track[original_spot], "camels affected by a die roll should no longer occupy the original track position.")
            self.assertEqual(self.board.track[original_spot+movement], [camel_color_to_move], "camels affected by a die roll should move the expected amount.")

    def test_Board_move_camel_3(self):
        """Board - move_camel  bottom of camel stack into empty spot """
        track = [[] for i in range(self.board.TRACK_LENGTH)]
        camels = list(self.board.STYLES.keys())
        original_spot=2
        track[original_spot] = camels  #all camels stacked on top of each other
        camel_color_to_move = camels[0]
        for movement in range(1, 4):
            self.board.track=deepcopy(track)
            die = (camel_color_to_move, movement)
            self.board.move_camel(die)
            self.assertEqual(self.board.track[original_spot], [], "All camels should move when the came is on the bottom of the stack.")
            self.assertFalse(camel_color_to_move in self.board.track[original_spot], "camels affected by a die roll should no longer occupy the original track position.")
            self.assertEqual(self.board.track[original_spot+movement], camels, "camels affected by a die roll should move the expected amount.")

    def test_Board_move_camel_4(self):
        """Board - move_camel  middle of camel stack empty spot"""
        track = [[] for i in range(self.board.TRACK_LENGTH)]
        camels = list(self.board.STYLES.keys())
        original_spot=3
        track[original_spot] = camels  #all camels stacked on top of each other
        camel_color_to_move = camels[2]
        for movement in range(1, 4):
            self.board.track=deepcopy(track)
            die = (camel_color_to_move, movement)
            self.board.move_camel(die)
            self.assertEqual(self.board.track[original_spot], camels[:2], "Only top camels should move when the came is on the bottom of the stack.")
            self.assertFalse(camel_color_to_move in self.board.track[original_spot], "camels affected by a die roll should no longer occupy the original track position.")
            self.assertEqual(self.board.track[original_spot+movement], camels[2:], "camels affected by a die roll should move the expected amount.")
   
    def test_Board_move_camel_5(self):
        """Board - move_camel  solo camel into occupied spot"""
        track = [[] for i in range(self.board.TRACK_LENGTH)]
        camels = list(self.board.STYLES.keys())

        movement=2
        original_spot=4
        track[original_spot-1] = camels[:3]
        track[original_spot] = [camels[3]] 
        track[original_spot+movement] = [camels[4]]
        camel_color_to_move = camels[3]
 
        self.board.track=deepcopy(track)
        die = (camel_color_to_move, movement)
        self.board.move_camel(die)
        self.assertEqual(self.board.track[original_spot-1], camels[:3], "camels that aren't affected by a die roll shouldn't move.")
        self.assertFalse(camel_color_to_move in self.board.track[original_spot], "camels affected by a die roll should no longer occupy the original track position.")
        self.assertTrue(camel_color_to_move in self.board.track[original_spot+movement], "camels affected by a die roll should be present ion the intended track position.")
        self.assertEqual(self.board.track[original_spot+movement], [camels[4]] + [camels[3]], "camels affected by a die roll lang on top of existing camels in a track position.")

    def test_Board_move_camel_6(self):
        """Board - move_camel  top of camel stack into occupied spot"""
        track = [[] for i in range(self.board.TRACK_LENGTH)]
        camels = list(self.board.STYLES.keys())

        movement=3
        original_spot=9
        track[original_spot] = camels[:4]  #four camels stacked on top of each other
        track[original_spot+movement] = [camels[4]]
        camel_color_to_move = camels[3]
 
        self.board.track=deepcopy(track)
        die = (camel_color_to_move, movement)
        self.board.move_camel(die)
        self.assertEqual(self.board.track[original_spot], camels[:3], "camels that aren't affected by a die roll shouldn't move.")
        self.assertFalse(camel_color_to_move in self.board.track[original_spot], "camels affected by a die roll should no longer occupy the original track position.")
        self.assertTrue(camel_color_to_move in self.board.track[original_spot+movement], "camels affected by a die roll should be present ion the intended track position.")
        self.assertEqual(self.board.track[original_spot+movement], [camels[4]] + [camels[3]], "camels affected by a die roll lang on top of existing camels in a track position.")

    def test_Board_move_camel_6(self):
        """Board - move_camel  bottom of camel stack into occupied spot """
        track = [[] for i in range(self.board.TRACK_LENGTH)]
        camels = list(self.board.STYLES.keys())

        movement=1
        original_spot=5
        track[original_spot] = camels[:4]  #four camels stacked on top of each other
        track[original_spot+movement] = [camels[4]]
        camel_color_to_move = camels[0]
     
        self.board.track=deepcopy(track)
        die = (camel_color_to_move, movement)
        self.board.move_camel(die)
        self.assertEqual(self.board.track[original_spot], [], "All camels move when the bottom camel moves.")
        self.assertFalse(camel_color_to_move in self.board.track[original_spot], "camels affected by a die roll should no longer occupy the original track position.")
        self.assertTrue(camel_color_to_move in self.board.track[original_spot+movement], "camels affected by a die roll should be present ion the intended track position.")
        self.assertEqual(self.board.track[original_spot+movement], [camels[4]] + camels[:4], "camels affected by a die roll lang on top of existing camels in a track position.")

    def test_Board_move_camel_7(self):
        """Board - move_camel  middle of camel stack inot occupied spot"""
        track = [[] for i in range(self.board.TRACK_LENGTH)]
        camels = list(self.board.STYLES.keys())

        movement=3
        original_spot=4
        track[original_spot] = camels[:4]  #four camels stacked on top of each other
        track[original_spot+movement] = [camels[4]]
        camel_color_to_move = camels[1]
 
        self.board.track=deepcopy(track)
        die = (camel_color_to_move, movement)
        self.board.move_camel(die)
        self.assertEqual(self.board.track[original_spot], [camels[0]], "camels that aren't affected by a die roll shouldn't move.")
        self.assertFalse(camel_color_to_move in self.board.track[original_spot], "camels affected by a die roll should no longer occupy the original track position.")
        self.assertTrue(camel_color_to_move in self.board.track[original_spot+movement], "camels affected by a die roll should be present ion the intended track position.")
        self.assertEqual(self.board.track[original_spot+movement], [camels[4]] + camels[1:4], "camels affected by a die roll lang on top of existing camels in a track position.")


if __name__ == "__main__":
    unittest.main()
        