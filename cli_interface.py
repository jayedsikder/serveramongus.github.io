#!/usr/bin/env python3
"""
CLI Interface for the Cognitive Workflow System
Provides an interactive command-line interface for managing the integrated learning system
"""

import argparse
import sys
import json
from datetime import datetime
from typing import List, Dict, Optional

from cognitive_workflow import CognitiveWorkflow
from srs_engine import ReviewQuality
from motivation_engine import QuestStatus, RewardType
from digital_brain import ContentType, ProcessingStatus

class CognitiveWorkflowCLI:
    """Command-line interface for the Cognitive Workflow system"""
    
    def __init__(self, data_dir: str = "cognitive_workflow_data"):
        self.workflow = CognitiveWorkflow(data_dir)
        self.current_session = None
    
    def run(self):
        """Main CLI loop"""
        print("🧠 Cognitive Workflow System")
        print("=" * 50)
        
        while True:
            try:
                self.show_main_menu()
                choice = input("\nEnter your choice: ").strip()
                
                if choice == "1":
                    self.daily_review()
                elif choice == "2":
                    self.manage_quests()
                elif choice == "3":
                    self.manage_srs()
                elif choice == "4":
                    self.manage_content()
                elif choice == "5":
                    self.view_dashboard()
                elif choice == "6":
                    self.start_learning_session()
                elif choice == "7":
                    self.generate_insights()
                elif choice == "8":
                    self.export_data()
                elif choice == "9":
                    self.show_help()
                elif choice == "0":
                    print("Goodbye! Keep learning! 🚀")
                    break
                else:
                    print("Invalid choice. Please try again.")
                    
            except KeyboardInterrupt:
                print("\n\nGoodbye! Keep learning! 🚀")
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                print("Please try again.")
    
    def show_main_menu(self):
        """Display the main menu"""
        print("\n" + "=" * 50)
        print("MAIN MENU")
        print("=" * 50)
        print("1. 📚 Daily Review")
        print("2. 🎯 Manage Quests")
        print("3. 🧠 Manage SRS Cards")
        print("4. 📝 Manage Content")
        print("5. 📊 View Dashboard")
        print("6. 🚀 Start Learning Session")
        print("7. 💡 Generate Insights")
        print("8. 💾 Export Data")
        print("9. ❓ Help")
        print("0. 🚪 Exit")
    
    def daily_review(self):
        """Execute daily review workflow"""
        print("\n📚 Daily Review")
        print("-" * 30)
        
        # Show due cards
        due_cards = self.workflow.srs.get_due_cards()
        print(f"Cards due for review: {len(due_cards)}")
        
        if due_cards:
            print("\nReviewing cards...")
            for i, card in enumerate(due_cards[:10], 1):
                print(f"\nCard {i}/{min(10, len(due_cards))}")
                print(f"Front: {card.front}")
                input("Press Enter to see answer...")
                print(f"Back: {card.back}")
                
                while True:
                    quality = input("Rate your recall (1=Again, 2=Hard, 3=Good, 4=Easy): ").strip()
                    if quality in ["1", "2", "3", "4"]:
                        quality_enum = [ReviewQuality.AGAIN, ReviewQuality.HARD, ReviewQuality.GOOD, ReviewQuality.EASY][int(quality)-1]
                        self.workflow.srs.review_card(card.id, quality_enum)
                        break
                    else:
                        print("Please enter 1, 2, 3, or 4")
        
        # Run automated daily review
        results = self.workflow.daily_review_workflow()
        print(f"\nDaily review completed:")
        print(f"- SRS reviews: {results['srs_reviews']}")
        print(f"- Quest updates: {results['quest_updates']}")
        print(f"- Content processed: {results['content_processed']}")
        print(f"- Insights generated: {results['insights_generated']}")
    
    def manage_quests(self):
        """Manage learning quests"""
        print("\n🎯 Quest Management")
        print("-" * 30)
        
        while True:
            print("\n1. Create new quest")
            print("2. View all quests")
            print("3. Update quest progress")
            print("4. Complete quest")
            print("5. Back to main menu")
            
            choice = input("Enter your choice: ").strip()
            
            if choice == "1":
                self.create_quest()
            elif choice == "2":
                self.view_quests()
            elif choice == "3":
                self.update_quest_progress()
            elif choice == "4":
                self.complete_quest()
            elif choice == "5":
                break
            else:
                print("Invalid choice. Please try again.")
    
    def create_quest(self):
        """Create a new quest"""
        print("\nCreate New Quest")
        print("-" * 20)
        
        title = input("Quest title: ").strip()
        description = input("Description: ").strip()
        category = input("Category: ").strip()
        
        print("Difficulty (1-5):")
        difficulty = int(input("Enter difficulty: ").strip())
        
        tags_input = input("Tags (comma-separated): ").strip()
        tags = [tag.strip() for tag in tags_input.split(",")] if tags_input else []
        
        quest_id = self.workflow.motivation.create_quest(
            title=title,
            description=description,
            category=category,
            difficulty=difficulty,
            tags=tags
        )
        
        print(f"Quest created with ID: {quest_id}")
        
        start_now = input("Start this quest now? (y/n): ").strip().lower()
        if start_now == "y":
            self.workflow.motivation.start_quest(quest_id)
            print("Quest started!")
    
    def view_quests(self):
        """View all quests"""
        print("\nAll Quests")
        print("-" * 20)
        
        quests = self.workflow.motivation.quests
        if not quests:
            print("No quests found.")
            return
        
        for quest in quests.values():
            status_icon = {"not_started": "⏸️", "in_progress": "▶️", "completed": "✅", "paused": "⏸️", "cancelled": "❌"}
            print(f"\n{status_icon.get(quest.status.value, '❓')} {quest.title}")
            print(f"   Status: {quest.status.value}")
            print(f"   Progress: {quest.progress:.1%}")
            print(f"   Category: {quest.category}")
            print(f"   Difficulty: {quest.difficulty}/5")
            if quest.tags:
                print(f"   Tags: {', '.join(quest.tags)}")
    
    def update_quest_progress(self):
        """Update quest progress"""
        print("\nUpdate Quest Progress")
        print("-" * 25)
        
        # Show active quests
        active_quests = [q for q in self.workflow.motivation.quests.values() if q.status == QuestStatus.IN_PROGRESS]
        if not active_quests:
            print("No active quests found.")
            return
        
        print("Active quests:")
        for i, quest in enumerate(active_quests, 1):
            print(f"{i}. {quest.title} ({quest.progress:.1%})")
        
        try:
            choice = int(input("Select quest number: ").strip()) - 1
            if 0 <= choice < len(active_quests):
                quest = active_quests[choice]
                progress = float(input(f"Enter new progress (0.0-1.0, current: {quest.progress:.1%}): ").strip())
                self.workflow.motivation.update_quest_progress(quest.id, progress)
                print("Progress updated!")
            else:
                print("Invalid quest number.")
        except ValueError:
            print("Invalid input.")
    
    def complete_quest(self):
        """Complete a quest"""
        print("\nComplete Quest")
        print("-" * 15)
        
        # Show active quests
        active_quests = [q for q in self.workflow.motivation.quests.values() if q.status == QuestStatus.IN_PROGRESS]
        if not active_quests:
            print("No active quests found.")
            return
        
        print("Active quests:")
        for i, quest in enumerate(active_quests, 1):
            print(f"{i}. {quest.title} ({quest.progress:.1%})")
        
        try:
            choice = int(input("Select quest number: ").strip()) - 1
            if 0 <= choice < len(active_quests):
                quest = active_quests[choice]
                self.workflow.motivation.complete_quest(quest.id)
                print(f"Quest '{quest.title}' completed! 🎉")
            else:
                print("Invalid quest number.")
        except ValueError:
            print("Invalid input.")
    
    def manage_srs(self):
        """Manage SRS cards"""
        print("\n🧠 SRS Card Management")
        print("-" * 30)
        
        while True:
            print("\n1. Create new card")
            print("2. View all cards")
            print("3. Search cards")
            print("4. View due cards")
            print("5. Back to main menu")
            
            choice = input("Enter your choice: ").strip()
            
            if choice == "1":
                self.create_card()
            elif choice == "2":
                self.view_cards()
            elif choice == "3":
                self.search_cards()
            elif choice == "4":
                self.view_due_cards()
            elif choice == "5":
                break
            else:
                print("Invalid choice. Please try again.")
    
    def create_card(self):
        """Create a new SRS card"""
        print("\nCreate New Card")
        print("-" * 20)
        
        front = input("Front (question): ").strip()
        back = input("Back (answer): ").strip()
        tags_input = input("Tags (comma-separated): ").strip()
        tags = [tag.strip() for tag in tags_input.split(",")] if tags_input else []
        
        card_id = self.workflow.srs.create_card(front, back, tags)
        print(f"Card created with ID: {card_id}")
    
    def view_cards(self):
        """View all cards"""
        print("\nAll Cards")
        print("-" * 15)
        
        cards = self.workflow.srs.cards
        if not cards:
            print("No cards found.")
            return
        
        for card in cards.values():
            print(f"\n📝 {card.front}")
            print(f"   Answer: {card.back}")
            print(f"   Tags: {', '.join(card.tags) if card.tags else 'None'}")
            print(f"   Next review: {card.next_review}")
            print(f"   Interval: {card.interval} days")
    
    def search_cards(self):
        """Search for cards"""
        query = input("Search query: ").strip()
        if not query:
            return
        
        results = self.workflow.srs.search_cards(query)
        if not results:
            print("No cards found.")
            return
        
        print(f"\nFound {len(results)} cards:")
        for card in results:
            print(f"\n📝 {card.front}")
            print(f"   Answer: {card.back}")
            print(f"   Tags: {', '.join(card.tags) if card.tags else 'None'}")
    
    def view_due_cards(self):
        """View cards due for review"""
        due_cards = self.workflow.srs.get_due_cards()
        if not due_cards:
            print("No cards due for review.")
            return
        
        print(f"\nCards due for review: {len(due_cards)}")
        for card in due_cards:
            print(f"\n📝 {card.front}")
            print(f"   Answer: {card.back}")
            print(f"   Next review: {card.next_review}")
    
    def manage_content(self):
        """Manage content in digital brain"""
        print("\n📝 Content Management")
        print("-" * 30)
        
        while True:
            print("\n1. Capture new content")
            print("2. View all content")
            print("3. Search content")
            print("4. Process content")
            print("5. Back to main menu")
            
            choice = input("Enter your choice: ").strip()
            
            if choice == "1":
                self.capture_content()
            elif choice == "2":
                self.view_content()
            elif choice == "3":
                self.search_content()
            elif choice == "4":
                self.process_content()
            elif choice == "5":
                break
            else:
                print("Invalid choice. Please try again.")
    
    def capture_content(self):
        """Capture new content"""
        print("\nCapture New Content")
        print("-" * 25)
        
        title = input("Title: ").strip()
        content = input("Content: ").strip()
        
        print("Content type:")
        print("1. Article")
        print("2. Paper")
        print("3. Video")
        print("4. Podcast")
        print("5. Book")
        print("6. Note")
        print("7. Idea")
        
        type_choice = input("Enter type (1-7): ").strip()
        type_map = {
            "1": ContentType.ARTICLE,
            "2": ContentType.PAPER,
            "3": ContentType.VIDEO,
            "4": ContentType.PODCAST,
            "5": ContentType.BOOK,
            "6": ContentType.NOTE,
            "7": ContentType.IDEA
        }
        
        content_type = type_map.get(type_choice, ContentType.NOTE)
        
        tags_input = input("Tags (comma-separated): ").strip()
        tags = [tag.strip() for tag in tags_input.split(",")] if tags_input else []
        
        content_id = self.workflow.capture_and_process_content(
            title=title,
            content=content,
            content_type=content_type,
            tags=tags
        )
        
        print(f"Content captured with ID: {content_id}")
    
    def view_content(self):
        """View all content"""
        print("\nAll Content")
        print("-" * 15)
        
        content_items = self.workflow.brain.content_items
        if not content_items:
            print("No content found.")
            return
        
        for item in content_items.values():
            status_icon = {"captured": "📥", "processed": "⚙️", "synthesized": "🔗", "insight": "💡"}
            print(f"\n{status_icon.get(item.status.value, '❓')} {item.title}")
            print(f"   Type: {item.content_type.value}")
            print(f"   Status: {item.status.value}")
            print(f"   Tags: {', '.join(item.tags) if item.tags else 'None'}")
            if item.summary:
                print(f"   Summary: {item.summary}")
    
    def search_content(self):
        """Search for content"""
        query = input("Search query: ").strip()
        if not query:
            return
        
        results = self.workflow.brain.search_knowledge(query)
        if not results:
            print("No content found.")
            return
        
        print(f"\nFound {len(results)} items:")
        for result in results:
            print(f"\n📝 {result['title']}")
            print(f"   Type: {result['content_type']}")
            if result.get('summary'):
                print(f"   Summary: {result['summary']}")
    
    def process_content(self):
        """Process captured content"""
        unprocessed = [item for item in self.workflow.brain.content_items.values() 
                      if item.status == ProcessingStatus.CAPTURED]
        
        if not unprocessed:
            print("No unprocessed content found.")
            return
        
        print(f"Processing {len(unprocessed)} items...")
        for item in unprocessed:
            self.workflow.brain.process_content(item.id)
            print(f"Processed: {item.title}")
    
    def view_dashboard(self):
        """View the workflow dashboard"""
        print("\n📊 Workflow Dashboard")
        print("-" * 30)
        
        dashboard = self.workflow.get_workflow_dashboard()
        
        # SRS Stats
        print("\n🧠 SRS System:")
        srs = dashboard['srs']
        print(f"   Total cards: {srs['total_cards']}")
        print(f"   Due for review: {srs['due_cards']}")
        print(f"   Success rate: {srs['overall_success_rate']:.1%}")
        
        # Motivation Stats
        print("\n🎯 Motivation System:")
        motivation = dashboard['motivation']
        print(f"   Current streak: {motivation['current_streak']} days")
        print(f"   Active quests: {motivation['quest_stats']['active']}")
        print(f"   Completed quests: {motivation['quest_stats']['completed']}")
        print(f"   SDT Scores:")
        sdt = motivation['sdt_scores']
        print(f"     Autonomy: {sdt['autonomy']:.2f}")
        print(f"     Competence: {sdt['competence']:.2f}")
        print(f"     Relatedness: {sdt['relatedness']:.2f}")
        
        # Digital Brain Stats
        print("\n📝 Digital Brain:")
        brain = dashboard['digital_brain']
        print(f"   Total content: {brain['total_content']}")
        print(f"   Processed: {brain['processed_content']}")
        print(f"   Synthesized: {brain['synthesized_content']}")
        print(f"   Concepts: {brain['total_concepts']}")
        print(f"   Insights: {brain['total_insights']}")
        
        # Workflow Health
        print("\n🏥 Workflow Health:")
        health = dashboard['workflow_health']
        print(f"   Overall health: {health['overall_health']:.2f}")
        print(f"   SRS health: {health['srs_health']:.2f}")
        print(f"   Motivation health: {health['motivation_health']:.2f}")
        print(f"   Brain health: {health['brain_health']:.2f}")
        
        print("\n💡 Recommendations:")
        for rec in health['recommendations']:
            print(f"   • {rec}")
    
    def start_learning_session(self):
        """Start a learning session"""
        print("\n🚀 Start Learning Session")
        print("-" * 30)
        
        # Show active quests
        active_quests = [q for q in self.workflow.motivation.quests.values() if q.status == QuestStatus.IN_PROGRESS]
        if not active_quests:
            print("No active quests found. Create a quest first.")
            return
        
        print("Active quests:")
        for i, quest in enumerate(active_quests, 1):
            print(f"{i}. {quest.title} ({quest.progress:.1%})")
        
        try:
            choice = int(input("Select quest number: ").strip()) - 1
            if 0 <= choice < len(active_quests):
                quest = active_quests[choice]
                session_id = self.workflow.start_learning_session(quest.id)
                self.current_session = session_id
                print(f"Learning session started for: {quest.title}")
                print("Session ID:", session_id)
            else:
                print("Invalid quest number.")
        except ValueError:
            print("Invalid input.")
    
    def generate_insights(self):
        """Generate research insights"""
        print("\n💡 Generate Insights")
        print("-" * 25)
        
        topic = input("Enter topic to research: ").strip()
        if not topic:
            return
        
        insights = self.workflow.generate_research_insights(topic)
        if not insights:
            print("No insights found for this topic.")
            return
        
        print(f"\nFound {len(insights)} insights on '{topic}':")
        for i, insight in enumerate(insights, 1):
            print(f"\n{i}. {insight['title']}")
            print(f"   Content: {insight['content']}")
            if insight['concepts']:
                print(f"   Concepts: {', '.join(insight['concepts'])}")
    
    def export_data(self):
        """Export workflow data"""
        print("\n💾 Export Data")
        print("-" * 20)
        
        filename = input("Enter filename (default: workflow_export.json): ").strip()
        if not filename:
            filename = "workflow_export.json"
        
        if not filename.endswith('.json'):
            filename += '.json'
        
        self.workflow.export_workflow_data(filename)
        print(f"Data exported to: {filename}")
    
    def show_help(self):
        """Show help information"""
        print("\n❓ Help")
        print("-" * 10)
        print("""
The Cognitive Workflow System is an integrated learning platform that combines:

1. 📚 Daily Review - Review SRS cards and run automated workflows
2. 🎯 Manage Quests - Create and track learning goals
3. 🧠 Manage SRS Cards - Create and manage spaced repetition cards
4. 📝 Manage Content - Capture and process information
5. 📊 View Dashboard - See overall system health and progress
6. 🚀 Start Learning Session - Begin a focused learning session
7. 💡 Generate Insights - Find connections and insights
8. 💾 Export Data - Export all data for backup

The system is based on cognitive science principles:
- Spaced Repetition for memory retention
- Self-Determination Theory for motivation
- Digital Second Brain for knowledge synthesis

For more information, see the framework documentation.
        """)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Cognitive Workflow System CLI")
    parser.add_argument("--data-dir", default="cognitive_workflow_data", 
                       help="Directory to store data files")
    
    args = parser.parse_args()
    
    try:
        cli = CognitiveWorkflowCLI(args.data_dir)
        cli.run()
    except Exception as e:
        print(f"Error starting CLI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()