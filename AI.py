from colorama import Back, Style
import copy
from itertools import permutations, product
import math
from random import choice
try:
    from Board import Board
except ModuleNotFoundError:
    print("Board.py is not found.")
    pass

class AI:
    def __init__(self, board:Board):
        self.STYLES = board.STYLES
        self.board = board #reference to actual game board... updates as game is played

    def get_all_roll_sequences(self) -> set[tuple[tuple[str, int]]]:
        '''
            Constructs a set of all possible roll sequences for the dice currently in the pyramid
            Note: Use itertools product function

            Return
                A set of tuples representing all the ordered dice seqences that could result from shaking all dice from the pyramid
        '''
        if self.board.pyramid.remaining_dice: ## check to make sure that we return an empty set of there is no remaining dice
            answer = set()
            permutations_of_camels = permutations(self.board.pyramid.remaining_dice) ##permutations of remaining dice
            permutations_of_dice = list(product([1, 2, 3], repeat = len(self.board.pyramid.remaining_dice))) ##all possible rolls
            for perm in permutations_of_camels: ##run through all of the remaining dice
                appended_list = [] ##this list will contain a sequence that I'm going to append the answer set by
                for dice in permutations_of_dice: ##run through all of the possible roll sequences
                    for i in range(len(self.board.pyramid.remaining_dice)): ##make the tuples
                            appended_list.append((perm[i], dice[i]))
                    answer.add(tuple(appended_list))
                    appended_list = []
            return answer
        else:
            return set()

    def run_enumerative_analysis(self) -> dict[str, tuple[float, float]]:
        if len(self.board.pyramid.remaining_dice) == 0:
            first, second = self.board.get_rankings()
            result = {color: (0.0, 0.0) for color in self.STYLES.keys()}
            result[first] = (1.0, 0.0)
            result[second] = (0.0, 1.0)
            return result
        answer_list = {'r':[0, 0], 'b':[0, 0], 'g':[0, 0], 'y':[0, 0], 'p':[0, 0]}
        answer_tuple = {}

        initial_track_copy = copy.deepcopy(self.board.track)

        try:
            for movement in self.get_all_roll_sequences():
                self.board.track = copy.deepcopy(initial_track_copy)

                for move in movement:
                    self.board.move_camel(move)

                winners = self.board.get_rankings()

                # increment the win counts
                answer_list[winners[0]][0] += 1
                answer_list[winners[1]][1] += 1

            num_left_dice = len(self.board.pyramid.remaining_dice)
            total_possibilities = math.factorial(num_left_dice) * (3 ** num_left_dice)

            for key in answer_list.keys():
                answer_tuple[key] = (
                    answer_list[key][0] / total_possibilities,
                    answer_list[key][1] / total_possibilities
                )

            return answer_tuple

        finally:
            self.board.track = initial_track_copy


    def run_experimental_analysis(self, trials:int) -> dict[str, tuple[float, float]]:
        if len(self.board.pyramid.remaining_dice) == 0:
            first, second = self.board.get_rankings()
            result = {color: (0.0, 0.0) for color in self.STYLES.keys()}
            result[first] = (1.0, 0.0)
            result[second] = (0.0, 1.0)
            return result
        answer_list_1 = {'r':[0, 0], 'b':[0, 0], 'g':[0, 0], 'y':[0, 0], 'p':[0, 0]}
        answer_tuple_1 = {}

        initial_track_copy = copy.deepcopy(self.board.track)
        roll_sequences = list(self.get_all_roll_sequences())

        if len(roll_sequences) == 0:
            return {color: (0, 0) for color in answer_list_1.keys()}

        try:
            for i in range(trials):
                self.board.track = copy.deepcopy(initial_track_copy)

                for move in choice(roll_sequences):
                    self.board.move_camel(move)

                winners = self.board.get_rankings()

                answer_list_1[winners[0]][0] += 1
                answer_list_1[winners[1]][1] += 1

            for key in answer_list_1.keys():
                answer_tuple_1[key] = (
                    round(answer_list_1[key][0] / trials, 2),
                    round(answer_list_1[key][1] / trials, 2)
                )

            return answer_tuple_1

        finally:
            self.board.track = initial_track_copy




    def get_ticket_EV(self, ticket_value:int, prob_first:float, prob_second:float)->float:
        '''Caclulates the Expected Value of a ticket

            Args:
                ticket_value (int): The value of a betting ticket if a camel comes in first place for a leg
                prob_first (float): The probability (0.0 - 1.0) that a camel will come in fist place
                prob_second (float): The probability (0.0 - 1.0) that a camel will come in second place

            Return:
                float: The expected value of the ticket
        '''
        return ticket_value * prob_first + prob_second - (1 - prob_first - prob_second)


    def run_analysis(self, trials:int)-> tuple[dict[str, tuple[float, float]], dict[str, tuple[float, float]]]:
        return self.run_enumerative_analysis(), self.run_experimental_analysis(trials)

    def __str__(self) -> str:
        enum, exper = self.run_analysis(5000)

        stats_str="  Enumerative\tExperimental\n"
        analysis = [(self.STYLES[c]+c+Style.RESET_ALL, enum[c][0],enum[c][1], exper[c][0], exper[c][1])  for c in enum ]
        stats_str+="   1st   2nd\t 1st   2nd\n"
        for row in analysis:
            stats_str+="{: >1} {: >5.2f} {: >5.2f} \t{: >5.2f} {: >5.2f}".format(*row)+"\n"

        advice_str="Available bets: "
        best_ev = -10
        best_camel = "x"
        for color in self.board.ticket_tents:
            tickets_left = self.board.ticket_tents[color]
            if len(tickets_left) > 0:
                top_ticket_value=tickets_left[0]
                ev = self.get_ticket_EV(top_ticket_value, enum[color][0], enum[color][1])
                if ev>best_ev:
                    best_ev=ev
                    best_camel=color
                advice_str += f"({color})"+self.STYLES[color]+str(top_ticket_value)+Style.RESET_ALL+f" EV:{ev:.2f} "
            else:
                advice_str += f"({color})"+self.STYLES[color]+"X"+Style.RESET_ALL+" "

        advice_str += "\nAI Advice: "
        if best_ev>1:
            advice_str+=f"  Bet on {self.STYLES[best_camel]+best_camel+Style.RESET_ALL} with an expected value of {best_ev:.2f}\n"
        else:
            advice_str+="  No camel has an EV > 1. You should roll instead of bet.\n"

        return stats_str + advice_str

if __name__ == "__main__":
    STYLES= {
            "r": Back.RED+Style.BRIGHT,
            "b": Back.BLUE+Style.BRIGHT,
            "g": Back.GREEN+Style.BRIGHT,
            "y": Back.YELLOW+Style.BRIGHT,
            "p": Back.MAGENTA
    }
    game_board = Board(STYLES)
    ai = AI(game_board)
    print(game_board)
    for _ in range(3):
        rolled_die=game_board.roll_die()
        game_board.move_camel(rolled_die)
    print(game_board)
    print(ai)
    print(game_board) #game state hasn't changed

    all_possible_roll_outcomes = ai.get_all_roll_sequences()
    print(f"There are {len(all_possible_roll_outcomes)} possible outcomes for the next two dice rolls:")
    for dice_sequence in all_possible_roll_outcomes:
        print(dice_sequence)
