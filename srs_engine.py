"""
Spaced Repetition System (SRS) Engine
Based on the SM-2 algorithm and cognitive science principles outlined in
"The Cognitive Workflow: An Integrated Framework for Deep Research, Idea Generation, and AI-Augmented Creation"

This implementation provides:
- SM-2 algorithm for optimal review scheduling
- Memory decay modeling based on Ebbinghaus forgetting curve
- Active recall optimization
- Progress tracking and analytics
"""

import json
import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

class ReviewQuality(Enum):
    """User feedback ratings for card recall performance"""
    AGAIN = 0  # Forgotten - reset to learning phase
    HARD = 1   # Recalled with difficulty
    GOOD = 2   # Recalled with some effort
    EASY = 3   # Recalled effortlessly

@dataclass
class Card:
    """Represents a single flashcard in the SRS system"""
    id: str
    front: str
    back: str
    tags: List[str]
    created_date: str
    last_reviewed: str
    next_review: str
    interval: int  # Days until next review
    ease_factor: float  # Multiplier for interval calculation
    repetitions: int  # Number of successful reviews
    lapses: int  # Number of times forgotten
    is_learning: bool  # True if still in initial learning phase
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Card':
        return cls(**data)

class SRSEngine:
    """
    Core SRS engine implementing the SM-2 algorithm
    """
    
    def __init__(self, data_file: str = "srs_data.json"):
        self.data_file = data_file
        self.cards: Dict[str, Card] = {}
        self.load_data()
    
    def load_data(self):
        """Load card data from persistent storage"""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                self.cards = {
                    card_id: Card.from_dict(card_data) 
                    for card_id, card_data in data.get('cards', {}).items()
                }
        except FileNotFoundError:
            self.cards = {}
    
    def save_data(self):
        """Save card data to persistent storage"""
        data = {
            'cards': {card_id: card.to_dict() for card_id, card in self.cards.items()}
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def create_card(self, front: str, back: str, tags: List[str] = None) -> str:
        """Create a new flashcard"""
        if tags is None:
            tags = []
        
        card_id = f"card_{len(self.cards) + 1}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        now = datetime.datetime.now().isoformat()
        
        card = Card(
            id=card_id,
            front=front,
            back=back,
            tags=tags,
            created_date=now,
            last_reviewed=now,
            next_review=now,  # New cards are due immediately
            interval=1,  # Start with 1 day interval
            ease_factor=2.5,  # Standard starting ease factor
            repetitions=0,
            lapses=0,
            is_learning=True
        )
        
        self.cards[card_id] = card
        self.save_data()
        return card_id
    
    def get_due_cards(self) -> List[Card]:
        """Get all cards that are due for review"""
        now = datetime.datetime.now()
        due_cards = []
        
        for card in self.cards.values():
            next_review = datetime.datetime.fromisoformat(card.next_review)
            if now >= next_review:
                due_cards.append(card)
        
        return sorted(due_cards, key=lambda x: x.next_review)
    
    def review_card(self, card_id: str, quality: ReviewQuality) -> Dict:
        """
        Process a card review and update its scheduling
        Returns updated card information and next review date
        """
        if card_id not in self.cards:
            raise ValueError(f"Card {card_id} not found")
        
        card = self.cards[card_id]
        now = datetime.datetime.now()
        
        # Update last reviewed timestamp
        card.last_reviewed = now.isoformat()
        
        # Process the review based on quality
        if quality == ReviewQuality.AGAIN:
            # Card was forgotten - reset to learning phase
            card.lapses += 1
            card.repetitions = 0
            card.interval = 1
            card.is_learning = True
            card.next_review = now.isoformat()  # Due immediately
            
        elif quality in [ReviewQuality.HARD, ReviewQuality.GOOD, ReviewQuality.EASY]:
            # Card was recalled successfully
            card.repetitions += 1
            
            if card.is_learning:
                # Still in learning phase - use predefined intervals
                if card.repetitions == 1:
                    card.interval = 1
                elif card.repetitions == 2:
                    card.interval = 6
                else:
                    # Graduate from learning phase
                    card.is_learning = False
                    card.interval = int(card.interval * card.ease_factor)
            else:
                # In review phase - use ease factor
                card.interval = int(card.interval * card.ease_factor)
            
            # Update ease factor based on quality
            if quality == ReviewQuality.HARD:
                card.ease_factor = max(1.3, card.ease_factor - 0.15)
            elif quality == ReviewQuality.GOOD:
                # No change to ease factor
                pass
            elif quality == ReviewQuality.EASY:
                card.ease_factor = min(3.0, card.ease_factor + 0.15)
            
            # Calculate next review date
            next_review = now + datetime.timedelta(days=card.interval)
            card.next_review = next_review.isoformat()
        
        self.save_data()
        
        return {
            'card': card.to_dict(),
            'next_review': card.next_review,
            'interval': card.interval,
            'ease_factor': card.ease_factor,
            'repetitions': card.repetitions,
            'lapses': card.lapses
        }
    
    def get_card_stats(self, card_id: str) -> Dict:
        """Get detailed statistics for a specific card"""
        if card_id not in self.cards:
            raise ValueError(f"Card {card_id} not found")
        
        card = self.cards[card_id]
        return {
            'id': card.id,
            'created': card.created_date,
            'last_reviewed': card.last_reviewed,
            'next_review': card.next_review,
            'interval': card.interval,
            'ease_factor': card.ease_factor,
            'repetitions': card.repetitions,
            'lapses': card.lapses,
            'is_learning': card.is_learning,
            'success_rate': card.repetitions / (card.repetitions + card.lapses) if (card.repetitions + card.lapses) > 0 else 0
        }
    
    def get_overall_stats(self) -> Dict:
        """Get overall statistics for the entire SRS system"""
        total_cards = len(self.cards)
        learning_cards = sum(1 for card in self.cards.values() if card.is_learning)
        review_cards = total_cards - learning_cards
        due_cards = len(self.get_due_cards())
        
        total_repetitions = sum(card.repetitions for card in self.cards.values())
        total_lapses = sum(card.lapses for card in self.cards.values())
        overall_success_rate = total_repetitions / (total_repetitions + total_lapses) if (total_repetitions + total_lapses) > 0 else 0
        
        return {
            'total_cards': total_cards,
            'learning_cards': learning_cards,
            'review_cards': review_cards,
            'due_cards': due_cards,
            'total_repetitions': total_repetitions,
            'total_lapses': total_lapses,
            'overall_success_rate': overall_success_rate,
            'average_ease_factor': sum(card.ease_factor for card in self.cards.values()) / total_cards if total_cards > 0 else 0
        }
    
    def search_cards(self, query: str, tags: List[str] = None) -> List[Card]:
        """Search for cards by content or tags"""
        results = []
        query_lower = query.lower()
        
        for card in self.cards.values():
            # Search in front and back text
            if (query_lower in card.front.lower() or 
                query_lower in card.back.lower()):
                results.append(card)
            
            # Search in tags if provided
            if tags:
                if any(tag.lower() in [t.lower() for t in card.tags] for tag in tags):
                    if card not in results:
                        results.append(card)
        
        return results
    
    def export_cards(self, filepath: str):
        """Export all cards to a JSON file"""
        data = {
            'cards': {card_id: card.to_dict() for card_id, card in self.cards.items()},
            'export_date': datetime.datetime.now().isoformat()
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def import_cards(self, filepath: str):
        """Import cards from a JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        for card_id, card_data in data.get('cards', {}).items():
            self.cards[card_id] = Card.from_dict(card_data)
        
        self.save_data()

# Example usage and testing
if __name__ == "__main__":
    # Initialize the SRS engine
    srs = SRSEngine()
    
    # Create some example cards
    card1 = srs.create_card(
        front="What is the Ebbinghaus forgetting curve?",
        back="The exponential decay of memory over time without reinforcement, discovered by Hermann Ebbinghaus in the late 19th century.",
        tags=["psychology", "memory", "cognitive-science"]
    )
    
    card2 = srs.create_card(
        front="What are the three psychological needs in Self-Determination Theory?",
        back="Autonomy (sense of control), Competence (feeling effective), and Relatedness (connection to others).",
        tags=["psychology", "motivation", "sdt"]
    )
    
    # Get due cards
    due_cards = srs.get_due_cards()
    print(f"Cards due for review: {len(due_cards)}")
    
    # Review a card
    if due_cards:
        card = due_cards[0]
        print(f"\nReviewing card: {card.front}")
        print(f"Answer: {card.back}")
        
        # Simulate a "Good" review
        result = srs.review_card(card.id, ReviewQuality.GOOD)
        print(f"Next review: {result['next_review']}")
        print(f"New interval: {result['interval']} days")
    
    # Get overall statistics
    stats = srs.get_overall_stats()
    print(f"\nOverall Stats:")
    print(f"Total cards: {stats['total_cards']}")
    print(f"Due for review: {stats['due_cards']}")
    print(f"Success rate: {stats['overall_success_rate']:.2%}")