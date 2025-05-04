import random
from typing import Optional



"""
Card representations "{value}{suit}"
The values are from 2-T where Jack = J, Queen = Q, King = K, Ace = A
The suits are D = diamonds, C = clubs, H = hearts, S = spades
"""

RANK_TO_VALUE = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
VALUE_TO_RANK = {1: 'A', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: 'T', 11: 'J', 12: 'Q', 13: 'K', 14: 'A'}
SUITS = ('D', 'C', 'H', 'S')

"""
Takes in hole and community cards, and returns the hand ranking and kickers
End term of the kickers is 
"""
def evaluate_hand(cards: set[str]) -> tuple[int, list[int]]:
    # Dictionary to hold the counts of each value of card
    value_counter = {}
    
    # Dictionary to hold the counts of each suit of card
    suit_counter = {}
    
    # Counts cards
    for card in cards:
        if RANK_TO_VALUE[card[0]] in value_counter.keys():
            value_counter[RANK_TO_VALUE[card[0]]] += 1
        else:
            value_counter[RANK_TO_VALUE[card[0]]] = 1
        
        if card[1] in suit_counter.keys():
            suit_counter[card[1]] += 1
        else:
            suit_counter[card[1]] = 1

    # Checks royal flush
    rf = royal_flush(value_counter, suit_counter, cards)
    if not rf is None:
        return rf

    # Checks four of a kind, three of a kind, full house, two pairs, pair, and high card
    dup = duplicates(value_counter, suit_counter, cards)

    # Checks straight, flush, and straight flush    
    sf = straight_flush(value_counter, suit_counter, cards)
    if sf is None or dup[0] == 3:
        return dup
    else:
        return sf

"""
Takes in two evaluated hands.
Returns 0 if p0 wins and 1 if p1 wins

By convention, p0 will be the bot and p1 will be the opponent.
I define a tie as not a win, and count it as a loss for the bot
"""
def choose_winner(p0: tuple[int, list[int]], p1: tuple[int, list[int]]) -> bool:
    # If hands have the same rank
    if(p0[0] == p1[0]):
        # Compare kickers
        while len(p0[0]) > 0:
            kicker0 = p0[1].pop()
            kicker1 = p1[1].pop()
            # Goes to the next kicker if they are the same
            if kicker0 == kicker1:
                continue
            else:
                # Otherwise compares kickers to determine winner
                return kicker1 > kicker0
        # Tie is a loss for the bot
        return True
    # Whoever has highest ranking hand wins
    # Note, 1 is the highest rank and 10 is the lowest.
    else:
        return p0[0] > p1[0]
    
def generate_hand() -> set[str]:
    hand = set()

    while(len(hand) < 5):
        hand.add(str(random.choice(list(RANK_TO_VALUE.keys()))) + str(random.choice(SUITS)))

    return hand

def royal_flush(values: dict, suits: dict, cards: set[str]) -> Optional[tuple[int, list[int]]]:
    # Royal flush must have 5 different cards values
    if len(values.keys()) < 5:
        return None
    
    # Checks if there is a suit with 5 different cards
    royal_suit = 0
    for suit in suits.keys():
        if suits[suit] >= 5:
            royal_suit = suit
    
    # No suits had 5 cards
    if royal_suit == 0:
        return None

    royal_values = set([10, 11, 12, 13, 14])
    # Checks if there a possible royal flush
    if len(set(values.keys()).intersection(royal_values)) == 5:
        royal_hand = set([f"T{royal_suit}", f"J{royal_suit}", f"Q{royal_suit}", f"K{royal_suit}", f"A{royal_suit}"])
        if len(royal_hand.intersection(cards)) == 5:
            return (1, [])
        else:
            return None

def straight_flush(values: dict, suits: dict, cards: set) -> Optional[tuple[int, list[int]]]:
    straight = False

    # Sorts the values
    sorted_values = sorted(values.keys())

    # Checks for straight
    in_a_row = 1
    straight_cards = set()
    
    for i in range(len(sorted_values) - 1):
        if(sorted_values[i + 1] == sorted_values[i] + 1):
            in_a_row += 1
            straight_cards.add(sorted_values[i])
            straight_cards.add(sorted_values[i+1])
        elif(in_a_row < 5):
            in_a_row = 1
            straight_cards = set()
            
    if(in_a_row < 5):
        # If ace
        if sorted_values[-1] == 14:
            in_a_row = 1
            # Retries with ace as 1
            sorted_values = [1] + sorted_values[:-1]
            for i in range(len(sorted_values) - 1):
                if(sorted_values[i + 1] == sorted_values[i] + 1):
                    in_a_row += 1
                    straight_cards.add(sorted_values[i])
                    straight_cards.add(sorted_values[i+1])
                elif(in_a_row < 5):
                    in_a_row = 1
                    straight_cards = set()
    
    # Confirms a straight is possible
    if(in_a_row >= 5):
        straight = True

    # Checks flush
    flush_suit = 0
    for suit in suits.keys():
        if suits[suit] == 5:
            # Flush is possible
            flush_suit = suit
            break
    # No flush
    if flush_suit == 0:
        if straight:
            # Just a straight
            return (6, list(straight_cards)[-5:])
        else:
            return None
    else:
        straight_flush_cards = set()
        for card in straight_cards:
            straight_flush_cards.add(f'{VALUE_TO_RANK[card]}{flush_suit}')
        # Checks straight and flush
        hand = (straight_flush_cards.intersection(cards))
        if len(hand) >= 5:
            h = sorted([RANK_TO_VALUE[card[0]] for card in hand])
            # Checks to make same suit
            in_a_row = 1
            for i in range(len(h) - 1):
                if(h[i + 1] == h[i] + 1):
                    in_a_row += 1
                else:
                    in_a_row = 1
            # Straight flush
            if(in_a_row == 5):
                return (2, h[-5:])
            
            else:
                # Just a flush
                return (5, sorted([RANK_TO_VALUE[card[0]] for card in cards if card[1] == suit]))

def duplicates(values: dict, suits: dict, cards: set) -> Optional[tuple[int, list[int]]]:
    
    sorted_values = sorted(values.keys())
    
    three_of_a_kind = False
    three_value = []
    pair_count = 0
    pair_values = []

    for value in values.keys():
        # Four of a kind
        if(values[value] == 4):
            sorted_values.remove(value)
            return (3, sorted_values[-1:] + [value])
        # Three of a kind
        if(values[value] == 3):
            three_value.append(value)
            three_of_a_kind = True
        # Pairs
        if(values[value] == 2):
            pair_count += 1
            pair_values.append(value)
    
    if(three_of_a_kind):
        # Full house
        if( pair_count > 0):
            return (4, [max(pair_values)] + three_value)
        else:
            # Just three of a kind
            sorted_values.remove(three_value[0])
            return (7, sorted_values[-2:] + three_value)

    # Two pairs
    if pair_count >= 2:
        pair_values.sort()
        # Takes the highest two pairs
        pair_values = pair_values[-2:]
        sorted_values.remove(pair_values[0])
        sorted_values.remove(pair_values[1])
        return (8, sorted_values[-1:] + pair_values)
    
    # Pair
    if pair_count == 1:
        sorted_values.remove(pair_values[0])
        return(9, sorted_values[-3:] + pair_values)
    
    # High card
    else:
        return(10, sorted_values[-5:])
