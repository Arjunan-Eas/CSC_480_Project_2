import random
import time
import math
from typing import Optional

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
RESULT_TO_HAND = {1 : "Royal flush", 2 : "Straight Flush", 3 : "Four of a kind", 4 : "Full House", 5 : "Flush", 6 : "Straight", 7 : "Three of a kind", 8 : "Two pair", 9 : "Pair", 10 : "High card"}



class PokerState:
    def __init__(self, bot_hand: set[str], opp_hand: set[str], community_cards: set[str], turn: str):
        self.bot_hand = bot_hand
        self.opp_hand = opp_hand
        self.community_cards = community_cards
        self.turn = turn
    # Updates current poker state based on what turn it is. Returns a new object
    def update_table(self, all_combos: set["PokerState"]) -> "PokerState":
        if(self.turn == "PF"):
            while True:
                new_opp_cards = set()
                while len(new_opp_cards) < 2:
                    new_opp_cards.add(random.choice(Deck.reference_deck))
                    new_opp_cards = new_opp_cards.difference(self.bot_hand)
                new_community_cards = set()
                while len(new_community_cards) < 3:
                    new_community_cards.add(random.choice(Deck.reference_deck))
                    new_community_cards = new_community_cards.difference(self.bot_hand, new_opp_cards)
                next_state = PokerState(self.bot_hand, new_opp_cards, new_community_cards, "PT")
                if not next_state in all_combos:
                    return next_state
        elif(self.turn == "PT"):
            while True:
                new_opp_cards = set()
                while len(new_opp_cards) < 2:
                    new_opp_cards.add(random.choice(Deck.reference_deck))
                    new_opp_cards = new_opp_cards.difference(self.bot_hand)
                new_community_cards = set()
                while len(new_community_cards) < 4:
                    new_community_cards.add(random.choice(Deck.reference_deck))
                    new_community_cards = new_community_cards.difference(self.bot_hand, new_opp_cards)
                next_state = PokerState(self.bot_hand, new_opp_cards, new_community_cards, "PR")
                if not next_state in all_combos:
                    return next_state
        elif(self.turn == "PR"):
            while True:
                new_opp_cards = set()
                while len(new_opp_cards) < 2:
                    new_opp_cards.add(random.choice(Deck.reference_deck))
                    new_opp_cards = new_opp_cards.difference(self.bot_hand)
                new_community_cards = set()
                while len(new_community_cards) < 5:
                    new_community_cards.add(random.choice(Deck.reference_deck))
                    new_community_cards = new_community_cards.difference(self.bot_hand, new_opp_cards)
                next_state = PokerState(self.bot_hand, new_opp_cards, new_community_cards, "R")
                if not next_state in all_combos:
                    return next_state
        else:
            # Return same state
            return PokerState(set(self.bot_hand), set(self.opp_hand), set(self.community_cards), self.turn)    
    # Hashable version of the current state to put in a set
    def hashable_state(self) -> str:
        hash_str = ""
        for card in community_cards:
            hash_str += card
        return hash_str
            

class GameState:
    def __init__(self, turn: str, cards: PokerState, parent: Optional["GameState"], all_combinations: set[str]):
        self.turn = turn    # Pre-flop (PF), pre-turn (PT), pre-river (PR), river (R)
        self.parent = parent    # Parent node
        self.cards = cards
        self.child_states: set["GameState"] = set()   # Contains all of the child states of this node
        self.n = 0  # Number of times visited
        self.t = 0  # Total value of node
        self.all_combinations = all_combinations
        

class Deck:
    # Immutable version of the deck for reference
    reference_deck = ("2D", "3D", "4D", "5D", "6D", "7D", "8D", "9D", "TD", "JD", "QD", "KD", "AD",
                      "2C", "3C", "4C", "5C", "6C", "7C", "8C", "9C", "TC", "JC", "QC", "KC", "AC",
                      "2H", "3H", "4H", "5H", "6H", "7H", "8H", "9H", "TH", "JH", "QH", "KH", "AH",
                      "2S", "3S", "4S", "5S", "6S", "7S", "8S", "9S", "TS", "JS", "QS", "KS", "AS")
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

def breakdown_result(result: tuple[int, list[int]]) -> str:      
    rank = RESULT_TO_HAND[result[0]]
    if result[0] == 1:
        return rank
    if result[0] in [2, 4, 5, 6]:
        return rank + f" ({str(result[1])})"
    if result[0] == 3:
        return rank + f" ({result[1][-1]}), Kicker: {result[1][-2]}"
    if result[0] == 7:
        return rank + f" ({result[1][-1]}), Kickers: {result[1][-3:-1]}"
    if result[0] == 8:
        return rank + f" ({result[1][-2]}, {result[1][-1]}), Kicker: {result[1][-3]}"
    if result[0] == 9:
        return rank + f" ({result[1][-1]}), Kickers: {result[1][-4:-1]}"
    else:
        return rank + f" ({result[1][-1]}), Kickers: {result[1][-5:-1]}"
    
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
    
def generate_hand(bot_hand: set[str], community_cards: set[str], opp_hand: set[str]) -> tuple[set[str], set[str], set[str]]:
    # PF
    if(len(bot_hand) == 0):
        hand = set()
        cc = set()
        o_hand = set()

        while len(hand) < 2:
            new_card = random.choice(Deck.reference_deck)
            if(not (new_card in hand)):
                hand.add(new_card)
            
        while len(o_hand) < 2:
            new_card = random.choice(Deck.reference_deck)
            if(not (new_card in hand or new_card in o_hand)):
                o_hand.add(new_card)

    # PT
    elif(len(bot_hand) == 2 and len(community_cards) == 0):
        hand = set(bot_hand)
        cc = set()
        o_hand = set(opp_hand)

        while len(cc) < 3:
            new_card = random.choice(Deck.reference_deck)
            if(not (new_card in hand or new_card in o_hand or new_card in cc)):
                cc.add(new_card)
    
    # PR
    elif(len(bot_hand) == 2 and len(community_cards) == 3):
        hand = set(bot_hand)
        cc = set(community_cards)
        o_hand = set(opp_hand)
        
        while len(cc) < 4:
            new_card = random.choice(Deck.reference_deck)
            if(not (new_card in hand or new_card in o_hand or new_card in cc)):
                cc.add(new_card)
    
    # R
    elif(len(bot_hand) == 2 and len(community_cards) == 4):
        hand = set(bot_hand)
        cc = set(community_cards)
        o_hand = set(opp_hand)

        while len(cc) < 5:
            new_card = random.choice(Deck.reference_deck)
            if(not (new_card in hand or new_card in o_hand or new_card in cc)):
                cc.add(new_card)

    return hand, cc, o_hand
    
    
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

def rollout( hand: set[str], opp_hand: set[str], community_cards: set[str]) -> int:
    # If reaches this point, it chose to stay until showdown
    while(len(community_cards) < 5):
        new_card = random.choice(Deck.reference_deck)
        if not (new_card in hand or new_card in community_cards or new_card in opp_hand):
            community_cards.add(new_card)
    
    # Each player can use community cards and their hole cards
    h0 = hand.union(community_cards)
    h1 = opp_hand.union(community_cards)

    # Determine who wins the 
    return choose_winner(evaluate_hand(h0), evaluate_hand(h1))

def MCTS(root: GameState):
        start_time = time.time()

        # For tracking
        total_combos = {"PF": 0, "PT": 0, "PR" : 0, "R" : 0}
        # Stores the number of unique possibilities at each stage based on which turn the start root is in
        max_len = {"PF": math.perm(50, 5), "PT": math.perm(45, 1), "PR" : math.perm(44, 1), "R" : 1, None : -1}

        # Starts off at root node
        current = root

        while True and time.time() - start_time < 10:
            # Checks if current is a leaf node
            if(current.child_states is None or len(current.child_states) < max_len[current.turn]):
                # If node already explored, expand
                if(current.n != 0):
                    # Doesn't expand past river
                    if(not current.turn is None):
                        new_child = GameState(NEXT_TURN[current.turn], current.cards.update_table(current.all_combinations), current, set())
                        current.all_combinations.add(new_child.cards)
                        total_combos[current.turn] += 1
                        current.child_states.add(new_child)
                        current = new_child  # Sets next exploration state as the newly created exploration
                
                # Rollout
                value = rollout(current.cards.bot_hand, current.cards.opp_hand, set(current.cards.community_cards))

                # Backpropagates
                while not current is None:
                    current.n += 1
                    current.t += value
                    current = current.parent

                # Sets current back to root and repeats
                current = root
                
            # Not a leaf node, use UCB1
            else:
                # Chooses higher UCB1, or first infinity in case of tie
                max_ucb1 = 0
                best_child = current
                for child in current.child_states:
                    ucb1 = UCB1(child, current.n)
                    if ucb1 > max_ucb1:
                        max_ucb1 = ucb1
                        best_child = child
                    if max_ucb1 == float('inf'):
                        break
                current = best_child

        # Returns win probability
        return (root.t / root.n * 100)


    
if __name__ == "__main__":

        bot_hand, community_cards, opp_hand = generate_hand(set(), set(), set())
        init_state = GameState("PF", PokerState(bot_hand, set(), community_cards, "PF"), None, set())
        print(f"Bot hand: {bot_hand}")
        chance = MCTS(init_state)
        print(f"Pre-flop win chance: {chance} %")

        bot_hand, community_cards, opp_hand = generate_hand(bot_hand, community_cards, opp_hand)
        init_state = GameState("PT", PokerState(bot_hand, set(), community_cards, "PT"), None, set())
        print(f"Bot hand: {bot_hand}  Community cards: {community_cards}")
        chance = MCTS(init_state)

        print(f"Pre-turn win chance: {chance} %")

        bot_hand, community_cards, opp_hand = generate_hand(bot_hand, community_cards, opp_hand)
        init_state = GameState("PR", PokerState(bot_hand, set(), community_cards, "PR"), None, set())
        print(f"Bot hand: {bot_hand}  Community cards: {community_cards}")
        chance = MCTS(init_state)

        print(f"Pre-river win chance: {chance} %")

        bot_hand, community_cards, opp_hand = generate_hand(bot_hand, community_cards, opp_hand)
        
        print(f"Bot hand: {bot_hand}  Community cards: {community_cards}  Opponent hand: {opp_hand}")
        if(choose_winner(evaluate_hand(bot_hand.union(community_cards)), evaluate_hand(opp_hand.union(community_cards)))):
            result = "Win"

        else:
            result = "Loss"

        print(f"Actual result: {result}")
        print(f"Bot: {breakdown_result(evaluate_hand(bot_hand.union(community_cards)))}")
        print(f"Opponent: {breakdown_result(evaluate_hand(opp_hand.union(community_cards)))}")




    