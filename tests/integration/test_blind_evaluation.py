import sys
sys.path.append('..')
import json
import os
from pages.blind_evaluation import (
    load_evaluation_data,
    create_sample_responses,
    get_responses_for_question,
    shuffle_responses
)

def test_load_evaluation_data():
    print('Testing load_evaluation_data...')
    questions, responses = load_evaluation_data()
    assert isinstance(questions, dict)
    assert isinstance(responses, list)
    print('load_evaluation_data test passed.')

def test_create_sample_responses():
    print('Testing create_sample_responses...')
    questions = {
        "retail": ["What product had the highest sales?"],
        "finance": ["What was the closing price?"]
    }
    responses = create_sample_responses(questions)
    assert len(responses) == 8  # 2 industries * 1 question * 4 models
    assert all("llm_model" in response for response in responses)
    print('create_sample_responses test passed.')

def test_get_responses_for_question():
    print('Testing get_responses_for_question...')
    questions = {
        "retail": ["What product had the highest sales?"],
        "finance": ["What was the closing price?"]
    }
    responses = create_sample_responses(questions)
    
    retail_responses = get_responses_for_question(
        "What product had the highest sales?", "retail", responses
    )
    assert len(retail_responses) == 4  # 4 models
    print('get_responses_for_question test passed.')

def test_shuffle_responses():
    print('Testing shuffle_responses...')
    questions = {
        "retail": ["What product had the highest sales?"]
    }
    responses = create_sample_responses(questions)
    retail_responses = get_responses_for_question(
        "What product had the highest sales?", "retail", responses
    )
    
    shuffled = shuffle_responses(retail_responses)
    assert len(shuffled) == 4
    assert all("anonymous_id" in response for response in shuffled)
    assert set(response["anonymous_id"] for response in shuffled) == {"A", "B", "C", "D"}
    print('shuffle_responses test passed.')

def run_tests():
    print('Starting blind evaluation tests...')
    try:
        test_load_evaluation_data()
        test_create_sample_responses()
        test_get_responses_for_question()
        test_shuffle_responses()
        print('All blind evaluation tests passed.')
    except Exception as e:
        print(f'Blind evaluation tests FAILED: {str(e)}')
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    run_tests() 