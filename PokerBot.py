import random
from typing import Optional



"""
Card representations "{value}{suit}"
The values are from 2-T where Jack = J, Queen = Q, King = K, Ace = A
The suits are D = diamonds, C = clubs, H = hearts, S = spades
"""

RANK_TO_VALUE = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
VALUE_TO_RANK = {2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: 'T', 11: 'J', 12: 'Q', 13: 'K', 14: 'A'}
SUITS = ('D', 'C', 'H', 'S')

"""
Takes in hole and community cards, and returns the hand ranking and kickers
End term of the kickers is 
"""
def evaluate_hand(cards: set[str]):
    # Dictionary to hold the counts of each value of card
    value_counter = {}
    
    # Dictionary to hold the counts of each suit of card
    suit_counter = {}
    
    for card in cards:
        if RANK_TO_VALUE[card[0]] in value_counter.keys():
            value_counter[RANK_TO_VALUE[card[0]]] += 1
        else:
            value_counter[RANK_TO_VALUE[card[0]]] = 1
        
        if card[1] in suit_counter.keys():
            suit_counter[card[1]] += 1
        else:
            suit_counter[card[1]] = 1

    return value_counter, suit_counter, cards
    # sorted_values = sorted(value_counter.keys())

    
    # # Flush, straight, and straight flush
    # straight = True
    # flush = True
    # if len(suit_counter.keys()) > 1:
    #     flush = False
    # if len(sorted_values) == 5:
    #     # Royal flush
    #     if(sorted_values[0] == 10):
    #         return (1,[])
    #     for i in range(4):
    #         if(sorted_values[i + 1] != sorted_values[i]):
    #             straight = False
    #             break
    #     # Catches straight with A, 2, 3, 4, 5
    #     if(sorted_values == [2, 3, 4, 5, 14]):
    #         straight = True
    # else:
    #     straight = False
    
    # if(straight and flush):
    #     return (2, sorted_values)
    # if(flush):
    #     return (5, sorted_values)
    # if(straight):
    #     return (6, sorted_values)

    # # Four of a kind and full house
    # if(len(sorted_values) == 2):
    #     # Four of a kind, with 4 of the lower card
    #     if(value_counter[sorted_values[1]] == 1):
    #         return(3, sorted_values.reverse())
    #     # Four of a kind, with 4 of the higher card
    #     elif(value_counter[sorted_values[1]] == 4):
    #         return(3, sorted_values)
    #     # Full house, with 3 of the lower card
    #     elif(value_counter[sorted_values[1]] == 2):
    #         return (4, sorted_values.reverse())
    #     # Full house, with 3 of the higher card
    #     else:
    #         return (4, sorted_values)
    
    # # 3 of a kind, two pairs, pair
    # if(len(sorted_values) < 5):
    #     pair_count = 0
    #     pair_values = []
    #     for value in sorted_values:
    #         # Three of a kind
    #         if value_counter[value] == 3:
    #             v = sorted_values.remove(value)
    #             return (7, (value, sorted_values + v))
    #         if value_counter[value] == 2:
    #             pair_count += 1
    #             pair_values.append(value)
    #     # Two pairs
    #     if pair_count == 2:
    #         sorted_values.remove(pair_values[0])
    #         sorted_values.remove(pair_values[1])
    #         return(8, sorted_values + sorted(pair_values))
    #     # Pair
    #     if pair_count == 1:
    #         sorted_values.remove(pair_values[0])
    #         return(9, sorted_values + pair_values)
    
    # # High card
    # return(10, sorted_values)

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
        if suits[suit] == 5:
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
            return False

def straight_flush(values: dict, suits: dict, cards: set) -> Optional[tuple[int, list[int]]]:

    # Sorts the values
    sorted_values = sorted(values.keys())

    # Checks for straight
    in_a_row = 1
    straight_cards = set()
    
    for i in range(len(sorted_values) - 1):
        print(in_a_row)
        if(sorted_values[i + 1] == sorted_values[i] + 1):
            in_a_row += 1
            straight_cards.add(sorted_values[i])
            straight_cards.add(sorted_values[i+1])
        elif(in_a_row < 5):
            in_a_row = 1
            straight_cards = set()
            

    # Not a straight
    if(in_a_row < 5):
        # If ace
        if sorted_values[-1] == 14:
            #TODO: retry with ace as 1




    # Checks flush
    flush_suit = 0
    for suit in suits.keys():
        if suits[suit] == 5:
            flush_suit = suit
            break
    # No flush
    if flush_suit == 0:
        return None
    else:
        straight_flush_cards = set()
        for card in straight_cards:
            straight_flush_cards.add(f'{VALUE_TO_RANK[card]}{flush_suit}')
        # Checks straight and flush
        hand = (straight_flush_cards.intersection(cards))
        if len(hand) >= 5:
            h = sorted([RANK_TO_VALUE[card[0]] for card in hand])
            return (2, h[-5:])

    # No flush
    return None
    

rf = set()
rf.add("3H")
rf.add("3D")
rf.add("6H")
rf.add("5H")
rf.add("4H")
rf.add("7H")
rf.add("AS")

v, s, c = evaluate_hand(rf)
print(straight_flush(v, s, c))