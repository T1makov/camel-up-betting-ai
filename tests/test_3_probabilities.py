import unittest
from colorama import Fore, Back, Style, init
import os, sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.join(current_dir, '..')
sys.path.append(parent_dir)

AI = None
if not AI:
    from AI import AI as AI 

Board = None
if not Board:
    from Board import Board as Board 

class Test_AI_probabilites(unittest.TestCase):
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
        """run_enumerative_leg_analysis, run_experimental_leg_analysis - Data Types"""
        actual = self.AI.run_enumerative_analysis()
        self.assertIsInstance(actual, dict, "run_enumerative_leg_analysis should return a dict")
        for key in actual.keys():
            self.assertIsInstance(key, str, "run_enumerative_leg_analysis should return a dict with str keys")
            value = actual[key]
            self.assertIsInstance(value, tuple, "run_enumerative_leg_analysis should return a dict with tuple values")
            self.assertTrue(len(value)==2, "run_enumerative_leg_analysis should return a dict with tuple values that have 2 elements")
            self.assertIsInstance(value[0], float, "run_enumerative_leg_analysis should return a dict with tuple values having first element float")
            self.assertIsInstance(value[1], float, "run_enumerative_leg_analysis should return a dict with tuple values having first element float")
        actual = self.AI.run_experimental_analysis(100)
        self.assertIsInstance(actual, dict, "run_experimental_leg_analysis should return a dict")
        for key in actual.keys():
            self.assertIsInstance(key, str, "run_experimental_leg_analysis should return a dict with str keys")
            value = actual[key]
            self.assertIsInstance(value, tuple, "run_experimental_leg_analysis should return a dict with tuple values")
            self.assertTrue(len(value)==2, "run_experimental_leg_analysis should return a dict with tuple values that have 2 elements")
            self.assertIsInstance(value[0], float, "run_experimental_leg_analysis should return a dict with tuple values having first element float")
            self.assertIsInstance(value[1], float, "run_experimental_leg_analysis should return a dict with tuple values having first element float")
    
    def test_1(self):
        """run_enumerative_analysis-- All 1st place probs add to ~1, all 2nd place probs add to ~1"""
        colors = list(self.board.STYLES.keys())
        for i in range(len(colors)):
            dice_colors = colors[i:]
            self.board.pyramid.remaining_dice = dice_colors
            enum_probs = self.AI.run_enumerative_analysis()
            sum1=0
            sum2=0
            for color, probs in enum_probs.items():
                sum1+=probs[0]
                sum2+=probs[1]
            self.assertTrue(abs(1-sum1) <= 0.1, "The sum of all first place probabilites should be approximately 1")
            self.assertTrue(abs(1-sum2) <= 0.1, "The sum of all first place probabilites should be approximately 1")
    
    def test_2(self):
        """run_enumerative_analysis-- clear 1st, 2nd, 1 roll left"""
        track = [[] for i in range(self.board.TRACK_LENGTH)]
        track[1]= ['g']
        track[2]= ['p','b','y','r']
        self.board.track = track
        self.board.pyramid.remaining_dice = {'b'}
        self.dice_tents =[('g',1), ('r', 1), ('p',1), ('y', 1)]
        print("Track:", self.board.track)
        print("Dice left to roll:", self.board.pyramid.remaining_dice)
        actual = self.AI.run_enumerative_analysis()
        expected={
            'r':(1.0,0.0),
            'g':(0.0,0.0),
            'b':(0.0,0.0),
            'y':(0.0,1.0),
            'p':(0.0,0.0)
        }
        
        self.assertEqual(actual, expected, f"Actual probablities: {actual} Expected probabilites: {expected}")

    def test_3(self):
        """run_enumerative_analysis-- all stacked, 4 rolls left"""
        track = [[] for i in range(self.board.TRACK_LENGTH)]
        track[2]= ['p','g','b','y','r']
        self.board.track = track
        self.board.pyramid.remaining_dice = {'b', 'y', 'g', 'r'}
        self.dice_tents =[('p',2)]
        print("Track:", self.board.track)
        print("Dice left to roll:", self.board.pyramid.remaining_dice)
        actual = self.AI.run_enumerative_analysis()
        expected={
            'r':(0.39,0.27),
            'b':(0.22,0.23),
            'g':(0.11,0.16),
            'y':(0.28,0.33),
            'p':(0.0,0.0)
        }
        for key in actual.keys():
            self.assertTrue(abs(actual[key][0] - expected[key][0])<=0.1, f"Actual probablities: {actual} Expected probabilites: {expected}")
            self.assertTrue(abs(actual[key][1] - expected[key][1])<=0.1, f"Actual probablities: {actual} Expected probabilites: {expected}")
    
    def test_4(self):
        """run_enumerative_analysis-- camels in mixed positions, 3 rolls left"""
        track = [[] for i in range(self.board.TRACK_LENGTH)]
        track[1]= ['b','g','r']
        track[3]=['p']
        track[5]=['y']
        self.board.track = track
        self.board.pyramid.remaining_dice = {'b', 'g', 'r'}
        self.dice_tents =[('p',2), ('y', 2)]
        print("Track:", self.board.track)
        print("Dice left to roll:", self.board.pyramid.remaining_dice)
        actual = self.AI.run_enumerative_analysis()
        expected={
            'r':(0.40,0.21),
            'b':(0.04,0.13),
            'g':(0.20,0.26),
            'y':(0.37,0.40),
            'p':(0.0,0.01)
        }
        for key in actual.keys():
            self.assertTrue(abs(actual[key][0] - expected[key][0])<=0.1, f"Actual probablities: {actual} Expected probabilites: {expected}")
            self.assertTrue(abs(actual[key][1] - expected[key][1])<=0.1, f"Actual probablities: {actual} Expected probabilites: {expected}")

    def test_5(self):
        """run_experimental_analysis-- All 1st place probs add to 1, all 2nd place probs add to 1"""
        colors = list(self.board.STYLES.keys())
        for i in range(len(colors)):
            dice_colors = colors[i:]
            self.board.pyramid.remaining_dice = dice_colors
            enum_probs = self.AI.run_experimental_analysis(1000)
            sum1=0
            sum2=0
            for color, probs in enum_probs.items():
                sum1+=probs[0]
                sum2+=probs[1]
            self.assertTrue(abs(1-sum1) <= 0.15, "The sum of all first place probabilites should be approximately 1")
            self.assertTrue(abs(1-sum2) <= 0.15, "The sum of all first place probabilites should be approximately 1")
    
    def test_6(self):
        """run_experimental_analysis-- clear 1st, 2nd, 1 roll left"""
        track = [[] for i in range(self.board.TRACK_LENGTH)]
        track[1]= ['g']
        track[2]= ['p','b','y','r']
        self.board.track = track
        self.board.pyramid.remaining_dice = ['y']
        self.dice_tents =[('g',1), ('r', 1), ('p',1), ('b', 1)]
        print("Track:", self.board.track)
        print("Dice left to roll:", self.board.pyramid.remaining_dice)
        actual = self.AI.run_enumerative_analysis()
        expected={
            'r':(1.0,0.0),
            'g':(0.0,0.0),
            'b':(0.0,0.0),
            'y':(0.0,1.0),
            'p':(0.0,0.0)
        }
        
        self.assertEqual(actual, expected, f"Expected probabilites: {expected}")
   

    def test_7(self):
        """run_experimental_analysis-- all stacked, 4 rolls left"""
        track = [[] for i in range(self.board.TRACK_LENGTH)]
        track[2]= ['p','g','b','y','r']
        self.board.track = track
        self.board.pyramid.remaining_dice = ['b', 'y', 'g', 'r']
        self.dice_tents =[('p',2)]
        print("Track:", self.board.track)
        print("Dice left to roll:", self.board.pyramid.remaining_dice)
        actual = self.AI.run_experimental_analysis(1000)
        expected={
            'r':(0.39,0.27),
            'b':(0.22,0.23),
            'g':(0.11,0.16),
            'y':(0.28,0.33),
            'p':(0.0,0.0)
        }
        for key in actual.keys():
            self.assertTrue(abs(actual[key][0] - expected[key][0])<=0.1, f"Actual probablities: {actual} Expected probabilites: {expected}")
            self.assertTrue(abs(actual[key][1] - expected[key][1])<=0.1, f"Actual probablities: {actual} Expected probabilites: {expected}")
    

    def test_8(self):
        """run_experimental_analysis-- camels in mixed positions, 1, 2, 3, 4, 5 rolls left"""
        track = [[] for i in range(self.board.TRACK_LENGTH)]
        track[1]= ['b','g','r']
        track[3]=['p']
        track[5]=['y']
        self.board.track = track
        self.board.pyramid.remaining_dice = ['b', 'g', 'r']
        self.dice_tents =[('p',2), ('y', 2)]
        print("Track:", self.board.track)
        print("Dice left to roll:", self.board.pyramid.remaining_dice)
        actual = self.AI.run_experimental_analysis(1000)
        expected={
            'r':(0.40,0.21),
            'b':(0.04,0.13),
            'g':(0.20,0.26),
            'y':(0.37,0.40),
            'p':(0.0,0.01)
        }
        for key in actual.keys():
            self.assertTrue(abs(actual[key][0] - expected[key][0])<=0.1, f"Actual probablities: {actual} Expected probabilites: {expected}")
            self.assertTrue(abs(actual[key][1] - expected[key][1])<=0.1, f"Actual probablities: {actual} Expected probabilites: {expected}")
   


if __name__ == "__main__":
    unittest.main()