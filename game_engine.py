from card import Card
from agent import SimpleHeartsAgent

import random


class HeartsEngine:
    NUM_AGENTS = 4
    JACK_OF_SPADES = Card(Card.Suit.SPADES, 11)
    CARDS_PER_AGENT = Card.NUM_CARDS // NUM_AGENTS

    def __init__(self, agent_gen_fns):
        self.agents_points = [0 for _ in range(self.NUM_AGENTS)]
        assert len(agent_gen_fns) == self.NUM_AGENTS
        self.agent_gen_fns = agent_gen_fns

    @classmethod
    def create(cls):
        return cls.createWithOneCustomAgent(lambda agent_id, cards: SimpleHeartsAgent(
            agent_id, cards))

    @classmethod
    def createWithOneCustomAgent(cls, custom_agent_gen_fn):
        agent_gen_fns = [lambda agent_id, cards: SimpleHeartsAgent(
            agent_id, cards) for _ in range(cls.NUM_AGENTS - 1)]
        agent_gen_fns.append(custom_agent_gen_fn)
        return HeartsEngine(agent_gen_fns)

    def deal(self):
        print("deal")
        cards = [Card.createFromCardIdx(i) for i in range(Card.NUM_CARDS)]
        random.shuffle(cards)
        assert len(cards) % self.NUM_AGENTS == 0
        self.agents = [self.agent_gen_fns[i](i,
                                             cards[i * self.CARDS_PER_AGENT:(i + 1) * self.CARDS_PER_AGENT]) for i in range(self.NUM_AGENTS)]

    """
    @returns winner agent_id of trick
    """

    def trick(self, start_agent_id):
        print(f"Starting agent: {start_agent_id}, Points: {self.agents_points}")
        in_trick = []  # (agent_id, Card)
        for offset in range(self.NUM_AGENTS):
            curr_agent_id = (start_agent_id + offset) % self.NUM_AGENTS
            agent = self.agents[curr_agent_id]
            card = agent.getNextAction()
            in_trick.append((curr_agent_id, card))
            # notify all agents of a move
            for notified_agent in self.agents:
                notified_agent.observeActionTaken(agent.agent_id, card)
        # update points based on winner of trick (ignores the rule reset rule when player takes all 8 hearts and the jack of spades, for sake of reduced complexity)
        winner_agent_id = self._determine_trick_winner(in_trick)
        won_points = 0
        won_points += sum(
            card.suit == Card.Suit.HEARTS for _, card in in_trick)
        if self.JACK_OF_SPADES in map(lambda ac: ac[1], in_trick):
            won_points += 8
        print(
            f"Agent {winner_agent_id} won the trick and received {won_points} points")
        self.agents_points[winner_agent_id] += won_points
        return winner_agent_id

    # @returns leaderboard: sorted (points, agent_id)
    def play(self, win_points):
        start_agent_id = 0
        while True:
            self.deal()
            num_tricks_per_round = Card.NUM_CARDS // self.NUM_AGENTS
            for i in range(num_tricks_per_round):
                print(f"\033[1mCalling trick for the {i+1}th time\033[0m")
                start_agent_id = self.trick(start_agent_id)
                if any(map(lambda points: points >= win_points, self.agents_points)):
                    leaderboard = sorted(
                        [(points, i) for i, points in enumerate(self.agents_points)])
                    for notified_agent in self.agents:
                        notified_agent.resetSeenCards()
                    return leaderboard

    @staticmethod
    def _determine_trick_winner(in_trick):
        leading_suit = in_trick[0][1].suit
        _, winner_agent_id = sorted(map(lambda agent_id_card: (
            agent_id_card[1].num if agent_id_card[1].suit == leading_suit else float("-inf"), agent_id_card[0]), in_trick))[-1]
        return winner_agent_id


if __name__ == '__main__':
    engine = HeartsEngine.create()
    engine.play(50)
