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


class Test_AI_ticket_EV(unittest.TestCase):
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
    
    def test_ticket_EV_data_attributes(self):
        actual = self.AI.get_ticket_EV(5, .5, .5)
        self.assertIsInstance(actual, float, "get_ticket_EV should return a float value")

    def test_1(self):
        """get_ticket_EV - Both 0% """
        ticket_value = 5
        p1 = 0
        p2 = 0
        actual = self.AI.get_ticket_EV(ticket_value, p1, p2)
        expected = -1
        self.assertEqual(actual, expected, f"For a ticket value: {ticket_value} with prob 1st:{p1} and prob 2nd:{p2}, get_ticket_EV should return {expected}")

    def test_2(self):
        """get_ticket_EV - 100%, 0%"""
        ticket_value = 3
        p1 = 1
        p2 = 0
        actual = self.AI.get_ticket_EV(ticket_value, p1, p2)
        expected = 3
        self.assertEqual(actual, expected, f"For a ticket value: {ticket_value} with prob 1st:{p1} and prob 2nd:{p2}, get_ticket_EV should return {expected}")

    def test_3(self):
        """get_ticket_EV - 0%, 100%"""
        ticket_value = 2
        p1 = 0
        p2 = 1
        actual = self.AI.get_ticket_EV(ticket_value, p1, p2)
        expected = 1
        self.assertEqual(actual, expected, f"For a ticket value: {ticket_value} with prob 1st:{p1} and prob 2nd:{p2}, get_ticket_EV should return {expected}")
 
    def test_4(self):
        """get_ticket_EV - 50%, 50%"""
        ticket_value = 5
        p1 = .5
        p2 = .5
        actual = self.AI.get_ticket_EV(ticket_value, p1, p2)
        expected = 3
        self.assertEqual(actual, expected, f"For a ticket value: {ticket_value} with prob 1st:{p1} and prob 2nd:{p2}, get_ticket_EV should return {expected}")

    def test_5(self):
        """get_ticket_EV - 33%, 67%"""
        ticket_value = 3
        p1 = .33
        p2 = .67
        actual = self.AI.get_ticket_EV(ticket_value, p1, p2)
        expected = 1.66
        self.assertTrue(abs(actual-expected)<.02, f"For a ticket value: {ticket_value} with prob 1st:{p1} and prob 2nd:{p2}, get_ticket_EV should return {expected}")

    def test_6(self):
        """get_ticket_EV - 67%, 33%"""
        ticket_value = 3
        p1 = .67
        p2 = .33
        actual = self.AI.get_ticket_EV(ticket_value, p1, p2)
        expected = 2.34
        self.assertTrue(abs(actual-expected)<.02, f"For a ticket value: {ticket_value} with prob 1st:{p1} and prob 2nd:{p2}, get_ticket_EV should return {expected}")
    
    def test_7(self):
        """get_ticket_EV - 0%, 17%"""
        ticket_value = 5
        p1 = 0
        p2 = .17
        actual = self.AI.get_ticket_EV(ticket_value, p1, p2)
        expected = -0.66
        self.assertTrue(abs(actual-expected)<.01, f"For a ticket value: {ticket_value} with prob 1st:{p1} and prob 2nd:{p2}, get_ticket_EV should return {expected}")
    
    def test_8(self):
        """get_ticket_EV - 23%, 0%"""
        ticket_value = 2
        p1 = .23
        p2 = 0
        actual = self.AI.get_ticket_EV(ticket_value, p1, p2)
        expected = -0.31
        self.assertTrue(abs(actual-expected)<.02, f"For a ticket value: {ticket_value} with prob 1st:{p1} and prob 2nd:{p2}, get_ticket_EV should return {expected}")

if __name__ == "__main__":
    unittest.main()