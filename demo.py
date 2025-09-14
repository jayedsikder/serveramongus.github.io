#!/usr/bin/env python3
"""
Demonstration of the Cognitive Workflow System
Shows the complete system in action with realistic examples
"""

import os
import sys
import tempfile
import shutil
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cognitive_workflow import CognitiveWorkflow
from srs_engine import ReviewQuality
from motivation_engine import QuestStatus, RewardType
from digital_brain import ContentType, ProcessingStatus

def run_demo():
    """Run a comprehensive demonstration of the system"""
    print("🧠 Cognitive Workflow System - Demonstration")
    print("=" * 60)
    
    # Create temporary directory for demo
    temp_dir = tempfile.mkdtemp()
    print(f"Using temporary directory: {temp_dir}")
    
    try:
        # Initialize the system
        workflow = CognitiveWorkflow(temp_dir)
        print("✓ System initialized")
        
        # 1. Create a learning quest
        print("\n1. Creating a Learning Quest")
        print("-" * 30)
        
        quest_id = workflow.motivation.create_quest(
            title="Master Cognitive Science",
            description="Learn about memory, motivation, and knowledge management through research and practice",
            category="learning",
            difficulty=4,
            tags=["cognitive-science", "learning", "research"],
            reward_description="Deep understanding of cognitive principles and ability to apply them",
            reward_type=RewardType.INTRINSIC
        )
        
        workflow.motivation.start_quest(quest_id)
        print(f"✓ Quest created and started: {quest_id}")
        
        # 2. Capture and process content
        print("\n2. Capturing and Processing Content")
        print("-" * 40)
        
        # Capture an article about memory
        memory_content = """
        The Ebbinghaus Forgetting Curve: A Foundation for Learning
        
        Hermann Ebbinghaus, a German psychologist, conducted groundbreaking research on memory in the late 19th century. 
        His most famous contribution is the forgetting curve, which demonstrates that memory decays exponentially over time 
        without reinforcement. This finding revolutionized our understanding of learning and retention.
        
        The forgetting curve shows that:
        - 50% of information is forgotten within the first hour
        - 70% is forgotten within 24 hours
        - 90% is forgotten within a week
        
        However, Ebbinghaus also discovered the spacing effect - the phenomenon that learning is more effective when 
        study sessions are spaced out over time rather than massed together. This principle forms the foundation of 
        spaced repetition systems used in modern learning applications.
        
        The implications for education and personal development are profound. Instead of cramming, learners should 
        space their study sessions and review material at increasing intervals to maximize long-term retention.
        """
        
        content1_id = workflow.capture_and_process_content(
            title="The Ebbinghaus Forgetting Curve",
            content=memory_content,
            content_type=ContentType.ARTICLE,
            quest_id=quest_id,
            tags=["memory", "psychology", "learning", "ebbinghaus"]
        )
        print(f"✓ Memory article captured: {content1_id}")
        
        # Capture content about motivation
        motivation_content = """
        Self-Determination Theory: The Psychology of Motivation
        
        Self-Determination Theory (SDT), developed by Edward Deci and Richard Ryan, is a macro theory of human 
        motivation that examines the conditions that promote or hinder intrinsic motivation. SDT identifies three 
        basic psychological needs that must be satisfied for optimal motivation and well-being:
        
        1. Autonomy: The need to feel a sense of volition and control over one's actions
        2. Competence: The need to feel effective and experience mastery over challenges
        3. Relatedness: The need to feel connected to others and have a sense of belonging
        
        When these needs are met, individuals experience intrinsic motivation - the drive to engage in activities 
        for their inherent satisfaction rather than external rewards. This type of motivation is associated with 
        higher performance, persistence, and psychological well-being.
        
        SDT has important implications for education, workplace management, and personal development. By creating 
        environments that support autonomy, competence, and relatedness, we can foster sustained engagement and 
        optimal performance.
        """
        
        content2_id = workflow.capture_and_process_content(
            title="Self-Determination Theory",
            content=motivation_content,
            content_type=ContentType.PAPER,
            quest_id=quest_id,
            tags=["motivation", "psychology", "sdt", "autonomy"]
        )
        print(f"✓ Motivation paper captured: {content2_id}")
        
        # 3. Create SRS cards from concepts
        print("\n3. Creating SRS Cards from Concepts")
        print("-" * 40)
        
        # Get concepts from the captured content
        concepts1 = workflow.brain.content_items[content1_id].concepts
        concepts2 = workflow.brain.content_items[content2_id].concepts
        
        print(f"Concepts from memory article: {concepts1}")
        print(f"Concepts from motivation paper: {concepts2}")
        
        # Create cards for key concepts
        card1_id = workflow.srs.create_card(
            front="What is the Ebbinghaus forgetting curve?",
            back="The exponential decay of memory over time without reinforcement, showing that 50% is forgotten within an hour and 90% within a week.",
            tags=["memory", "ebbinghaus", "psychology"]
        )
        
        card2_id = workflow.srs.create_card(
            front="What are the three psychological needs in Self-Determination Theory?",
            back="Autonomy (sense of control), Competence (feeling effective), and Relatedness (connection to others).",
            tags=["motivation", "sdt", "psychology"]
        )
        
        card3_id = workflow.srs.create_card(
            front="What is the spacing effect?",
            back="The phenomenon that learning is more effective when study sessions are spaced out over time rather than massed together.",
            tags=["memory", "learning", "spacing"]
        )
        
        print(f"✓ Created 3 SRS cards")
        
        # 4. Start a learning session
        print("\n4. Starting a Learning Session")
        print("-" * 35)
        
        session_id = workflow.start_learning_session(quest_id)
        print(f"✓ Learning session started: {session_id}")
        
        # Simulate some learning activity
        print("\nSimulating learning activities...")
        
        # Review some cards
        due_cards = workflow.srs.get_due_cards()
        for i, card in enumerate(due_cards[:3], 1):
            print(f"  Reviewing card {i}: {card.front}")
            # Simulate different review qualities
            qualities = [ReviewQuality.GOOD, ReviewQuality.EASY, ReviewQuality.HARD]
            quality = qualities[i-1] if i <= len(qualities) else ReviewQuality.GOOD
            workflow.srs.review_card(card.id, quality)
            print(f"    Rated as: {quality.name}")
        
        # Log the session
        workflow.end_learning_session(
            session_id, 
            quality_rating=4, 
            notes="Great progress on memory and motivation concepts. Made good connections between Ebbinghaus and SDT."
        )
        print("✓ Learning session completed")
        
        # 5. Run daily review workflow
        print("\n5. Running Daily Review Workflow")
        print("-" * 40)
        
        results = workflow.daily_review_workflow()
        print(f"✓ Daily review completed:")
        print(f"  - SRS reviews: {results['srs_reviews']}")
        print(f"  - Quest updates: {results['quest_updates']}")
        print(f"  - Content processed: {results['content_processed']}")
        print(f"  - Insights generated: {results['insights_generated']}")
        
        # 6. Generate insights
        print("\n6. Generating Research Insights")
        print("-" * 35)
        
        insights = workflow.generate_research_insights("memory")
        print(f"✓ Generated {len(insights)} insights on memory:")
        for i, insight in enumerate(insights, 1):
            print(f"  {i}. {insight['title']}")
            print(f"     {insight['content'][:100]}...")
        
        # 7. View comprehensive dashboard
        print("\n7. System Dashboard")
        print("-" * 20)
        
        dashboard = workflow.get_workflow_dashboard()
        
        print(f"\n📊 SRS System:")
        print(f"  Total cards: {dashboard['srs']['total_cards']}")
        print(f"  Due for review: {dashboard['srs']['due_cards']}")
        print(f"  Success rate: {dashboard['srs']['overall_success_rate']:.1%}")
        
        print(f"\n🎯 Motivation System:")
        print(f"  Current streak: {dashboard['motivation']['current_streak']} days")
        print(f"  Active quests: {dashboard['motivation']['quest_stats']['active']}")
        print(f"  Completed quests: {dashboard['motivation']['quest_stats']['completed']}")
        print(f"  SDT Scores:")
        sdt = dashboard['motivation']['sdt_scores']
        print(f"    Autonomy: {sdt['autonomy']:.2f}")
        print(f"    Competence: {sdt['competence']:.2f}")
        print(f"    Relatedness: {sdt['relatedness']:.2f}")
        
        print(f"\n📝 Digital Brain:")
        print(f"  Total content: {dashboard['digital_brain']['total_content']}")
        print(f"  Processed: {dashboard['digital_brain']['processed_content']}")
        print(f"  Synthesized: {dashboard['digital_brain']['synthesized_content']}")
        print(f"  Concepts: {dashboard['digital_brain']['total_concepts']}")
        print(f"  Insights: {dashboard['digital_brain']['total_insights']}")
        
        print(f"\n🏥 Workflow Health:")
        health = dashboard['workflow_health']
        print(f"  Overall health: {health['overall_health']:.2f}")
        print(f"  SRS health: {health['srs_health']:.2f}")
        print(f"  Motivation health: {health['motivation_health']:.2f}")
        print(f"  Brain health: {health['brain_health']:.2f}")
        
        print(f"\n💡 Recommendations:")
        for rec in health['recommendations']:
            print(f"  • {rec}")
        
        # 8. Show knowledge graph
        print("\n8. Knowledge Graph")
        print("-" * 20)
        
        if workflow.brain.concepts:
            print("Concepts in the knowledge graph:")
            for concept_id, concept in workflow.brain.concepts.items():
                print(f"  • {concept.name} (appears in {len(concept.content_items)} content items)")
        
        # 9. Export data
        print("\n9. Exporting Data")
        print("-" * 20)
        
        export_file = f"{temp_dir}/demo_export.json"
        workflow.export_workflow_data(export_file)
        print(f"✓ Data exported to: {export_file}")
        
        print("\n🎉 Demonstration completed successfully!")
        print("\nThe Cognitive Workflow System has demonstrated:")
        print("✓ Content capture and processing")
        print("✓ Concept extraction and linking")
        print("✓ SRS card creation and review")
        print("✓ Quest management and progress tracking")
        print("✓ Learning session management")
        print("✓ Insight generation")
        print("✓ Comprehensive analytics and health monitoring")
        print("✓ Data persistence and export")
        
        print(f"\nAll data has been saved to: {temp_dir}")
        print("You can explore the JSON files to see the complete data structure.")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Note: We're not cleaning up the temp directory so you can explore the data
        print(f"\nData preserved in: {temp_dir}")

if __name__ == "__main__":
    run_demo()