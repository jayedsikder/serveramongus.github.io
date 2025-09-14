"""
Cognitive Workflow: Integrated Framework Implementation
Combines SRS, Motivation, and Digital Brain systems for deep research and AI-augmented creation

This is the main orchestrator that integrates:
- Spaced Repetition System for knowledge retention
- Motivation Engine for sustained engagement
- Digital Second Brain for knowledge synthesis
"""

import json
import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

from srs_engine import SRSEngine, ReviewQuality, Card
from motivation_engine import MotivationEngine, QuestStatus, RewardType
from digital_brain import DigitalBrain, ContentType, ProcessingStatus

@dataclass
class WorkflowSession:
    """Represents a complete learning session"""
    id: str
    start_time: str
    end_time: str
    duration_minutes: int
    quest_id: str
    cards_reviewed: int
    content_captured: int
    insights_generated: int
    quality_rating: int
    notes: str

class CognitiveWorkflow:
    """
    Main orchestrator for the cognitive workflow system
    """
    
    def __init__(self, data_dir: str = "cognitive_workflow_data"):
        self.data_dir = data_dir
        self.srs = SRSEngine(f"{data_dir}/srs_data.json")
        self.motivation = MotivationEngine(f"{data_dir}/motivation_data.json")
        self.brain = DigitalBrain(f"{data_dir}/digital_brain.json")
        self.sessions: Dict[str, WorkflowSession] = {}
        self.load_sessions()
    
    def load_sessions(self):
        """Load workflow sessions from storage"""
        try:
            with open(f"{self.data_dir}/sessions.json", 'r') as f:
                data = json.load(f)
                self.sessions = {
                    session_id: WorkflowSession(**session_data)
                    for session_id, session_data in data.items()
                }
        except FileNotFoundError:
            self.sessions = {}
    
    def save_sessions(self):
        """Save workflow sessions to storage"""
        data = {session_id: asdict(session) for session_id, session in self.sessions.items()}
        with open(f"{self.data_dir}/sessions.json", 'w') as f:
            json.dump(data, f, indent=2)
    
    def start_learning_session(self, quest_id: str) -> str:
        """Start a new learning session"""
        session_id = f"session_{len(self.sessions) + 1}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.datetime.now()
        
        session = WorkflowSession(
            id=session_id,
            start_time=start_time.isoformat(),
            end_time="",
            duration_minutes=0,
            quest_id=quest_id,
            cards_reviewed=0,
            content_captured=0,
            insights_generated=0,
            quality_rating=0,
            notes=""
        )
        
        self.sessions[session_id] = session
        return session_id
    
    def end_learning_session(self, session_id: str, quality_rating: int, notes: str = "") -> bool:
        """End a learning session and update all systems"""
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        end_time = datetime.datetime.now()
        start_time = datetime.datetime.fromisoformat(session.start_time)
        duration = int((end_time - start_time).total_seconds() / 60)
        
        session.end_time = end_time.isoformat()
        session.duration_minutes = duration
        session.quality_rating = quality_rating
        session.notes = notes
        
        # Update motivation system
        self.motivation.log_learning_session(
            quest_id=session.quest_id,
            duration_minutes=duration,
            quality_rating=quality_rating,
            notes=notes
        )
        
        self.save_sessions()
        return True
    
    def daily_review_workflow(self) -> Dict:
        """Execute the daily review workflow"""
        results = {
            'srs_reviews': 0,
            'quest_updates': 0,
            'content_processed': 0,
            'insights_generated': 0
        }
        
        # 1. Review SRS cards
        due_cards = self.srs.get_due_cards()
        for card in due_cards[:10]:  # Limit to 10 cards per session
            # In a real implementation, this would be interactive
            # For now, simulate a "Good" review
            self.srs.review_card(card.id, ReviewQuality.GOOD)
            results['srs_reviews'] += 1
        
        # 2. Update quest progress
        active_quests = [q for q in self.motivation.quests.values() if q.status == QuestStatus.IN_PROGRESS]
        for quest in active_quests:
            # Simulate progress based on SRS reviews
            if results['srs_reviews'] > 0:
                progress_increment = min(0.1, results['srs_reviews'] * 0.02)
                self.motivation.update_quest_progress(quest.id, quest.progress + progress_increment)
                results['quest_updates'] += 1
        
        # 3. Process captured content
        unprocessed_content = [
            item for item in self.brain.content_items.values() 
            if item.status == ProcessingStatus.CAPTURED
        ]
        for item in unprocessed_content[:5]:  # Process up to 5 items
            self.brain.process_content(item.id)
            results['content_processed'] += 1
        
        # 4. Generate insights
        if len(self.brain.concepts) >= 2:
            concept_ids = list(self.brain.concepts.keys())[:2]
            insight_id = self.brain.generate_insight(concept_ids)
            if insight_id:
                results['insights_generated'] += 1
        
        return results
    
    def capture_and_process_content(self, title: str, content: str, content_type: ContentType,
                                  quest_id: str = None, tags: List[str] = None) -> str:
        """Capture new content and integrate it into the workflow"""
        if tags is None:
            tags = []
        
        # Capture content in digital brain
        content_id = self.brain.capture_content(
            title=title,
            content=content,
            content_type=content_type,
            tags=tags
        )
        
        # Process the content
        self.brain.process_content(content_id)
        
        # Create SRS cards from key concepts
        content_item = self.brain.content_items[content_id]
        for concept in content_item.concepts[:3]:  # Create cards for top 3 concepts
            card_id = self.srs.create_card(
                front=f"What is {concept}?",
                back=f"Concept from: {title}",
                tags=tags + [concept]
            )
        
        # Update quest progress if quest_id provided
        if quest_id and quest_id in self.motivation.quests:
            quest = self.motivation.quests[quest_id]
            if quest.status == QuestStatus.IN_PROGRESS:
                progress_increment = 0.05  # Small increment for content capture
                self.motivation.update_quest_progress(quest_id, quest.progress + progress_increment)
        
        return content_id
    
    def generate_research_insights(self, topic: str) -> List[Dict]:
        """Generate research insights on a specific topic"""
        # Search for relevant content
        search_results = self.brain.search_knowledge(topic)
        
        insights = []
        for result in search_results[:5]:  # Top 5 results
            if result['type'] == 'content':
                content_item = self.brain.content_items[result['id']]
                
                # Generate insight based on content
                insight = {
                    'title': f"Insight from {content_item.title}",
                    'content': content_item.summary or content_item.content[:200] + "...",
                    'concepts': content_item.concepts,
                    'connections': content_item.connections,
                    'ai_insights': content_item.ai_insights,
                    'source': content_item.source_url or "Personal knowledge base"
                }
                insights.append(insight)
        
        return insights
    
    def get_workflow_dashboard(self) -> Dict:
        """Get comprehensive dashboard of the entire workflow"""
        # SRS stats
        srs_stats = self.srs.get_overall_stats()
        
        # Motivation stats
        motivation_dashboard = self.motivation.get_motivation_dashboard()
        
        # Digital brain stats
        brain_stats = self.brain.get_knowledge_graph_stats()
        
        # Session stats
        total_sessions = len(self.sessions)
        total_learning_time = sum(session.duration_minutes for session in self.sessions.values())
        avg_session_quality = sum(session.quality_rating for session in self.sessions.values()) / total_sessions if total_sessions > 0 else 0
        
        return {
            'srs': srs_stats,
            'motivation': motivation_dashboard,
            'digital_brain': brain_stats,
            'sessions': {
                'total_sessions': total_sessions,
                'total_learning_time_hours': total_learning_time / 60,
                'avg_session_quality': avg_session_quality,
                'avg_session_duration': total_learning_time / total_sessions if total_sessions > 0 else 0
            },
            'workflow_health': self._calculate_workflow_health(srs_stats, motivation_dashboard, brain_stats)
        }
    
    def _calculate_workflow_health(self, srs_stats: Dict, motivation_dashboard: Dict, brain_stats: Dict) -> Dict:
        """Calculate overall health of the workflow system"""
        # SRS health (based on success rate and due cards)
        srs_health = srs_stats['overall_success_rate']
        if srs_stats['due_cards'] > 20:
            srs_health *= 0.8  # Penalty for too many due cards
        
        # Motivation health (based on SDT scores)
        motivation_health = motivation_dashboard['sdt_scores']['overall']
        
        # Digital brain health (based on processing and synthesis rates)
        brain_health = (brain_stats['processing_rate'] + brain_stats['synthesis_rate']) / 2
        
        # Overall health
        overall_health = (srs_health + motivation_health + brain_health) / 3
        
        return {
            'srs_health': srs_health,
            'motivation_health': motivation_health,
            'brain_health': brain_health,
            'overall_health': overall_health,
            'recommendations': self._generate_workflow_recommendations(srs_health, motivation_health, brain_health)
        }
    
    def _generate_workflow_recommendations(self, srs_health: float, motivation_health: float, brain_health: float) -> List[str]:
        """Generate recommendations for improving workflow health"""
        recommendations = []
        
        if srs_health < 0.6:
            recommendations.append("Focus on improving SRS success rate - review difficult cards more frequently")
        
        if motivation_health < 0.6:
            recommendations.append("Work on motivation - create more self-directed quests and celebrate achievements")
        
        if brain_health < 0.6:
            recommendations.append("Process more captured content and generate more insights")
        
        if not recommendations:
            recommendations.append("Workflow is healthy - continue current practices")
        
        return recommendations
    
    def export_workflow_data(self, filepath: str):
        """Export all workflow data to a single file"""
        data = {
            'srs_data': {card_id: card.to_dict() for card_id, card in self.srs.cards.items()},
            'motivation_data': {
                'quests': {quest_id: quest.to_dict() for quest_id, quest in self.motivation.quests.items()},
                'achievements': {ach_id: ach.to_dict() for ach_id, ach in self.motivation.achievements.items()},
                'sessions': {session_id: session.to_dict() for session_id, session in self.motivation.sessions.items()}
            },
            'brain_data': {
                'content_items': {item_id: item.to_dict() for item_id, item in self.brain.content_items.items()},
                'concepts': {concept_id: concept.to_dict() for concept_id, concept in self.brain.concepts.items()},
                'insights': {insight_id: insight.to_dict() for insight_id, insight in self.brain.insights.items()}
            },
            'workflow_sessions': {session_id: asdict(session) for session_id, session in self.sessions.items()},
            'export_date': datetime.datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)

# Example usage and testing
if __name__ == "__main__":
    # Initialize the cognitive workflow
    workflow = CognitiveWorkflow()
    
    # Create a learning quest
    quest_id = workflow.motivation.create_quest(
        title="Master Cognitive Science",
        description="Learn about memory, motivation, and knowledge management",
        category="learning",
        difficulty=4,
        tags=["cognitive-science", "learning", "research"]
    )
    
    # Start the quest
    workflow.motivation.start_quest(quest_id)
    
    # Capture some content
    content_id = workflow.capture_and_process_content(
        title="Memory and Learning",
        content="The Ebbinghaus forgetting curve demonstrates that memory decays exponentially over time. Spaced repetition is the systematic application of the spacing effect to counteract this decay.",
        content_type=ContentType.ARTICLE,
        quest_id=quest_id,
        tags=["memory", "learning", "psychology"]
    )
    
    # Start a learning session
    session_id = workflow.start_learning_session(quest_id)
    
    # Simulate some learning activity
    workflow.srs.create_card(
        front="What is the Ebbinghaus forgetting curve?",
        back="The exponential decay of memory over time without reinforcement",
        tags=["memory", "psychology"]
    )
    
    # End the session
    workflow.end_learning_session(session_id, quality_rating=4, notes="Good progress on memory concepts")
    
    # Run daily review
    daily_results = workflow.daily_review_workflow()
    print(f"Daily review results: {daily_results}")
    
    # Get workflow dashboard
    dashboard = workflow.get_workflow_dashboard()
    print(f"Workflow Health: {dashboard['workflow_health']['overall_health']:.2f}")
    print(f"Recommendations: {dashboard['workflow_health']['recommendations']}")
    
    # Generate research insights
    insights = workflow.generate_research_insights("memory")
    print(f"Generated {len(insights)} insights on memory")