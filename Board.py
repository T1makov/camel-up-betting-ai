import random
from colorama import Back, Style

try:
    from Pyramid import Pyramid
except ModuleNotFoundError:
    print("Pyramid.py is not found.")
    pass

class Board:
    def __init__(self, STYLES: dict[str, str] ):
        self.TRACK_LENGTH = 16
        self.STYLES = STYLES
        self.track = [[] for _ in range(self.TRACK_LENGTH)]
        self.place_camels()
        self.pyramid = Pyramid(STYLES)
        self.ticket_tents = {
                             "r" : [5, 3, 2, 2],
                             "b" : [5, 3, 2, 2],
                             "g" : [5, 3, 2, 2],
                             "y" : [5, 3, 2, 2],
                             "p" : [5, 3, 2, 2]
                            }
        self.dice_tents = []


    def place_camels(self):
        '''Places stacked camels in a random order on the first position of the track.
        '''
        self.track[0] = []
        available_camels = list(self.STYLES.keys())
        for i in range(5):
            camel = random.choice(available_camels) ##Choosing a random camel from the list
            self.track[0].append(camel) ## put the camel on the track
            available_camels.remove(camel) ##remove the camel from the list of avaiable_camels
    def move_camel(self, die: tuple[str, int]):
        if die == ("", 0):
            return

        moving_list = []
        current_location = None

        for location, inner_list in enumerate(self.track):
            if die[0] in inner_list:
                current_location = location
                moving_list = inner_list[inner_list.index(die[0]):]
                break

        if current_location is None or len(moving_list) == 0:
            return

        for camel in moving_list:
            self.track[current_location].remove(camel)

        new_location = min(current_location + die[1], self.TRACK_LENGTH - 1)

        for camel in moving_list:
            self.track[new_location].append(camel)
    def roll_die(self):
        '''Shakes the pyramid and places the rolled die on the next dice tent
            If the pyramid is empty, returns a die with color "" and value 0.

            Returns:
                tuple[str, int] - A tuple representation of the rolled die
        '''
        the_roll = self.pyramid.shake()
        if the_roll == ("", 0):
            return the_roll
        self.dice_tents.append(the_roll)
        return the_roll

    def take_ticket(self, color:str):
        '''Reomves the top ticket available from the ticket tent of the given color.
           Tickets are removed from the tent in the order of their values, with the highest value ticket being removed first.

            If no tickets are available, returns a ticket with value of 0.

            Returns:
                tuple[str, int] - A tuple representation of the ticket
        '''
        if self.ticket_tents[color] == []:
            return (color, 0)
        output = (color, self.ticket_tents[color][0])
        self.ticket_tents[color].pop(0)
        return output
    def is_leg_finished(self):
        ''' A leg is finished when all dice have been rolled. This is determined by checking dice tents
            as playing with crazy camels involves more than five dice.

            Returns:
                bool - True if all dice have been rolled, False otherwise
        '''
        if len(self.dice_tents) == 5:
            return True
        return False

    def get_rankings(self):
        '''Returns the first and second place camels as a tuple of strings.

            Return
                tuple[str, str] - A tuple containing the first and second place camels
        '''
        camels_list = []
        counter = 0
        for inner_list in self.track[::-1]:
            for camel in inner_list[::-1]:
                if camel:
                    camels_list.append(camel)
                    counter += 1
                    if counter == 2:
                        return tuple(camels_list)


    def reset_leg(self):
        '''Resets the board for a new leg of the game.
            - Resets the pyramid
            - Resets the ticket tents
            - Empties the dice tents
            - Does not move camels
        '''
        self.pyramid.reset_leg()
        self.ticket_tents = {
                             "r" : [5, 3, 2, 2],
                             "b" : [5, 3, 2, 2],
                             "g" : [5, 3, 2, 2],
                             "y" : [5, 3, 2, 2],
                             "p" : [5, 3, 2, 2]
                            }
        self.dice_tents = []


    def __str__(self):
        board_string = ""
         #Ticket Tents
        ticket_string = "Ticket Tents: "
        for ticket_color in self.ticket_tents:
            if len(self.ticket_tents[ticket_color]) > 0:
                next_ticket_value = str(self.ticket_tents[ticket_color][0])
            else:
                next_ticket_value = 'X'
            ticket_string+=self.STYLES[ticket_color]+next_ticket_value+Style.RESET_ALL+" "
        board_string += ticket_string +"\t\t"

        #Dice Tents
        dice_string = "Dice Tents: "
        for die in self.dice_tents:
            dice_string+=self.STYLES[die[0]]+str(die[1])+Style.RESET_ALL+" "
        for i in range (5-len(self.dice_tents)):
            dice_string+=Back.WHITE+" "+Style.RESET_ALL+" "

        #Camels and Race Track
        board_string += dice_string +"\n"
        for row in range(4, -1, -1):
            row_str = [" "]*16
            for i in range(len(self.track)):
                for camel_place, camel in enumerate(self.track[i]):
                    if camel_place == row:
                        row_str[i]=self.STYLES[camel]+ camel +  Style.RESET_ALL
            board_string += "🌴 "+str("   ".join(row_str))+" |🏁\n"
        board_string += "   "+"".join([str(i)+"   " for i in range(1, 10)])
        board_string += "".join([str(i)+"  " for i in range(10, 17)])

        return board_string



if __name__ == "__main__":
    STYLES= {
            "r": Back.RED+Style.BRIGHT,
            "b": Back.BLUE+Style.BRIGHT,
            "g": Back.GREEN+Style.BRIGHT,
            "y": Back.YELLOW+Style.BRIGHT,
            "p": Back.MAGENTA
    }
    board = Board(STYLES)
    print(str(board)+"\n")
    board.place_camels()
    board.move_camel(("y", 2))
    board.move_camel(("p", 1))
    print(board.get_rankings())

    num_rolls=2
    for _ in range(num_rolls):
        rolled_die=board.roll_die()
        board.move_camel(rolled_die)
        print(f"{rolled_die} was shaken from the pyramid")
    print(board.pyramid)
    ticket = board.take_ticket(rolled_die[0])
    print(f"Player took a {rolled_die[0]} ticket: {ticket}")
    print(board)

    first, second = board.get_rankings()
    print(f"First place: {first}, Second place: {second}")
    print("\nResetting leg...")
    board.reset_leg()
    print(board)
