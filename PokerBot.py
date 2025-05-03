"""
Card representations (value, suit)
The values are from 2-14 where Jack = 11, Queen = 12, King = 13, Ace = 14
The suits are 0 = diamonds, 2 = clubs, 3 = hearts, 4 = spades
"""

"""
Takes in hole and community cards, and returns the hand ranking and kickers
End term of the kickers
"""
def evaluate_hand(cards: list[tuple[int]]) -> tuple[int, tuple[int]]:
    # Dictionary to hold the counts of each value of card
    value_counter = {}
    
    # Dictionary to hold the counts of each suit of card
    suit_counter = {}
    
    for card in cards:
        if card[0] in value_counter.keys():
            value_counter[card[0]] += 1
        else:
            value_counter[card[0]] = 0
        
        if card[1] in suit_counter.keys():
            suit_counter[card[1]] += 1
        else:
            suit_counter[card[1]] = 0

    sorted_values = sorted(value_counter.keys())
    

    # Royal flush
    if sorted_values == [10, 11, 12, 13, 14]:
        return (1,())
        
    
    # Flush, straight, and straight flush
    straight = True
    flush = True
    if len(suit_counter.keys()) > 1:
        flush = False
    for i in range(4):
        if(sorted_values[i + 1] != sorted_values[i]):
            straight = False
            break
    
    if(straight and flush):
        return (2, sorted_values)
    if(flush):
        return (5, sorted_values)
    if(straight):
        return (6, sorted_values)

    # Four of a kind and full house
    if(len(sorted_values) == 2):
        # Four of a kind, with 4 of the lower card
        if(value_counter[sorted_values[1]] == 1):
            return(3, sorted_values.reverse())
        # Four of a kind, with 4 of the lower card
        elif(value_counter[sorted_values[1]] == 4):
            return(3, sorted_values)
        # Full house, with 3 of the lower card
        elif(value_counter[sorted_values[1]] == 2):
            return (4, sorted_values.reverse())
        # Full house, with 3 of the higher card
        else:
            return (4, sorted_values)
    
    # 3 of a kind and two pairs
    if(len(sorted_values) == 3):
        for value in sorted_values:
            # Three of a kind
            if value_counter[value] == 3:
                sorted_values.remove(value)
                return (7, (value, sorted_values))