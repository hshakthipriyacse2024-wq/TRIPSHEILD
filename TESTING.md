# TripShield AI — Testing Guide

## Testing Strategy

TripShield AI uses a three-layer testing approach:

1. **Unit Tests** — Individual engines, services, and utilities
2. **Integration Tests** — API endpoints with database
3. **End-to-End Tests** — Complete user workflows

## Backend Tests (pytest)

### Setup

```bash
cd backend
pip install pytest httpx
```

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_ripple_impact.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

### Test Categories

#### Unit Tests

**test_ripple_impact.py** — Ripple Impact Engine
- Test BFS traversal identifies correct downstream nodes
- Test time conflict detection with various delays
- Test location conflict detection
- Test connection feasibility calculation
- Test financial exposure calculation
- Test severity classification (0-20=low, 21-40=moderate, etc.)
- Test configurable weights produce different scores
- Test edge case: no downstream nodes
- Test edge case: all nodes affected

**test_recovery.py** — Recovery Optimizer
- Test strategy generation produces multiple options
- Test preference-weighted scoring
- Test different preference profiles produce different rankings
- Test explanation generation from actual values
- Test feasibility scoring
- Test cost calculation correctness

**test_resilience.py** — Resilience Scorer
- Test score calculation with high-resilience journey
- Test score calculation with vulnerable journey
- Test classification thresholds
- Test individual component scoring
- Test explanation generation

**test_auth.py** — Authentication
- Test password hashing and verification
- Test JWT token creation and decoding
- Test expired token handling
- Test invalid token handling
- Test role-based access control

#### Integration Tests

**test_api.py** — API Endpoints
- Test user registration (POST /auth/register)
- Test user login (POST /auth/login)
- Test journey CRUD operations
- Test node CRUD operations
- Test dependency creation
- Test disruption creation triggers impact analysis
- Test recovery generation
- Test recovery approval and execution
- Test notification creation
- Test audit log creation
- Test health endpoint
- Test unauthorized access returns 401
- Test wrong role returns 403

#### End-to-End Tests

**test_e2e.py** — Complete Workflow
```
1. Register user
2. Login
3. Create journey
4. Add 5 nodes (flight, transfer, hotel, activity, restaurant)
5. Add 4 dependencies
6. Verify digital twin data
7. Calculate resilience score
8. Create disruption (4-hour flight delay)
9. Verify impact analysis was created
10. Verify affected nodes status changed
11. Generate recovery strategies
12. Verify multiple strategies returned
13. Verify strategies are ranked
14. Approve top strategy
15. Execute recovery
16. Verify node statuses changed to 'recovered'
17. Verify journey status changed to 'recovered'
18. Verify notifications were created
19. Verify audit logs were created
```

## Frontend Tests

### Setup

```bash
cd frontend
npm install --save-dev @testing-library/react @testing-library/jest-dom vitest
```

### Test Files

- Component rendering tests
- User interaction tests
- API integration mock tests

## Test Data

Tests use isolated in-memory SQLite databases. Each test gets a fresh database to ensure independence.

```python
@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
```

## Continuous Integration

The test suite should run on every commit:

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r backend/requirements.txt
      - run: pip install pytest httpx
      - run: cd backend && pytest tests/ -v

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: cd frontend && npm ci
      - run: cd frontend && npm test
```
