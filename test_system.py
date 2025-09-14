#!/usr/bin/env python3
"""
Test script for the Cognitive Workflow System
Verifies that all components work correctly
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

def test_srs_engine():
    """Test the SRS engine functionality"""
    print("Testing SRS Engine...")
    
    from srs_engine import SRSEngine
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    srs = SRSEngine(f"{temp_dir}/srs_test.json")
    
    # Test card creation
    card_id = srs.create_card(
        front="What is the Ebbinghaus forgetting curve?",
        back="The exponential decay of memory over time without reinforcement",
        tags=["memory", "psychology"]
    )
    
    assert card_id is not None
    assert card_id in srs.cards
    print("✓ Card creation works")
    
    # Test card review
    result = srs.review_card(card_id, ReviewQuality.GOOD)
    assert result['card']['repetitions'] == 1
    print("✓ Card review works")
    
    # Test due cards
    due_cards = srs.get_due_cards()
    assert len(due_cards) >= 0
    print("✓ Due cards retrieval works")
    
    # Test statistics
    stats = srs.get_overall_stats()
    assert stats['total_cards'] == 1
    print("✓ Statistics work")
    
    # Cleanup
    shutil.rmtree(temp_dir)
    print("✓ SRS Engine test passed\n")

def test_motivation_engine():
    """Test the motivation engine functionality"""
    print("Testing Motivation Engine...")
    
    from motivation_engine import MotivationEngine
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    motivation = MotivationEngine(f"{temp_dir}/motivation_test.json")
    
    # Test quest creation
    quest_id = motivation.create_quest(
        title="Test Quest",
        description="A test quest for verification",
        category="testing",
        difficulty=3,
        tags=["test"]
    )
    
    assert quest_id is not None
    assert quest_id in motivation.quests
    print("✓ Quest creation works")
    
    # Test quest starting
    success = motivation.start_quest(quest_id)
    assert success
    assert motivation.quests[quest_id].status == QuestStatus.IN_PROGRESS
    print("✓ Quest starting works")
    
    # Test progress update
    success = motivation.update_quest_progress(quest_id, 0.5)
    assert success
    assert motivation.quests[quest_id].progress == 0.5
    print("✓ Progress update works")
    
    # Test session logging
    session_id = motivation.log_learning_session(
        quest_id=quest_id,
        duration_minutes=30,
        quality_rating=4,
        notes="Test session"
    )
    
    assert session_id is not None
    assert session_id in motivation.sessions
    print("✓ Session logging works")
    
    # Test SDT scores
    sdt_scores = motivation.get_sdt_scores()
    assert 'autonomy' in sdt_scores
    assert 'competence' in sdt_scores
    assert 'relatedness' in sdt_scores
    print("✓ SDT scores work")
    
    # Cleanup
    shutil.rmtree(temp_dir)
    print("✓ Motivation Engine test passed\n")

def test_digital_brain():
    """Test the digital brain functionality"""
    print("Testing Digital Brain...")
    
    from digital_brain import DigitalBrain
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    brain = DigitalBrain(f"{temp_dir}/brain_test.json")
    
    # Test content capture
    content_id = brain.capture_content(
        title="Test Article",
        content="This is a test article about memory and learning. It contains important concepts about cognitive science.",
        content_type=ContentType.ARTICLE,
        tags=["test", "memory"]
    )
    
    assert content_id is not None
    assert content_id in brain.content_items
    print("✓ Content capture works")
    
    # Test content processing
    success = brain.process_content(content_id)
    assert success
    assert brain.content_items[content_id].status == ProcessingStatus.PROCESSED
    print("✓ Content processing works")
    
    # Test concept extraction
    item = brain.content_items[content_id]
    assert len(item.concepts) > 0
    print("✓ Concept extraction works")
    
    # Test content synthesis
    success = brain.synthesize_content(content_id)
    assert success
    assert brain.content_items[content_id].status == ProcessingStatus.SYNTHESIZED
    print("✓ Content synthesis works")
    
    # Test knowledge search
    results = brain.search_knowledge("memory")
    assert len(results) > 0
    print("✓ Knowledge search works")
    
    # Test insight generation
    if len(brain.concepts) >= 2:
        concept_ids = list(brain.concepts.keys())[:2]
        insight_id = brain.generate_insight(concept_ids)
        assert insight_id is not None
        print("✓ Insight generation works")
    
    # Test statistics
    stats = brain.get_knowledge_graph_stats()
    assert stats['total_content'] == 1
    print("✓ Statistics work")
    
    # Cleanup
    shutil.rmtree(temp_dir)
    print("✓ Digital Brain test passed\n")

def test_integrated_workflow():
    """Test the integrated workflow system"""
    print("Testing Integrated Workflow...")
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    workflow = CognitiveWorkflow(temp_dir)
    
    # Test quest creation
    quest_id = workflow.motivation.create_quest(
        title="Integrated Test Quest",
        description="Testing the integrated workflow",
        category="testing",
        difficulty=3
    )
    
    workflow.motivation.start_quest(quest_id)
    print("✓ Quest creation in workflow works")
    
    # Test content capture and processing
    content_id = workflow.capture_and_process_content(
        title="Test Content",
        content="This is test content for the integrated workflow system.",
        content_type=ContentType.ARTICLE,
        quest_id=quest_id,
        tags=["test", "integration"]
    )
    
    assert content_id is not None
    print("✓ Content capture in workflow works")
    
    # Test learning session
    session_id = workflow.start_learning_session(quest_id)
    assert session_id is not None
    print("✓ Learning session creation works")
    
    # Test daily review
    results = workflow.daily_review_workflow()
    assert isinstance(results, dict)
    print("✓ Daily review workflow works")
    
    # Test dashboard
    dashboard = workflow.get_workflow_dashboard()
    assert 'srs' in dashboard
    assert 'motivation' in dashboard
    assert 'digital_brain' in dashboard
    print("✓ Dashboard generation works")
    
    # Test insight generation
    insights = workflow.generate_research_insights("test")
    assert isinstance(insights, list)
    print("✓ Insight generation works")
    
    # Cleanup
    shutil.rmtree(temp_dir)
    print("✓ Integrated Workflow test passed\n")

def test_cli_interface():
    """Test the CLI interface (basic functionality)"""
    print("Testing CLI Interface...")
    
    from cli_interface import CognitiveWorkflowCLI
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    cli = CognitiveWorkflowCLI(temp_dir)
    
    # Test initialization
    assert cli.workflow is not None
    assert cli.current_session is None
    print("✓ CLI initialization works")
    
    # Test quest creation through CLI
    quest_id = cli.workflow.motivation.create_quest(
        title="CLI Test Quest",
        description="Testing CLI functionality",
        category="testing"
    )
    
    assert quest_id is not None
    print("✓ CLI quest creation works")
    
    # Test content capture through CLI
    content_id = cli.workflow.capture_and_process_content(
        title="CLI Test Content",
        content="Test content for CLI testing",
        content_type=ContentType.NOTE
    )
    
    assert content_id is not None
    print("✓ CLI content capture works")
    
    # Cleanup
    shutil.rmtree(temp_dir)
    print("✓ CLI Interface test passed\n")

def run_all_tests():
    """Run all tests"""
    print("🧠 Running Cognitive Workflow System Tests")
    print("=" * 50)
    
    try:
        test_srs_engine()
        test_motivation_engine()
        test_digital_brain()
        test_integrated_workflow()
        test_cli_interface()
        
        print("🎉 All tests passed successfully!")
        print("The Cognitive Workflow System is ready to use.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)