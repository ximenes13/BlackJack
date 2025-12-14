import random

# Create and shuffle the deck
suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
deck = [(rank, suit) for suit in suits for rank in ranks]


def shuffle_deck(deck):
    random.shuffle(deck)
    return deck


# Calculate hand value
def hand_value(hand):
    value = 0
    aces = 0
    for rank, suit in hand:
        if rank in ['J', 'Q', 'K']:
            value += 10
        elif rank == 'A':
            value += 11
            aces += 1
        else:
            value += int(rank)
    # Adjust for Aces
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value


# Deal a card
def deal_card(deck):
    return deck.pop()


# Display hands
def show_hands(player_hand, dealer_hand, hide_dealer=True):
    print("\nPlayer's hand:", player_hand, "Value:", hand_value(player_hand))
    if hide_dealer:
        print("Dealer's hand: [", dealer_hand[0], ", ? ]")
    else:
        print("Dealer's hand:", dealer_hand, "Value:", hand_value(dealer_hand))


# Game loop
def play_blackjack():
    global deck
    deck = shuffle_deck(deck.copy())

    player_hand = [deal_card(deck), deal_card(deck)]
    dealer_hand = [deal_card(deck), deal_card(deck)]

    show_hands(player_hand, dealer_hand)

    # Player's turn
    while hand_value(player_hand) < 21:
        move = input("Do you want to hit or stand? (h/s): ").lower()
        if move == 'h':
            player_hand.append(deal_card(deck))
            show_hands(player_hand, dealer_hand)
        elif move == 's':
            break
        else:
            print("Invalid input. Enter 'h' or 's'.")

    player_total = hand_value(player_hand)
    if player_total > 21:
        print("You busted! Dealer wins.")
        return

    # Dealer's turn
    while hand_value(dealer_hand) < 17:
        dealer_hand.append(deal_card(deck))

    show_hands(player_hand, dealer_hand, hide_dealer=False)
    dealer_total = hand_value(dealer_hand)

    # Determine winner
    if dealer_total > 21 or player_total > dealer_total:
        print("You win!")
    elif player_total < dealer_total:
        print("Dealer wins!")
    else:
        print("It's a tie!")


# Play game
while True:
    play_blackjack()
    again = input("\nPlay again? (y/n): ").lower()
    if again != 'y':
        print("Thanks for playing!")
        break
