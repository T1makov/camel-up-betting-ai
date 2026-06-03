import unittest
from colorama import Fore, Back, Style, init
import os, sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.join(current_dir, '..')
sys.path.append(parent_dir)

Player = None
if not Player:
    from Player import Player as Player 

class Test_Player(unittest.TestCase):
    def setUp(self):
        """runs before each test"""
        self.camel_styles= {
            "r": Back.RED+Style.BRIGHT,
            "b": Back.BLUE+Style.BRIGHT,
            "g": Back.GREEN+Style.BRIGHT,
            "y": Back.YELLOW+Style.BRIGHT,
            "p": Back.MAGENTA
        }
        self.player = Player("Dave", self.camel_styles)
    
    def test_player_data_attributes(self):
        """Player- Data Types"""
        self.assertIsInstance(self.player.money, int, "Player.money should return an int")
        self.assertEqual(self.player.money, 3, "Player.money should start at 3")
        self.assertIsInstance(self.player.bets, list, "Player.bets should return a list")
        self.assertIsInstance(self.player.name, str, "Player.name should return a str")
        self.assertIsInstance(self.player.STYLES, dict, "Player.STYLES should return a dict")
        self.assertEqual(self.player.STYLES, self.camel_styles, "Player.STYLES should be a dict of the camel styles")
    
    def test_player_update_money(self):
        """Player- update_money"""
        self.player.update_money(2)
        self.assertEqual(self.player.money, 5, "update_money should increase Player.money by the given amount")
        self.player.update_money(-1)
        self.assertEqual(self.player.money, 4, "update_money should decrease Player.money by the given amount") 
    
    def test_player_add_bet(self):
        """Player- add_bet"""
        self.player.add_bet(('y', 5))
        self.assertEqual(self.player.bets, [('y', 5)], "add_bet should add a betting ticket to Player.bets")
        self.player.add_bet(('b', 3))
        self.assertEqual(self.player.bets, [('y', 5), ('b', 3)], "add_bet should add a betting ticket to Player.bets")
    
    def test_player_reset_leg(self):
        """Player- reset_leg"""
        self.player.add_bet(('y', 5))
        self.player.add_bet(('b', 3))
        self.player.reset_leg()
        self.assertEqual(self.player.bets, [], "reset_leg should reset Player.bets to an empty list")

if __name__ == "__main__":
    unittest.main()