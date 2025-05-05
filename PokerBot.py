import random
import time
import math
from typing import Optional

class GameState:
    def __init__(self, turn: str, stay: Optional[bool], parent: Optional["GameState"]):
        self.turn = turn    # Pre-flop (PF), pre-turn (PT), pre-river (PR), river (R)
        self.stay = stay    # Boolean representing if this is a stay state (true) or a fold state (false). N/A to root node
        self.left: Optional["GameState"] = None    # Child state 1
        self.right: Optional["GameState"] = None   # Child state 1
        self.n = 0  # Number of times visited
        self.t = 0  # Total value of node
        self.parent = parent

class Deck:
    def __init__(self):
        self.deck = ["2D", "3D", "4D", "5D", "6D", "7D", "8D", "9D", "TD", "JD", "QD", "KD", "AD",
                     "2C", "3C", "4C", "5C", "6C", "7C", "8C", "9C", "TC", "JC", "QC", "KC", "AC",
                     "2H", "3H", "4H", "5H", "6H", "7H", "8H", "9H", "TH", "JH", "QH", "KH", "AH",
                     "2S", "3S", "4S", "5S", "6S", "7S", "8S", "9S", "TS", "JS", "QS", "KS", "AS"]
    # Draws cards
    def draw(self) -> str:
        card = random.choice(self.deck)
        self.deck.remove(card)
        return card
    # Draws cards without removing them
    def temp_draw(self, num):
        cards = []
        for i in range(num):
            cards.append(self.draw())
        self.deck += cards
        return cards

"""
Card representations "{value}{suit}"
The values are from 2-T where Jack = J, Queen = Q, King = K, Ace = A
The suits are D = diamonds, C = clubs, H = hearts, S = spades
"""

RANK_TO_VALUE = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
VALUE_TO_RANK = {1: 'A', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: 'T', 11: 'J', 12: 'Q', 13: 'K', 14: 'A'}
SUITS = ('D', 'C', 'H', 'S')

NUM_CHOICES = {"PF" : 3, "PT" : 2, "PR" : 1, "R" : 0}
NEXT_TURN = {"PF" : "PT", "PT" : "PR", "PR" : "R", "R" : None}

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
Returns 1 if bot wins and 0 if bot loses

By convention, p0 will be the bot and p1 will be the opponent.
I define a tie as not a win, and count it as a loss for the bot
"""
def choose_winner(p0: tuple[int, list[int]], p1: tuple[int, list[int]]) -> int:
    # If hands have the same rank
    if(p0[0] == p1[0]):
        # Compare kickers
        while len(p0[1]) > 0 and len(p1[1]) > 0:
            kicker0 = p0[1].pop()
            kicker1 = p1[1].pop()
            # Goes to the next kicker if they are the same
            if kicker0 == kicker1:
                continue
            else:
                # Otherwise compares kickers to determine winner
                return kicker1 < kicker0
        
        # Bot had higher duplicate kicker
        if len(p0[1]) == 0:
            return 1
        # Ties, or when the opponent has higher duplicate kicker
        else:
            return 0
            
    # Whoever has highest ranking hand wins
    # Note, 1 is the highest rank and 10 is the lowest.
    else:
        return p0[0] < p1[0]
    
def generate_hand(turn: str) -> tuple[set[str], set[str], Deck]:
    # In pre-flop, both player receives hand
    hand = set()
    community_cards = set()
    deck = Deck()

    for i in range(2):
        hand.add(deck.draw())
    
    if(turn == "PT"):
        for i in range(3):
            community_cards.add(deck.draw())

    elif(turn == "PR"):
        for i in range(1):
            community_cards.add(deck.draw())
        
    return hand, community_cards, deck
    
    
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

def UCB1(node: GameState, parent_N: int) -> float:
    try:
        return node.t / node.n + 1.414 * (math.log(parent_N) / node.n) ** 0.5
    except(ArithmeticError):
        return float('inf')

def rollout(node: GameState, hand: set[str], community_cards: set[str], deck: Deck) -> int:
    for i in range(NUM_CHOICES[node.turn]):
        # Randomly chooses to stay or fold through each stage
        # 0 = stay
        if(random.randint(0,1)):
            return 0
    # If reaches this point, it chose to stay until showdown
    if(len(community_cards) < 5):
        for card in deck.temp_draw(5  - len(community_cards)):
            community_cards.add(card)
    
    # Randomly generate opponent hand
    opp_hand = set()
    new_cards = deck.temp_draw(2)
    opp_hand.add(new_cards[0])
    opp_hand.add(new_cards[1])

    # Each player can use community cards and their hole cards
    h0 = hand.union(community_cards)
    h1 = opp_hand.union(community_cards)

    # Determine who wins the 
    return choose_winner(evaluate_hand(h0), evaluate_hand(h1))

def MCTS(root: GameState, hand: set[str], start_community_cards: set[str], start_deck: Deck):
        start_time = time.time()
        total_n = 0
        total_t = 0

        while time.time() - start_time < 10:
            # Reset root node and cards for another simulation
            root.left = None
            root.right = None
            root.n = 0
            root.t = 0
            current = root
            community_cards = set(start_community_cards)
            drawn_cards = []
            flop = False
            turn = False
            river = False
            while True and time.time() - start_time < 10:
                # Checks if current is a leaf node
                if(current.left is None and current.right is None):
                    # If node already explored, expand
                    if(current.n != 0):
                        # If river state is being expanded, tree expansion has concluded
                        if(NEXT_TURN[current.turn] is None):
                            break
                        # Don't expand fold states
                        elif(current.stay):
                            current.left = GameState(NEXT_TURN[current.turn], True, current)    # Stay 
                            current.right = GameState(NEXT_TURN[current.turn], False, current)  # Fold
                            current = current.left  # Arbitrarily selects exploration state
                    
                    # Rollout
                    value = rollout(current, hand, set(community_cards), start_deck)

                    # Backpropagates
                    while not current is None:
                        current.n += 1
                        current.t += value
                        current = current.parent

                    # Sets current back to root and repeats
                    current = root
                    
                # Not a leaf node, use UCB1
                else:
                    # Chooses higher UCB1, or leftmost in case of a tie
                    if(UCB1(current.left, current.n) >= UCB1(current.right, current.n)):
                        current = current.left
                    else:
                        current = current.right
                    if(current.turn == "PT" and not flop):
                        flop = True
                        for i in range(3):
                            # Add three random cards to community cards
                            card = start_deck.draw()
                            drawn_cards.append(card)
                            community_cards.add(card)
                        
                    elif(current.turn == "PR" and not turn):
                        # Add one card for PR
                        card = start_deck.draw()
                        drawn_cards.append(card)
                        community_cards.add(card)  
                        turn = True
                        
                    elif(current.turn == "R" and not river):
                        # Add one card for PR
                        card = start_deck.draw()
                        drawn_cards.append(card)
                        community_cards.add(card)  
                        river = True
                        

            total_n += root.n
            total_t += root.t
            start_deck.deck += drawn_cards
            

        # Returns win probability
        return (total_t / total_n * 100)


    
if __name__ == "__main__":
    for i in range(10):
        bot_hand, community_cards, deck = generate_hand("PF")
        init_state = GameState("PF", True, None)
        print(f"Hand: {bot_hand} Turn: {init_state.turn} Win: {MCTS(init_state, bot_hand, community_cards, deck)}")
    print()
    for i in range(10):
        bot_hand, community_cards, deck = generate_hand("PT")
        init_state = GameState("PT", True, None)
        print(f"Hand: {bot_hand} Turn: {init_state.turn} Win: {MCTS(init_state, bot_hand, community_cards, deck)}")
    print()
    for i in range(10):
        bot_hand, community_cards, deck = generate_hand("PR")
        init_state = GameState("PR", True, None)
        print(f"Hand: {bot_hand} Turn: {init_state.turn} Win: {MCTS(init_state, bot_hand, community_cards, deck)}")
    