# Feature Voting System - Test Suite

This comprehensive test suite covers all aspects of the Feature Voting System backend API including edge cases, database constraints, and integration scenarios.

## Test Structure

### Test Files

1. **`test_users.py`** - User API tests
   - User creation, retrieval, validation
   - Duplicate username/email handling
   - Edge cases and security tests

2. **`test_features.py`** - Feature API tests
   - Feature CRUD operations
   - Authentication and authorization
   - Pagination and sorting
   - Boundary value testing

3. **`test_voting.py`** - Voting functionality tests
   - Vote creation and removal
   - Duplicate vote prevention
   - Vote count accuracy
   - Concurrent voting scenarios

4. **`test_database_constraints.py`** - Database constraint tests
   - Unique constraints
   - Foreign key constraints
   - Cascade operations
   - Data integrity

5. **`test_integration.py`** - Integration tests
   - End-to-end workflows
   - Multi-component interactions
   - Performance under load
   - Concurrent operations

6. **`test_exception_handling.py`** - Exception handling tests
   - Database errors
   - Validation errors
   - Authentication errors
   - Edge case inputs

### Test Configuration

- **`conftest.py`** - Test fixtures and configuration
- **`factories.py`** - Test data factories
- **`pytest.ini`** - Pytest configuration with markers
- **`requirements-test.txt`** - Test dependencies

## Running Tests

### Quick Start

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests with the test runner
python run_tests.py

# Run specific test categories
python run_tests.py -m unit          # Unit tests only
python run_tests.py -m integration   # Integration tests only
python run_tests.py -m edge_case     # Edge case tests only
```

### Manual Execution

```bash
# Set environment variables manually
export TESTING=true
export DATABASE_URL=sqlite:///:memory:

# Run with pytest directly
pytest tests/ -v --cov=app
```

### Test Categories (Markers)

- `unit` - Fast, isolated unit tests
- `integration` - Integration tests with database
- `auth` - Authentication and authorization tests
- `validation` - Input validation tests
- `edge_case` - Edge cases and error conditions
- `slow` - Performance and load tests

## Test Coverage

The test suite covers:

### API Endpoints
- ✅ User creation and retrieval
- ✅ Feature CRUD operations
- ✅ Voting endpoints (vote/unvote)
- ✅ Pagination and filtering
- ✅ Authentication middleware

### Database Operations
- ✅ Unique constraints (users, votes)
- ✅ Foreign key relationships
- ✅ Cascade operations
- ✅ Transaction integrity
- ✅ Concurrent access patterns

### Edge Cases
- ✅ SQL injection protection
- ✅ XSS prevention
- ✅ Large payload handling
- ✅ Unicode character support
- ✅ Malformed request handling
- ✅ Concurrent operations
- ✅ Race conditions

### Business Logic
- ✅ Duplicate vote prevention
- ✅ Vote count accuracy
- ✅ Feature sorting by votes
- ✅ User ownership validation
- ✅ Data consistency

## Test Data

The test suite uses:
- **Factory Boy** for consistent test data generation
- **Faker** for realistic fake data
- **In-memory SQLite** for fast test execution
- **Transactional isolation** for test independence

## Coverage Requirements

- Minimum coverage: 85% (configured in pytest.ini)
- Coverage reports generated in `htmlcov/` directory
- Terminal coverage summary included in test output

## Known Issues

Some tests may fail due to:
1. Missing voting API endpoints
2. Different HTTP status codes than expected
3. Validation rules not matching test assumptions

These failures help identify areas where the API implementation may need adjustment or where tests need to be updated to match actual behavior.

## Performance Tests

Integration tests include performance scenarios:
- Concurrent user operations
- Bulk data operations
- Database constraint verification under load
- Memory usage protection

## Security Tests

Comprehensive security testing includes:
- SQL injection attempts
- XSS attack vectors
- Authentication bypass attempts
- Input validation edge cases
- Unicode and special character handling

## Future Enhancements

- Add API contract testing with OpenAPI schemas
- Include mutation testing for test quality verification
- Add load testing with larger datasets
- Implement database migration testing
- Add API response time benchmarks