"""
Motivation Engine for Sustained Learning
Based on Self-Determination Theory (SDT) principles outlined in
"The Cognitive Workflow: An Integrated Framework for Deep Research, Idea Generation, and AI-Augmented Creation"

This implementation provides:
- SDT-based motivation tracking (Autonomy, Competence, Relatedness)
- Gamification mechanics for learning
- Progress visualization and goal setting
- Habit formation support
"""

import json
import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

class QuestStatus(Enum):
    """Status of learning quests/missions"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"

class RewardType(Enum):
    """Types of rewards for motivation"""
    INTRINSIC = "intrinsic"  # Internal satisfaction, mastery
    EXTRINSIC = "extrinsic"  # External rewards, points, badges

@dataclass
class Quest:
    """Represents a learning quest or mission"""
    id: str
    title: str
    description: str
    category: str  # e.g., "research", "programming", "language"
    status: QuestStatus
    created_date: str
    target_date: Optional[str]
    completed_date: Optional[str]
    progress: float  # 0.0 to 1.0
    difficulty: int  # 1-5 scale
    tags: List[str]
    parent_quest_id: Optional[str]  # For sub-quests
    reward_description: str
    reward_type: RewardType
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Quest':
        # Convert string back to enum
        data['status'] = QuestStatus(data['status'])
        data['reward_type'] = RewardType(data['reward_type'])
        return cls(**data)

@dataclass
class Achievement:
    """Represents an achievement or badge"""
    id: str
    name: str
    description: str
    icon: str  # Emoji or symbol
    unlocked_date: Optional[str]
    category: str
    rarity: str  # "common", "rare", "epic", "legendary"
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Achievement':
        return cls(**data)

@dataclass
class LearningSession:
    """Represents a single learning session"""
    id: str
    quest_id: str
    start_time: str
    end_time: str
    duration_minutes: int
    quality_rating: int  # 1-5 scale
    notes: str
    skills_practiced: List[str]
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'LearningSession':
        return cls(**data)

class MotivationEngine:
    """
    Core motivation engine implementing SDT principles
    """
    
    def __init__(self, data_file: str = "motivation_data.json"):
        self.data_file = data_file
        self.quests: Dict[str, Quest] = {}
        self.achievements: Dict[str, Achievement] = {}
        self.sessions: Dict[str, LearningSession] = {}
        self.streak_data: Dict[str, int] = {}  # Daily streak tracking
        self.load_data()
        self._initialize_default_achievements()
    
    def load_data(self):
        """Load motivation data from persistent storage"""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                self.quests = {
                    quest_id: Quest.from_dict(quest_data) 
                    for quest_id, quest_data in data.get('quests', {}).items()
                }
                self.achievements = {
                    ach_id: Achievement.from_dict(ach_data) 
                    for ach_id, ach_data in data.get('achievements', {}).items()
                }
                self.sessions = {
                    session_id: LearningSession.from_dict(session_data) 
                    for session_id, session_data in data.get('sessions', {}).items()
                }
                self.streak_data = data.get('streak_data', {})
        except FileNotFoundError:
            self.quests = {}
            self.achievements = {}
            self.sessions = {}
            self.streak_data = {}
    
    def save_data(self):
        """Save motivation data to persistent storage"""
        data = {
            'quests': {quest_id: quest.to_dict() for quest_id, quest in self.quests.items()},
            'achievements': {ach_id: ach.to_dict() for ach_id, ach in self.achievements.items()},
            'sessions': {session_id: session.to_dict() for session_id, session in self.sessions.items()},
            'streak_data': self.streak_data
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _initialize_default_achievements(self):
        """Initialize default achievement system"""
        if not self.achievements:
            default_achievements = [
                Achievement("first_quest", "First Steps", "Complete your first learning quest", "🎯", None, "milestone", "common"),
                Achievement("week_streak", "Week Warrior", "Maintain a 7-day learning streak", "🔥", None, "consistency", "rare"),
                Achievement("month_streak", "Monthly Master", "Maintain a 30-day learning streak", "💎", None, "consistency", "epic"),
                Achievement("quest_master", "Quest Master", "Complete 10 quests", "🏆", None, "completion", "rare"),
                Achievement("deep_diver", "Deep Diver", "Complete a quest with 5+ difficulty", "⚡", None, "challenge", "epic"),
                Achievement("autonomy_seeker", "Autonomy Seeker", "Create and complete 5 self-defined quests", "🎨", None, "autonomy", "rare"),
                Achievement("competence_builder", "Competence Builder", "Achieve 80%+ success rate on 5 quests", "📈", None, "competence", "rare"),
                Achievement("community_connector", "Community Connector", "Share 3 achievements with others", "🤝", None, "relatedness", "common"),
            ]
            
            for achievement in default_achievements:
                self.achievements[achievement.id] = achievement
    
    def create_quest(self, title: str, description: str, category: str, 
                    difficulty: int = 3, target_date: Optional[str] = None,
                    parent_quest_id: Optional[str] = None, tags: List[str] = None,
                    reward_description: str = "Sense of mastery and accomplishment",
                    reward_type: RewardType = RewardType.INTRINSIC) -> str:
        """Create a new learning quest"""
        if tags is None:
            tags = []
        
        quest_id = f"quest_{len(self.quests) + 1}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        now = datetime.datetime.now().isoformat()
        
        quest = Quest(
            id=quest_id,
            title=title,
            description=description,
            category=category,
            status=QuestStatus.NOT_STARTED,
            created_date=now,
            target_date=target_date,
            completed_date=None,
            progress=0.0,
            difficulty=difficulty,
            tags=tags,
            parent_quest_id=parent_quest_id,
            reward_description=reward_description,
            reward_type=reward_type
        )
        
        self.quests[quest_id] = quest
        self.save_data()
        return quest_id
    
    def start_quest(self, quest_id: str) -> bool:
        """Start a quest (change status to in_progress)"""
        if quest_id not in self.quests:
            return False
        
        quest = self.quests[quest_id]
        if quest.status == QuestStatus.NOT_STARTED:
            quest.status = QuestStatus.IN_PROGRESS
            self.save_data()
            return True
        return False
    
    def update_quest_progress(self, quest_id: str, progress: float) -> bool:
        """Update quest progress (0.0 to 1.0)"""
        if quest_id not in self.quests:
            return False
        
        quest = self.quests[quest_id]
        quest.progress = max(0.0, min(1.0, progress))
        
        # Auto-complete if progress reaches 100%
        if quest.progress >= 1.0 and quest.status == QuestStatus.IN_PROGRESS:
            self.complete_quest(quest_id)
        
        self.save_data()
        return True
    
    def complete_quest(self, quest_id: str) -> bool:
        """Mark a quest as completed"""
        if quest_id not in self.quests:
            return False
        
        quest = self.quests[quest_id]
        quest.status = QuestStatus.COMPLETED
        quest.progress = 1.0
        quest.completed_date = datetime.datetime.now().isoformat()
        
        # Check for achievements
        self._check_achievements()
        
        self.save_data()
        return True
    
    def log_learning_session(self, quest_id: str, duration_minutes: int, 
                           quality_rating: int, notes: str = "", 
                           skills_practiced: List[str] = None) -> str:
        """Log a learning session"""
        if skills_practiced is None:
            skills_practiced = []
        
        session_id = f"session_{len(self.sessions) + 1}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        now = datetime.datetime.now()
        start_time = now - datetime.timedelta(minutes=duration_minutes)
        
        session = LearningSession(
            id=session_id,
            quest_id=quest_id,
            start_time=start_time.isoformat(),
            end_time=now.isoformat(),
            duration_minutes=duration_minutes,
            quality_rating=quality_rating,
            notes=notes,
            skills_practiced=skills_practiced
        )
        
        self.sessions[session_id] = session
        
        # Update quest progress based on session
        if quest_id in self.quests:
            quest = self.quests[quest_id]
            if quest.status == QuestStatus.IN_PROGRESS:
                # Simple progress calculation based on session quality and duration
                progress_increment = (quality_rating / 5.0) * (duration_minutes / 60.0) * 0.1
                quest.progress = min(1.0, quest.progress + progress_increment)
                
                if quest.progress >= 1.0:
                    self.complete_quest(quest_id)
        
        # Update streak
        self._update_streak()
        
        self.save_data()
        return session_id
    
    def _update_streak(self):
        """Update daily learning streak"""
        today = datetime.date.today().isoformat()
        yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        
        if today not in self.streak_data:
            if yesterday in self.streak_data:
                self.streak_data[today] = self.streak_data[yesterday] + 1
            else:
                self.streak_data[today] = 1
    
    def get_current_streak(self) -> int:
        """Get current learning streak in days"""
        today = datetime.date.today().isoformat()
        return self.streak_data.get(today, 0)
    
    def _check_achievements(self):
        """Check and unlock achievements based on current progress"""
        # Check first quest achievement
        if not self.achievements["first_quest"].unlocked_date:
            completed_quests = [q for q in self.quests.values() if q.status == QuestStatus.COMPLETED]
            if completed_quests:
                self.achievements["first_quest"].unlocked_date = datetime.datetime.now().isoformat()
        
        # Check quest master achievement
        if not self.achievements["quest_master"].unlocked_date:
            completed_quests = [q for q in self.quests.values() if q.status == QuestStatus.COMPLETED]
            if len(completed_quests) >= 10:
                self.achievements["quest_master"].unlocked_date = datetime.datetime.now().isoformat()
        
        # Check streak achievements
        current_streak = self.get_current_streak()
        if current_streak >= 7 and not self.achievements["week_streak"].unlocked_date:
            self.achievements["week_streak"].unlocked_date = datetime.datetime.now().isoformat()
        
        if current_streak >= 30 and not self.achievements["month_streak"].unlocked_date:
            self.achievements["month_streak"].unlocked_date = datetime.datetime.now().isoformat()
    
    def get_sdt_scores(self) -> Dict[str, float]:
        """Calculate SDT scores based on quest and session data"""
        # Autonomy: Based on self-created quests and choice in learning
        total_quests = len(self.quests)
        self_created_quests = len([q for q in self.quests.values() if q.reward_type == RewardType.INTRINSIC])
        autonomy_score = self_created_quests / total_quests if total_quests > 0 else 0
        
        # Competence: Based on quest completion rate and quality ratings
        completed_quests = [q for q in self.quests.values() if q.status == QuestStatus.COMPLETED]
        completion_rate = len(completed_quests) / total_quests if total_quests > 0 else 0
        
        avg_quality = 0
        if self.sessions:
            avg_quality = sum(session.quality_rating for session in self.sessions.values()) / len(self.sessions)
        
        competence_score = (completion_rate + (avg_quality / 5.0)) / 2
        
        # Relatedness: Based on shared achievements and community engagement
        # This would be enhanced with actual social features
        shared_achievements = len([a for a in self.achievements.values() if a.unlocked_date])
        relatedness_score = min(1.0, shared_achievements / 5.0)  # Normalize to 0-1
        
        return {
            'autonomy': autonomy_score,
            'competence': competence_score,
            'relatedness': relatedness_score,
            'overall': (autonomy_score + competence_score + relatedness_score) / 3
        }
    
    def get_motivation_dashboard(self) -> Dict:
        """Get comprehensive motivation dashboard data"""
        sdt_scores = self.get_sdt_scores()
        current_streak = self.get_current_streak()
        
        # Quest statistics
        total_quests = len(self.quests)
        active_quests = len([q for q in self.quests.values() if q.status == QuestStatus.IN_PROGRESS])
        completed_quests = len([q for q in self.quests.values() if q.status == QuestStatus.COMPLETED])
        
        # Session statistics
        total_sessions = len(self.sessions)
        total_learning_time = sum(session.duration_minutes for session in self.sessions.values())
        avg_session_quality = sum(session.quality_rating for session in self.sessions.values()) / total_sessions if total_sessions > 0 else 0
        
        # Achievement statistics
        unlocked_achievements = len([a for a in self.achievements.values() if a.unlocked_date])
        total_achievements = len(self.achievements)
        
        return {
            'sdt_scores': sdt_scores,
            'current_streak': current_streak,
            'quest_stats': {
                'total': total_quests,
                'active': active_quests,
                'completed': completed_quests,
                'completion_rate': completed_quests / total_quests if total_quests > 0 else 0
            },
            'session_stats': {
                'total_sessions': total_sessions,
                'total_learning_time_hours': total_learning_time / 60,
                'avg_session_quality': avg_session_quality,
                'avg_session_duration': total_learning_time / total_sessions if total_sessions > 0 else 0
            },
            'achievement_stats': {
                'unlocked': unlocked_achievements,
                'total': total_achievements,
                'completion_rate': unlocked_achievements / total_achievements
            }
        }
    
    def get_recommendations(self) -> List[str]:
        """Get personalized recommendations based on SDT scores"""
        sdt_scores = self.get_sdt_scores()
        recommendations = []
        
        if sdt_scores['autonomy'] < 0.5:
            recommendations.append("Create more self-defined quests to increase autonomy")
            recommendations.append("Set personal learning goals that align with your interests")
        
        if sdt_scores['competence'] < 0.5:
            recommendations.append("Focus on completing easier quests to build confidence")
            recommendations.append("Break down complex quests into smaller, manageable tasks")
        
        if sdt_scores['relatedness'] < 0.5:
            recommendations.append("Share your achievements with friends or study groups")
            recommendations.append("Join learning communities or find study partners")
        
        if self.get_current_streak() < 3:
            recommendations.append("Try to maintain a daily learning habit, even if just for 15 minutes")
        
        return recommendations

# Example usage and testing
if __name__ == "__main__":
    # Initialize the motivation engine
    motivation = MotivationEngine()
    
    # Create some example quests
    quest1 = motivation.create_quest(
        title="Master Python Fundamentals",
        description="Complete the Python basics course and build 3 small projects",
        category="programming",
        difficulty=3,
        tags=["python", "programming", "fundamentals"]
    )
    
    quest2 = motivation.create_quest(
        title="Read 'Deep Work' by Cal Newport",
        description="Read the entire book and take notes on key concepts",
        category="reading",
        difficulty=2,
        tags=["reading", "productivity", "focus"]
    )
    
    # Start a quest
    motivation.start_quest(quest1)
    
    # Log some learning sessions
    motivation.log_learning_session(
        quest_id=quest1,
        duration_minutes=45,
        quality_rating=4,
        notes="Worked through Python data structures chapter",
        skills_practiced=["python", "data-structures"]
    )
    
    # Update quest progress
    motivation.update_quest_progress(quest1, 0.3)
    
    # Get motivation dashboard
    dashboard = motivation.get_motivation_dashboard()
    print("Motivation Dashboard:")
    print(f"SDT Scores: {dashboard['sdt_scores']}")
    print(f"Current Streak: {dashboard['current_streak']} days")
    print(f"Active Quests: {dashboard['quest_stats']['active']}")
    
    # Get recommendations
    recommendations = motivation.get_recommendations()
    print(f"\nRecommendations: {recommendations}")