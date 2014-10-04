from enum import Enum
from random import shuffle, choice

class Rank(Enum):
    Seven = 7
    Eight = 8
    Nine = 9
    Ten = 10
    Jack = 11
    Queen = 12
    King = 13
    Ace = 14

PIPS = {
    Rank.Seven: 7,
    Rank.Eight: 8,
    Rank.Nine: 9,
    Rank.Ten: 10,
    Rank.Jack: 10,
    Rank.Queen: 10,
    Rank.King: 10,
    Rank.Ace: 11
}

class Suit:
    DIAMONDS = '♢'
    HEARTS = '♡'
    SPADES = '♤'
    CLUBS = '♧'
    suits = [DIAMONDS, HEARTS, SPADES, CLUBS]

class Good:
    GOOD = 'good'
    EQUAL = 'equal'
    NOT_GOOD = 'not good'

class Category:
    POINT = 'point'
    SEQUENCES = 'sequences'
    SETS = 'sets'
    categories = [POINT, SEQUENCES, SETS]


class Card:

    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __str__(self):
        return "{}{}".format(self.rank.name, self.suit.capitalize())

    def __repr__(self):
        return str(self)

    def __lt__(self, other):
        return self.rank.value < other.rank.value

    def __eq__(self, other):
        return self.rank.value == other.rank.value

    def __sub__(self, other):
        return self.rank.value - other.rank.value

    def hash(self):
        CHARMAP = {
            Rank.Seven: '7',
            Rank.Eight: '8',
            Rank.Nine: '9',
            Rank.Ten: 'T',
            Rank.Jack: 'J',
            Rank.Queen: 'Q',
            Rank.King: 'K',
            Rank.Ace: 'A',
            Suit.DIAMONDS: 'D',
            Suit.HEARTS: 'H',
            Suit.SPADES: 'S',
            Suit.CLUBS: 'C'
        }
        return '{}{}'.format(CHARMAP[self.rank], CHARMAP[self.suit])

    def __hash__(self):
        return hash(self.hash())

def all_cards():
    return [Card(r, s) for s in Suit.suits for r in Rank]

class Deck:
    def __init__(self, cards):
        self.cards = []
        self.cards.extend(cards)
        shuffle(self.cards)

    def __len__(self):
        return len(self.cards)

    def pop(self):
        return self.cards.pop()

class Declaration:
    def __init__(self, result, detail=False):
        self.category = result.category
        self.result = result
        self.score = result.score
        self.value = result.value if detail else None

    def __str__(self):
        if self.value:
            return self.result.score_name(detail=True)
        else:
            return self.result.score_name(detail=False)

    @property
    def all_results(self):
        if self.value:
            return self.result.score_name(detail=True, multiple=True)
        else:
            return self.result.score_name(detail=False, multiple=True)


class Result:
    def __init__(self, player, category, score, value):
        self.category = category
        self.player = player
        self.score = score
        self.value = value

    def __lt__(self, other):
        return (self.score, self.value) < (other.score, other.value)

    def __eq__(self, other):
        return (self.score, self.value) == (other.score, other.value)

    def __repr__(self):
        return 'Result: {} with {}, {}'.format(self.player, self.score, self.value)

    def score_name(self, detail=False, multiple=False):
        POINT_NAMES = {
            'sequences': {
                3: 'tierce',
                4: 'quarte',
                5: 'quinte',
                6: 'sixième',
                7: 'septième',
                8: 'septième'
            },
            'sets': {
                3: 'trio',
                4: 'quatorze'
            }
        }
        detail_name = ''
        if self.category == Category.POINT:
            values = [self.value]
        
        else:
            if multiple:
                values = self.value
            else:
                values = self.value[0:1]

        full_names = []
        for value in values:      
            if self.category == Category.POINT:
                point_name = 'Point of {}'.format(self.score)

            else:
                point_name = POINT_NAMES[self.category][len(value)]

            if detail:
                if self.category == Category.POINT:
                    detail_name = " making {}".format(self.value)
                if self.category == Category.SEQUENCES:
                    if value[0].rank == Rank.Seven:
                        detail_name = ' minor'
                    if value[-1].rank == Rank.Ace:
                        detail_name = ' major'
                    else:
                        detail_name = ' to the {}'.format(value[-1].rank.name)
                if self.category == Category.SETS:
                    detail_name = ' of {}s'.format(value[0].rank.name)
            full_names.append('{}{}'.format(point_name, detail_name))
        return ", ".join(full_names)


class Player:
    def __init__(self, name):
        self.hand = {}
        self.name = name
        self.deal = None

    def __repr__(self):
        return '{}'.format(self.name)

    def reset(self):
        self.hand = {}

    def suits(self):
        return sorted([
               sorted([c for c in self.hand.values() if c.suit == s], key=lambda x:x.rank.value) 
                      for s in Suit.suits], key=len)

    def print_hand(self):
        def print_hash(card):
            if not card:
                return "  "
            PRINTMAP = {
                Rank.Seven: '7',
                Rank.Eight: '8',
                Rank.Nine: '9',
                Rank.Ten: 'T',
                Rank.Jack: 'J',
                Rank.Queen: 'Q',
                Rank.King: 'K',
                Rank.Ace: 'A',
                Suit.DIAMONDS: Suit.DIAMONDS,
                Suit.HEARTS: Suit.HEARTS,
                Suit.SPADES: Suit.SPADES,
                Suit.CLUBS: Suit.CLUBS
            }
            return '{}{}'.format(PRINTMAP[card.rank], PRINTMAP[card.suit])

        all_cards = [print_hash(self.hand.get(card.hash(), "")) for card in self.deal.pool]
        suits = "\n".join([" | ".join(all_cards[n*8:(n*8)+8]) for n in range(0, 4)])

        return suits


    @property
    def carte_blanche(self):
        courts = {Rank.Jack, Rank.Queen, Rank.King}
        return not [card for card in self.hand.values() if card.rank in courts]

    @property
    def point(self):
        """
        A player may declare for point if they have 4 or more cards in one suit.
        Whoever has the longest point wins. If two players have the same value 
        for point, then the player with the highest value point wins.
        """
        suits = self.suits()

        max_length = len(suits[-1])
        
        if max_length < 4:
            return Result(self, Category.POINT, 0, 0)

        point_suits = [suit for suit in suits if len(suit) == max_length]

        point_pips = [sum([PIPS[c.rank] for c in point_suit]) for point_suit in point_suits]
        max_points = max(point_pips)
        point_suit = point_suits[point_pips.index(max_points)]
        point_length = len(point_suit)
    
        return Result(self, Category.POINT, point_length, max_points)

    @property
    def sequences(self):
        suits = self.suits()
        sequences = []
        for suit in suits:
            longest_sequence = []
            suit.sort()
            i = 0
            runner = 1

            while i < len(suit):
                run = [suit[i]]
                while runner < len(suit):
                    card = suit[runner - 1]
                    next_card = suit[runner]
                    if next_card - card == 1:
                        runner = runner + 1
                        run.append(next_card)
                    else:          
                        break

                if len(run) > len(longest_sequence):
                    longest_sequence = run

                i = runner
                runner = i + 1
                
            sequences.append(longest_sequence)

        sequences = sorted([sequence for sequence in sequences if len(sequence) >= 3],
                            key=lambda l: (-len(l), -l[0].rank.value))
        max_length = len(sequences[0]) if sequences else 0
        return Result(self, Category.SEQUENCES, max_length, sequences)

    @property
    def sets(self):
        ELIGIBLE_RANKS = [
            Rank.Ace,
            Rank.King,
            Rank.Queen,
            Rank.Jack,
            Rank.Ten
        ]
        sets = sorted([l for l in 
                       [[c for c in self.hand.values() if c.rank == r] 
                           for r in ELIGIBLE_RANKS] 
                        if len(l) >= 3],
                      key=lambda l: (-len(l), -l[0].rank.value))
        set_class = len(sets[0]) if sets else 0
        return Result(self, Category.SETS, set_class, sets)


class Deal:
    SCORE_VALUES = {
        Category.POINT: {
            4: 4,
            5: 5,
            6: 6,
            7: 7,
            8: 8
        },
        Category.SEQUENCES: {
            3: 3,
            4: 4,
            5: 15,
            6: 16,
            7: 17,
            8: 18
        },
        Category.SETS: {
            3: 3,
            4: 14
        }
    }
    def __init__(self, partie, elder, younger):
        self.partie = partie
        self.pool = all_cards()
        self.deck = Deck(self.pool)
        self.elder = elder
        self.younger = younger
        self.players = {self.elder, self.younger}
        self.score = {self.elder: 0, self.younger: 0}
        self.tricks = {self.elder: 0, self.younger: 0}
        self.discards = {self.elder: [], self.younger: []}
        self.repique = None
        self.pique = None

        elder.deal = self
        younger.deal = self
        self.reset_players()
 
    def reset_players(self):
        for player in self.players:
            player.reset()         

    def deal(self):
        for i in range(12):
            self.elder.draw([self.deck.pop()])
            self.younger.draw([self.deck.pop()])
        for player in self.players:
            if player.carte_blanche:
                self.score[player] += 10
                break

    def exchange(self, player, cards):
        for card in cards:
            del player.hand[card.hash()]
            self.discards[player].append(card)
            player.draw([self.deck.pop()])

    def score_declarations(self):
        for category in (Category.POINT, Category.SEQUENCES, Category.SETS):
            winning_score = max([getattr(player, category) for player in self.players])
            winner = winning_score.player
            if category == Category.POINT:
                self.score[winner] += self.SCORE_VALUES[category][winning_score.score]
            else:
                self.score[winner] += sum([self.SCORE_VALUES[category][len(value)] for value in winning_score.value])
        # Repique
        for player in self.players:
            other_player = (self.players - {player}).pop()
            if self.score[player] >= 30 and self.score[other_player] == 0:
                self.repique = player
                self.score[player] += 60

    def play_trick(self, lead_play, follow_play):
        lead_card = lead_play['card']
        follow_card = follow_play['card']
        lead_player = lead_play['player']
        follow_player = follow_play['player']

        del lead_player.hand[lead_card.hash()]
        del follow_player.hand[follow_card.hash()]

        result = {'caput': None}

        self.score[lead_player] += 1

        if follow_card.suit == lead_card.suit and follow_card.rank.value > lead_card.rank.value:
            self.score[follow_player] += 1
            winner = follow_player
            loser = lead_player
        else:
            winner = lead_player
            loser = follow_player


        self.tricks[winner] += 1
        result['winner'] = winner

        if not self.repique and not self.pique:
            if self.score[winner] >= 30 and self.score[loser] == 0:
                self.score[winner] += 30
                self.pique = winner

        if not lead_player.hand:
            self.score[winner] += 1

            if self.tricks[winner] == 12: # If winner has taken all the tricks
                self.score[winner] += 40
                result['caput'] = winner

            elif self.tricks[winner] != 6: # If winner (and thus both) have taken half the tricks
                most_tricks_player = max(self.tricks.items(), key=lambda x: x[1])
                self.score[most_tricks_player[0]] += 10

            for player in self.players:
                self.partie.score[player] += self.score[player]

        return result

class Partie:
    def __init__(self, player1, player2):
        players = {player1, player2}
        self.players = players
        self.dealer = choice(list(players))
        self.non_dealer = (players - {self.dealer}).pop()
        self.deals = []
        self.score = {player1: 0, player2: 0}
        self.winner = None
        self.final_score = 0

    def new_deal(self):
        if len(self.deals) == 0 or len(self.deals) % 2 == 0:
            d = Deal(self, self.non_dealer, self.dealer)
        elif len(self.deals) % 2 == 1:
            d = Deal(self, self.dealer, self.non_dealer)
        self.deals.append(d)
        return d

    def get_final_score(self):
        self.winner = sorted(list(self.players), key=lambda x:self.score[x])[-1]
        self.loser = (self.players - {self.winner}).pop()
        if self.score[self.loser] >= 100:
            self.final_score = 100 + (self.score[self.winner] - self.score[self.loser]) 
        else:
            self.final_score = 100 + (self.score[self.winner] + self.score[self.loser])

        return self.final_score
        