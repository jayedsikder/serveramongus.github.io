"""
Digital Second Brain: Capture-to-Concept Pipeline
Based on the framework outlined in
"The Cognitive Workflow: An Integrated Framework for Deep Research, Idea Generation, and AI-Augmented Creation"

This implementation provides:
- Centralized knowledge repository
- Capture-to-concept workflow
- Knowledge graph construction
- AI-augmented synthesis and insight generation
"""

import json
import datetime
import hashlib
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import re

class ContentType(Enum):
    """Types of content that can be captured"""
    ARTICLE = "article"
    PAPER = "paper"
    VIDEO = "video"
    PODCAST = "podcast"
    BOOK = "book"
    NOTE = "note"
    IDEA = "idea"
    QUOTE = "quote"
    IMAGE = "image"
    AUDIO = "audio"

class ProcessingStatus(Enum):
    """Status of content processing"""
    CAPTURED = "captured"  # Raw content captured
    PROCESSED = "processed"  # Extracted and structured
    SYNTHESIZED = "synthesized"  # Connected to knowledge graph
    INSIGHT = "insight"  # Generated novel insights

@dataclass
class ContentItem:
    """Represents a piece of captured content"""
    id: str
    title: str
    content: str
    content_type: ContentType
    source_url: Optional[str]
    author: Optional[str]
    created_date: str
    processed_date: Optional[str]
    status: ProcessingStatus
    tags: List[str]
    concepts: List[str]  # Extracted concepts
    connections: List[str]  # IDs of related content
    summary: Optional[str]
    key_quotes: List[str]
    personal_notes: str
    ai_insights: List[str]
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict):
        # Convert string back to enum
        data['content_type'] = ContentType(data['content_type'])
        data['status'] = ProcessingStatus(data['status'])
        return cls(**data)

@dataclass
class Concept:
    """Represents a concept in the knowledge graph"""
    id: str
    name: str
    definition: str
    aliases: List[str]
    related_concepts: List[str]
    content_items: List[str]  # IDs of content that mention this concept
    created_date: str
    last_updated: str
    confidence_score: float  # 0.0 to 1.0
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(**data)

@dataclass
class Insight:
    """Represents a generated insight or connection"""
    id: str
    title: str
    description: str
    source_concepts: List[str]
    source_content: List[str]
    confidence: float
    created_date: str
    insight_type: str  # "connection", "pattern", "contradiction", "synthesis"
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(**data)

class DigitalBrain:
    """
    Core digital second brain implementation
    """
    
    def __init__(self, data_file: str = "digital_brain.json"):
        self.data_file = data_file
        self.content_items: Dict[str, ContentItem] = {}
        self.concepts: Dict[str, Concept] = {}
        self.insights: Dict[str, Insight] = {}
        self.load_data()
    
    def load_data(self):
        """Load digital brain data from persistent storage"""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                self.content_items = {
                    item_id: ContentItem.from_dict(item_data) 
                    for item_id, item_data in data.get('content_items', {}).items()
                }
                self.concepts = {
                    concept_id: Concept.from_dict(concept_data) 
                    for concept_id, concept_data in data.get('concepts', {}).items()
                }
                self.insights = {
                    insight_id: Insight.from_dict(insight_data) 
                    for insight_id, insight_data in data.get('insights', {}).items()
                }
        except FileNotFoundError:
            self.content_items = {}
            self.concepts = {}
            self.insights = {}
    
    def save_data(self):
        """Save digital brain data to persistent storage"""
        data = {
            'content_items': {item_id: item.to_dict() for item_id, item in self.content_items.items()},
            'concepts': {concept_id: concept.to_dict() for concept_id, concept in self.concepts.items()},
            'insights': {insight_id: insight.to_dict() for insight_id, insight in self.insights.items()}
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def capture_content(self, title: str, content: str, content_type: ContentType,
                      source_url: Optional[str] = None, author: Optional[str] = None,
                      tags: List[str] = None, personal_notes: str = "") -> str:
        """Capture new content into the digital brain"""
        if tags is None:
            tags = []
        
        # Generate unique ID based on content hash
        content_hash = hashlib.md5(f"{title}{content}".encode()).hexdigest()[:12]
        item_id = f"{content_type.value}_{content_hash}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        now = datetime.datetime.now().isoformat()
        
        content_item = ContentItem(
            id=item_id,
            title=title,
            content=content,
            content_type=content_type,
            source_url=source_url,
            author=author,
            created_date=now,
            processed_date=None,
            status=ProcessingStatus.CAPTURED,
            tags=tags,
            concepts=[],
            connections=[],
            summary=None,
            key_quotes=[],
            personal_notes=personal_notes,
            ai_insights=[]
        )
        
        self.content_items[item_id] = content_item
        self.save_data()
        return item_id
    
    def process_content(self, item_id: str) -> bool:
        """Process captured content to extract concepts and structure"""
        if item_id not in self.content_items:
            return False
        
        item = self.content_items[item_id]
        
        # Extract key quotes (simple implementation)
        quotes = self._extract_quotes(item.content)
        item.key_quotes = quotes
        
        # Generate summary (simple implementation)
        summary = self._generate_summary(item.content)
        item.summary = summary
        
        # Extract concepts
        concepts = self._extract_concepts(item.content)
        item.concepts = concepts
        
        # Update status
        item.status = ProcessingStatus.PROCESSED
        item.processed_date = datetime.datetime.now().isoformat()
        
        # Create or update concept entries
        for concept_name in concepts:
            self._create_or_update_concept(concept_name, item_id)
        
        self.save_data()
        return True
    
    def _extract_quotes(self, content: str) -> List[str]:
        """Extract key quotes from content (simple implementation)"""
        # Look for sentences with quotes or important keywords
        sentences = re.split(r'[.!?]+', content)
        quotes = []
        
        important_keywords = ['important', 'key', 'crucial', 'essential', 'fundamental', 'critical']
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and len(sentence) < 200:
                if any(keyword in sentence.lower() for keyword in important_keywords):
                    quotes.append(sentence)
        
        return quotes[:5]  # Return top 5 quotes
    
    def _generate_summary(self, content: str) -> str:
        """Generate a summary of the content (simple implementation)"""
        sentences = re.split(r'[.!?]+', content)
        # Take first few sentences as summary
        summary_sentences = sentences[:3]
        return '. '.join(sentence.strip() for sentence in summary_sentences if sentence.strip()) + '.'
    
    def _extract_concepts(self, content: str) -> List[str]:
        """Extract concepts from content (simple implementation)"""
        # Simple keyword extraction - in a real implementation, this would use NLP
        words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)
        
        # Filter out common words and short terms
        stop_words = {'The', 'This', 'That', 'These', 'Those', 'A', 'An', 'And', 'Or', 'But', 'In', 'On', 'At', 'To', 'For', 'Of', 'With', 'By'}
        concepts = [word for word in words if len(word) > 3 and word not in stop_words]
        
        # If no capitalized words found, try simple word extraction
        if not concepts:
            # Extract words that might be concepts (longer words, not common words)
            all_words = re.findall(r'\b[a-zA-Z]+\b', content.lower())
            common_words = {'the', 'this', 'that', 'these', 'those', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must', 'about', 'from', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'up', 'down', 'out', 'off', 'over', 'under', 'again', 'further', 'then', 'once'}
            concepts = [word.title() for word in all_words if len(word) > 4 and word not in common_words]
        
        # Return unique concepts, limited to 10
        return list(set(concepts))[:10]
    
    def _create_or_update_concept(self, concept_name: str, content_item_id: str):
        """Create or update a concept in the knowledge graph"""
        concept_id = concept_name.lower().replace(' ', '_')
        
        if concept_id in self.concepts:
            # Update existing concept
            concept = self.concepts[concept_id]
            if content_item_id not in concept.content_items:
                concept.content_items.append(content_item_id)
        else:
            # Create new concept
            now = datetime.datetime.now().isoformat()
            concept = Concept(
                id=concept_id,
                name=concept_name,
                definition="",  # Would be filled by AI in real implementation
                aliases=[],
                related_concepts=[],
                content_items=[content_item_id],
                created_date=now,
                last_updated=now,
                confidence_score=0.5
            )
            self.concepts[concept_id] = concept
    
    def synthesize_content(self, item_id: str) -> bool:
        """Synthesize content by finding connections and generating insights"""
        if item_id not in self.content_items:
            return False
        
        item = self.content_items[item_id]
        
        # Find related content based on shared concepts
        related_items = self._find_related_content(item)
        item.connections = [related_id for related_id, _ in related_items]
        
        # Generate AI insights (simplified)
        insights = self._generate_insights(item, related_items)
        item.ai_insights = insights
        
        # Update status
        item.status = ProcessingStatus.SYNTHESIZED
        
        self.save_data()
        return True
    
    def _find_related_content(self, item: ContentItem) -> List[Tuple[str, float]]:
        """Find content related to the given item based on concept overlap"""
        related_items = []
        
        for other_id, other_item in self.content_items.items():
            if other_id == item.id:
                continue
            
            # Calculate concept overlap
            item_concepts = set(item.concepts)
            other_concepts = set(other_item.concepts)
            
            if item_concepts and other_concepts:
                overlap = len(item_concepts.intersection(other_concepts))
                total_concepts = len(item_concepts.union(other_concepts))
                similarity = overlap / total_concepts if total_concepts > 0 else 0
                
                if similarity > 0.1:  # Threshold for relatedness
                    related_items.append((other_id, similarity))
        
        # Sort by similarity and return top 5
        return sorted(related_items, key=lambda x: x[1], reverse=True)[:5]
    
    def _generate_insights(self, item: ContentItem, related_items: List[Tuple[str, float]]) -> List[str]:
        """Generate insights based on content and its relationships (simplified)"""
        insights = []
        
        if len(related_items) > 0:
            insights.append(f"This content connects to {len(related_items)} other items in your knowledge base")
        
        if len(item.concepts) > 3:
            insights.append(f"Key concepts identified: {', '.join(item.concepts[:3])}")
        
        if item.content_type == ContentType.PAPER:
            insights.append("This appears to be academic content - consider adding to your research collection")
        
        return insights
    
    def generate_insight(self, concept_ids: List[str]) -> Optional[str]:
        """Generate a new insight by connecting multiple concepts"""
        if len(concept_ids) < 2:
            return None
        
        # Find content that contains these concepts
        relevant_content = []
        for concept_id in concept_ids:
            if concept_id in self.concepts:
                concept = self.concepts[concept_id]
                relevant_content.extend(concept.content_items)
        
        if not relevant_content:
            return None
        
        # Generate insight ID
        insight_id = f"insight_{len(self.insights) + 1}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create insight
        insight = Insight(
            id=insight_id,
            title=f"Connection between {len(concept_ids)} concepts",
            description=f"These concepts appear together in {len(set(relevant_content))} content items",
            source_concepts=concept_ids,
            source_content=list(set(relevant_content)),
            confidence=0.7,  # Would be calculated by AI in real implementation
            created_date=datetime.datetime.now().isoformat(),
            insight_type="connection"
        )
        
        self.insights[insight_id] = insight
        self.save_data()
        return insight_id
    
    def search_knowledge(self, query: str, content_types: List[ContentType] = None) -> List[Dict]:
        """Search across all content and concepts"""
        if content_types is None:
            content_types = list(ContentType)
        
        results = []
        query_lower = query.lower()
        
        # Search content items
        for item in self.content_items.values():
            if item.content_type not in content_types:
                continue
            
            score = 0
            if query_lower in item.title.lower():
                score += 3
            if query_lower in item.content.lower():
                score += 1
            if query_lower in item.summary.lower() if item.summary else False:
                score += 2
            
            if score > 0:
                results.append({
                    'type': 'content',
                    'id': item.id,
                    'title': item.title,
                    'summary': item.summary,
                    'score': score,
                    'content_type': item.content_type.value
                })
        
        # Search concepts
        for concept in self.concepts.values():
            if query_lower in concept.name.lower() or query_lower in concept.definition.lower():
                results.append({
                    'type': 'concept',
                    'id': concept.id,
                    'name': concept.name,
                    'definition': concept.definition,
                    'score': 2,
                    'content_type': 'concept'
                })
        
        # Sort by score and return
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def get_knowledge_graph_stats(self) -> Dict:
        """Get statistics about the knowledge graph"""
        total_content = len(self.content_items)
        processed_content = len([item for item in self.content_items.values() if item.status != ProcessingStatus.CAPTURED])
        synthesized_content = len([item for item in self.content_items.values() if item.status == ProcessingStatus.SYNTHESIZED])
        
        total_concepts = len(self.concepts)
        total_insights = len(self.insights)
        
        # Content type distribution
        content_type_dist = {}
        for item in self.content_items.values():
            content_type_dist[item.content_type.value] = content_type_dist.get(item.content_type.value, 0) + 1
        
        return {
            'total_content': total_content,
            'processed_content': processed_content,
            'synthesized_content': synthesized_content,
            'total_concepts': total_concepts,
            'total_insights': total_insights,
            'content_type_distribution': content_type_dist,
            'processing_rate': processed_content / total_content if total_content > 0 else 0,
            'synthesis_rate': synthesized_content / total_content if total_content > 0 else 0
        }
    
    def get_concept_network(self, concept_id: str) -> Dict:
        """Get the network of concepts related to a specific concept"""
        if concept_id not in self.concepts:
            return {}
        
        concept = self.concepts[concept_id]
        
        # Find related concepts through shared content
        related_concepts = {}
        for content_id in concept.content_items:
            if content_id in self.content_items:
                content_item = self.content_items[content_id]
                for other_concept in content_item.concepts:
                    if other_concept != concept.name:
                        related_concepts[other_concept] = related_concepts.get(other_concept, 0) + 1
        
        return {
            'concept': concept.to_dict(),
            'related_concepts': related_concepts,
            'content_items': concept.content_items
        }

# Example usage and testing
if __name__ == "__main__":
    # Initialize the digital brain
    brain = DigitalBrain()
    
    # Capture some example content
    content1 = brain.capture_content(
        title="The Science of Memory",
        content="Memory is not a single system but a collection of different systems. The Ebbinghaus forgetting curve shows that memory decays exponentially over time without reinforcement. Spaced repetition is the systematic application of the spacing effect to counteract this decay.",
        content_type=ContentType.ARTICLE,
        author="Cognitive Science Research",
        tags=["memory", "learning", "psychology"]
    )
    
    content2 = brain.capture_content(
        title="Motivation and Learning",
        content="Self-Determination Theory identifies three core psychological needs: autonomy, competence, and relatedness. When these needs are met, individuals experience intrinsic motivation and sustained engagement in learning activities.",
        content_type=ContentType.PAPER,
        author="Deci & Ryan",
        tags=["motivation", "psychology", "learning"]
    )
    
    # Process the content
    brain.process_content(content1)
    brain.process_content(content2)
    
    # Synthesize the content
    brain.synthesize_content(content1)
    brain.synthesize_content(content2)
    
    # Search for knowledge
    search_results = brain.search_knowledge("memory")
    print(f"Search results for 'memory': {len(search_results)} items found")
    
    # Get knowledge graph stats
    stats = brain.get_knowledge_graph_stats()
    print(f"Knowledge Graph Stats: {stats}")
    
    # Generate an insight
    concept_ids = list(brain.concepts.keys())[:2]
    if concept_ids:
        insight_id = brain.generate_insight(concept_ids)
        print(f"Generated insight: {insight_id}")