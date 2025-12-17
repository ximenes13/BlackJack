from flask import Flask, render_template, request, session, jsonify
from datetime import timedelta
from game import new_deck, hand_value, is_blackjack, to_str

app = Flask(__name__)
app.secret_key = "change-me" # secure session data
app.permanent_session_lifetime = timedelta(hours=1) # sets expiration time

def ensure_state():
    # One player, optional split => list of hands and bets
    if "bankroll" not in session:
        session["bankroll"] = 1000
    if "deck" not in session:
        session["deck"] = new_deck()
    if "hands" not in session:
        session["hands"] = []
    if "bets" not in session:
        session["bets"] = []
    if "dealer" not in session:
        session["dealer"] = []
    if "active_hand" not in session:
        session["active_hand"] = 0
    if "finished" not in session:
        session["finished"] = True
    if "message" not in session:
        session["message"] = ""
    if "can_insure" not in session:
        session["can_insure"] = False
    if "insurance_bet" not in session:
        session["insurance_bet"] = 0
    if "phase" not in session:
        # phases: "betting", "playing", "dealer", "payout"
        session["phase"] = "betting"

def deal_round(bet):
    ensure_state()
    deck = session["deck"]
    if len(deck) < 15:
        deck = new_deck()

    dealer = [deck.pop(), deck.pop()]
    player = [deck.pop(), deck.pop()]

    session["deck"] = deck
    session["dealer"] = dealer
    session["hands"] = [player]
    session["bets"] = [bet]
    session["active_hand"] = 0
    session["finished"] = False
    session["message"] = ""
    session["insurance_bet"] = 0
    session["phase"] = "playing"

    # insurance only if dealer up-card is Ace
    session["can_insure"] = (dealer[0][0] == "A")

def settle_round():
    """Dealer plays and all hands are compared, bankroll updated."""
    deck = session["deck"]
    dealer = session["dealer"]
    hands = session["hands"]
    bets = session["bets"]
    bankroll = session["bankroll"]
    insurance_bet = session["insurance_bet"]

    # Dealer checks for blackjack first.
    dealer_has_blackjack = is_blackjack(dealer)

    # Resolve insurance first. Insurance pays 2:1 if dealer has blackjack.
    if insurance_bet > 0:
        if dealer_has_blackjack:
            bankroll += insurance_bet * 2
        # else insurance bet lost
    session["insurance_bet"] = 0

    # If dealer has blackjack, players without blackjack lose immediately.
    if dealer_has_blackjack:
        for i, hand in enumerate(hands):
            if is_blackjack(hand):
                # push on equal blackjack (even money not implemented).
                bankroll += bets[i]
        session["bankroll"] = bankroll
        session["finished"] = True
        session["phase"] = "payout"
        session["message"] = "Dealer has blackjack."
        return

    # Dealer plays out if no dealer blackjack. Dealer hits to 17+, standing on all 17.
    while hand_value(dealer) < 17:
        if not deck:
            deck = new_deck()
        dealer.append(deck.pop())

    session["deck"] = deck
    dealer_total = hand_value(dealer)
    bankroll_change = 0
    messages = []

    # Evaluate each hand
    for i, hand in enumerate(hands):
        total = hand_value(hand)
        bet = bets[i]
        hand_msg = f"Hand {i+1}: "

        if total > 21:
            hand_msg += "Player busts, loses."
            bankroll_change -= bet
        elif is_blackjack(hand):
            # No dealer blackjack here, so pay 3:2.
            win = int(bet * 1.5)
            bankroll_change += bet + win
            hand_msg += f"Blackjack! Win {win}."
        elif dealer_total > 21:
            bankroll_change += bet * 2
            hand_msg += "Dealer busts, player wins."
        elif total > dealer_total:
            bankroll_change += bet * 2
            hand_msg += "Player wins."
        elif total < dealer_total:
            bankroll_change -= bet
            hand_msg += "Dealer wins."
        else:
            bankroll_change += bet
            hand_msg += "Push (tie)."

        messages.append(hand_msg)

    bankroll += bankroll_change
    session["bankroll"] = bankroll
    session["finished"] = True
    session["phase"] = "payout"
    session["message"] = " ".join(messages)

def compute_flags():
    hands = session["hands"]
    dealer = session["dealer"]
    active = session["active_hand"]
    finished = session["finished"]
    phase = session["phase"]

    can_hit = False
    can_stand = False
    can_double = False
    can_split = False
    can_surrender = False
    can_insure = False

    if phase == "playing" and not finished and active < len(hands):
        hand = hands[active]
        if hand_value(hand) < 21:
            can_hit = True
            can_stand = True
        # double: only allowed on first 2 cards.
        if len(hand) == 2:
            can_double = True
            can_surrender = True   # late surrender before any hit.
            # simple rule: allow one split if same rank and no previous split.
            if len(hands) == 1 and hand[0][0] == hand[1][0]:
                can_split = True

        if session.get("can_insure", False) and len(hand) == 2:
            can_insure = True

    return dict(
        can_hit=can_hit,
        can_stand=can_stand,
        can_double=can_double,
        can_split=can_split,
        can_surrender=can_surrender,
        can_insure=can_insure,
    )

def make_state():
    ensure_state()
    hands = session["hands"]
    dealer = session["dealer"]
    active = session["active_hand"]
    finished = session["finished"]
    bankroll = session["bankroll"]
    bets = session["bets"]
    phase = session["phase"]

    flags = compute_flags()

    # hide dealer hole card until dealer phase or finished.
    if phase in ("dealer", "payout") or finished:
        dealer_visible = dealer
        dealer_total = hand_value(dealer)
    else:
        dealer_visible = dealer[:1]
        dealer_total = hand_value(dealer_visible)

    return {
        "bankroll": bankroll,
        "bets": bets,
        "hands": [to_str(h) for h in hands],
        "hand_totals": [hand_value(h) for h in hands],
        "active_hand": active,
        "dealer": to_str(dealer_visible),
        "dealer_total": dealer_total,
        "finished": finished,
        "phase": phase,
        "message": session.get("message", ""),
        **flags,
    }


@app.route("/")
def index():
    ensure_state()
    return render_template("index.html")


@app.route("/api/state", methods=["GET"])
def api_state():
    return jsonify(make_state())


@app.route("/api/bet", methods=["POST"])
def api_bet():
    ensure_state()
    data = request.get_json() or {}
    bet = int(data.get("bet", 0))
    bankroll = session["bankroll"]

    if bet <= 0 or bet > bankroll:
        return jsonify({"error": "Invalid bet."}), 400

    bankroll -= bet
    session["bankroll"] = bankroll
    deal_round(bet)
    return jsonify(make_state())


@app.route("/api/hit", methods=["POST"])
def api_hit():
    ensure_state()
    flags = compute_flags()
    if not flags["can_hit"]:
        return jsonify(make_state())

    deck = session["deck"]
    hands = session["hands"]
    active = session["active_hand"]

    if not deck:
        deck = new_deck()

    hands[active].append(deck.pop())
    session["deck"] = deck
    session["hands"] = hands

    # if bust, move to next hand or dealer
    if hand_value(hands[active]) > 21:
        if active + 1 < len(hands):
            session["active_hand"] = active + 1
        else:
            session["phase"] = "dealer"
            settle_round()

    return jsonify(make_state())


@app.route("/api/stand", methods=["POST"])
def api_stand():
    ensure_state()
    flags = compute_flags()
    if not flags["can_stand"]:
        return jsonify(make_state())

    active = session["active_hand"]
    hands = session["hands"]
    if active + 1 < len(hands):
        session["active_hand"] = active + 1
    else:
        session["phase"] = "dealer"
        settle_round()

    return jsonify(make_state())


@app.route("/api/double", methods=["POST"])
def api_double():
    ensure_state()
    flags = compute_flags()
    if not flags["can_double"]:
        return jsonify(make_state())

    deck = session["deck"]
    hands = session["hands"]
    bets = session["bets"]
    active = session["active_hand"]
    bankroll = session["bankroll"]

    bet = bets[active]
    if bankroll < bet:
        session["message"] = "Not enough bankroll to double."
        return jsonify(make_state())

    bankroll -= bet
    bets[active] += bet

    if not deck:
        deck = new_deck()
    hands[active].append(deck.pop())

    session["deck"] = deck
    session["hands"] = hands
    session["bets"] = bets
    session["bankroll"] = bankroll

    # after double, stand automatically.
    if active + 1 < len(hands):
        session["active_hand"] = active + 1
    else:
        session["phase"] = "dealer"
        settle_round()

    return jsonify(make_state())


@app.route("/api/split", methods=["POST"])
def api_split():
    ensure_state()
    flags = compute_flags()
    if not flags["can_split"]:
        return jsonify(make_state())

    deck = session["deck"]
    hands = session["hands"]
    bets = session["bets"]
    active = session["active_hand"]
    bankroll = session["bankroll"]

    hand = hands[active]
    bet = bets[active]

    if bankroll < bet:
        session["message"] = "Not enough bankroll to split."
        return jsonify(make_state())

    # one split max: create 2 hands.
    bankroll -= bet
    card1, card2 = hand
    new_hand1 = [card1, deck.pop()]
    new_hand2 = [card2, deck.pop()]

    hands = [new_hand1, new_hand2]
    bets = [bet, bet]

    session["deck"] = deck
    session["hands"] = hands
    session["bets"] = bets
    session["bankroll"] = bankroll
    session["active_hand"] = 0

    return jsonify(make_state())


@app.route("/api/surrender", methods=["POST"])
def api_surrender():
    ensure_state()
    flags = compute_flags()
    if not flags["can_surrender"]:
        return jsonify(make_state())

    hands = session["hands"]
    bets = session["bets"]
    active = session["active_hand"]
    bankroll = session["bankroll"]

    bet = bets[active]
    # player loses half bet, gets half back.
    bankroll += bet // 2

    # mark this hand as finished by making it a bust sentinel with 0 bet
    hands[active] = []
    bets[active] = 0
    session["hands"] = hands
    session["bets"] = bets
    session["bankroll"] = bankroll

    # if any other hand, move; else dealer resolves but only for non‑empty hands
    if active + 1 < len(hands):
        session["active_hand"] = active + 1
    else:
        session["phase"] = "dealer"
        settle_round()

    return jsonify(make_state())


@app.route("/api/insurance", methods=["POST"])
def api_insurance():
    ensure_state()
    flags = compute_flags()
    if not flags["can_insure"]:
        return jsonify(make_state())

    bankroll = session["bankroll"]
    bets = session["bets"]
    # insurance up to half original bet on first hand.
    base_bet = bets[0] if bets else 0
    max_ins = base_bet // 2
    if max_ins <= 0 or bankroll < max_ins:
        session["message"] = "Cannot take insurance."
        return jsonify(make_state())

    bankroll -= max_ins
    session["bankroll"] = bankroll
    session["insurance_bet"] = max_ins
    session["can_insure"] = False

    return jsonify(make_state())


@app.route("/api/reset", methods=["POST"])
def api_reset():
    session.clear()
    ensure_state()
    return jsonify(make_state())


if __name__ == "__main__":
    import logging

    logging.getLogger("werkzeug").setLevel(logging.ERROR)

    host = "127.0.0.1"
    port = 5000
    print(f"http://{host}:{port}")

    app.run(host=host, port=port, debug=True, use_reloader=False)


