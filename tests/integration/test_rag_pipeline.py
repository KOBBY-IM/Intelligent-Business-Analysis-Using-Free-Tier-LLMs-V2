import sys
sys.path.append('..')
from utils import rag_pipeline, embedding

def test_rag_pipeline():
    print('Running test_rag_pipeline...')
    try:
        print('  Building RAG index...')
        db = rag_pipeline.build_rag_index('data/shopping_trends.csv', dataset_type='csv')
        print('  Getting embedding model...')
        model = embedding.get_embedding_model()
        print('  Retrieving context...')
        results = rag_pipeline.retrieve_context('What product had the highest sales?', db, model, top_k=1)
        print(f'  Retrieved {len(results)} results')
        assert isinstance(results, list)
        assert len(results) > 0
        print('test_rag_pipeline passed.')
    except Exception as e:
        print(f'test_rag_pipeline FAILED with error: {str(e)}')
        import traceback
        traceback.print_exc()
        raise

def run_tests():
    print('Starting RAG pipeline tests...')
    try:
        test_rag_pipeline()
        print('All RAG pipeline tests passed.')
    except Exception as e:
        print('RAG pipeline tests FAILED.')
        sys.exit(1)

if __name__ == '__main__':
    run_tests() 