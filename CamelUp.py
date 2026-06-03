from colorama import Back, Style

try:
    from Board import Board
except ModuleNotFoundError:
    print("Board.py is not found.")
    pass
try:
    from Player import Player
except ModuleNotFoundError:
    print("Player.py is not found.")
    pass
try:
    from AI import AI
except ModuleNotFoundError:
    print("AI.py is not found.")
    pass

class CamelUp:
    def __init__(self, camel_styles:dict[str, str], player_list:list[Player]):
        self.STYLES = camel_styles
        self.board = Board(self.STYLES)
        self.ai = AI(self.board)
        self.players = player_list


    def get_player_move(self, player:Player):
        print(f"{player.name}-", end =" ")
        choice = "not_an_option"
        while choice.lower() not in ["b", "r", "a"]:
            choice = input("(B)et or (R)oll or (A)dvice? ").lower()
        return choice

    def get_player_bet(self):
        available_tickets="Available bets: "
        for color in self.board.ticket_tents:
            tickets_left = self.board.ticket_tents[color]
            if len(tickets_left) > 0:
                top_ticket_value=tickets_left[0]
                available_tickets += f"({color})"+self.STYLES[color]+str(top_ticket_value)+Style.RESET_ALL+" "
            else:
                available_tickets += f"({color})"+self.STYLES[color]+"X"+Style.RESET_ALL+" "
        print(available_tickets)

        ticket_color = "not_an_option"
        while ticket_color.lower() not in self.STYLES.keys() or len(self.board.ticket_tents[ticket_color])<=0:
            ticket_color = input("Which betting ticket would you like to take?\n").lower()

        return ticket_color.lower()

    def roll_for_player(self, player:Player):
        """Roll a die, move the matching camel, and give the player 1 coin.

        Returns:
            tuple[str, int]: the die that was rolled.
        """
        rolled_die = self.board.roll_die()

        if rolled_die == ("", 0):
            print("There are no dice left to roll.")
            return rolled_die

        self.board.move_camel(rolled_die)
        player.update_money(1)
        print(f"{player.name} rolled {self.STYLES[rolled_die[0]]}{rolled_die[0]}{Style.RESET_ALL} for {rolled_die[1]} and earned 1 coin.")
        return rolled_die

    def take_bet_for_player(self, player:Player, ticket_color:str):
        """Take the top betting ticket for a camel and add it to the player's bets.

        Returns:
            tuple[str, int]: the ticket that was taken.
        """
        ticket = self.board.take_ticket(ticket_color)

        if ticket[1] == 0:
            print(f"No {ticket_color} tickets are left.")
            return ticket

        player.add_bet(ticket)
        print(f"{player.name} took a {self.STYLES[ticket[0]]}{ticket[0]}{Style.RESET_ALL} ticket worth {ticket[1]}.")
        return ticket

    def play_leg(self):
        curr_player = 0

        while not self.board.is_leg_finished():
            player = self.players[curr_player]
            turn_finished = False

            while not turn_finished:
                move = self.get_player_move(player)

                match move:
                    case "r":
                        self.roll_for_player(player)
                        turn_finished = True

                    case "b":
                        ticket_color = self.get_player_bet()
                        self.take_bet_for_player(player, ticket_color)
                        turn_finished = True

                    case "a":
                        print(self.ai)

            print(self)
            curr_player = (curr_player + 1) % len(self.players)

    def process_leg_payouts(self):
        """Process payouts for the end of a leg.

        First-place bets earn the ticket value, second-place bets earn 1 coin,
        and all other bets lose 1 coin. After payouts, each player's betting
        tickets are cleared for the next leg.

        Returns:
            tuple[str, str]: a tuple of the form (first, second).
        """
        rankings = self.board.get_rankings()

        for player in self.players:
            for bet in player.bets:
                if bet[0] == rankings[0]:
                    player.update_money(bet[1])
                elif bet[0] == rankings[1]:
                    player.update_money(1)
                else:
                    player.update_money(-1)

            player.reset_leg()

        return rankings
    
    def __str__(self):
        game_str = str(self.board)
        for player in self.players:
            game_str += str(player)+"\n"
        return game_str

if __name__ == "__main__":
    STYLES= {
            "r": Back.RED+Style.BRIGHT,
            "b": Back.BLUE+Style.BRIGHT,
            "g": Back.GREEN+Style.BRIGHT,
            "y": Back.YELLOW+Style.BRIGHT,
            "p": Back.MAGENTA
    }
    player1 = Player("Dave", STYLES)
    player2 = Player("Sasha", STYLES)
    game = CamelUp(STYLES, [player1, player2])
    print(game)
    game.play_leg()
    first, second = game.process_leg_payouts()

    print(f"{game.STYLES[first]}{first}{Style.RESET_ALL} comes in 1st🥇🥇🥇!")
    print(f"{game.STYLES[second]}{second}{Style.RESET_ALL} comes in 2nd🥈🥈🥈!")

    for player in game.players:
        print(f"{player.name} ended the leg with {player.money} coins.")

    game.board.reset_leg()
