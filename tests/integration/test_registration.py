import sys
sys.path.append('..')
from utils import registration

def test_email_validation():
    print('Running test_email_validation...')
    try:
        assert registration.validate_email_format('test@example.com')
        assert not registration.validate_email_format('bad-email')
        print('test_email_validation passed.')
    except AssertionError:
        print('test_email_validation FAILED.')
        raise

def test_name_validation():
    print('Running test_name_validation...')
    try:
        assert registration.validate_name_format('Alice Smith')
        assert not registration.validate_name_format('A')
        print('test_name_validation passed.')
    except AssertionError:
        print('test_name_validation FAILED.')
        raise

def test_registration_and_uniqueness():
    print('Running test_registration_and_uniqueness...')
    try:
        email = 'unique@example.com'
        name = 'Unique User'
        consent = True
        record = registration.create_registration_record(name, email, consent)
        registration.store_registration(record)
        assert registration.is_email_already_registered(email)
        print('test_registration_and_uniqueness passed.')
    except AssertionError:
        print('test_registration_and_uniqueness FAILED.')
        raise
    finally:
        # Clean up
        import os
        if os.path.exists('data/registrations.json'):
            os.remove('data/registrations.json')

def run_tests():
    print('Starting registration tests...')
    try:
        test_email_validation()
        test_name_validation()
        test_registration_and_uniqueness()
        print('All registration tests passed.')
    except Exception as e:
        print('Registration tests FAILED.')
        sys.exit(1)

if __name__ == '__main__':
    run_tests() 