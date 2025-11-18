# Contributing to Entra

Thank you for your interest in contributing to the Entra AI Advisor Platform!

## Development Setup

See [SETUP.md](./SETUP.md) for complete setup instructions.

Quick start:
```bash
make install
make dev
```

## Code Standards

### TypeScript/Next.js (Frontend)

- Use TypeScript for all files
- Follow Airbnb style guide
- Use functional components with hooks
- Prefer composition over inheritance
- Write self-documenting code

Example:
```typescript
// Good
interface UserProfile {
  id: string;
  email: string;
  fullName: string;
}

export function UserCard({ user }: { user: UserProfile }) {
  return <div>{user.fullName}</div>;
}

// Bad
export function UserCard(props: any) {
  return <div>{props.user.fullName}</div>;
}
```

### Python/FastAPI (Backend)

- Use type hints for all functions
- Follow PEP 8 style guide
- Use Black for formatting
- Use Ruff for linting
- Write docstrings for all public functions

Example:
```python
# Good
async def calculate_runway(
    cash_balance: float,
    monthly_burn: float
) -> float:
    """
    Calculate runway in months.

    Args:
        cash_balance: Current cash balance
        monthly_burn: Monthly burn rate

    Returns:
        Runway in months
    """
    if monthly_burn <= 0:
        return float("inf")
    return cash_balance / monthly_burn

# Bad
def calculate_runway(cash, burn):
    return cash / burn
```

## Git Workflow

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make changes**
4. **Run tests**
   ```bash
   make test
   make lint
   ```
5. **Commit with conventional commits**
   ```bash
   git commit -m "feat: add new finance calculation"
   git commit -m "fix: resolve tax calculation bug"
   git commit -m "docs: update README"
   ```
6. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

**Examples:**
```
feat(agents): add real estate valuation agent
fix(tax): correct GST calculation for India
docs(setup): add Docker setup instructions
refactor(rag): improve document chunking logic
```

## Testing

### Frontend Tests

```bash
# Run all tests
pnpm test

# Run specific test file
pnpm test UserCard.test.tsx

# Watch mode
pnpm test:watch
```

### Backend Tests

```bash
# Run all tests
cd apps/agents && pytest tests/

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test
pytest tests/test_finance_agent.py -v
```

### Writing Tests

**Frontend:**
```typescript
import { render, screen } from '@testing-library/react';
import { UserCard } from './UserCard';

describe('UserCard', () => {
  it('renders user name', () => {
    const user = { id: '1', email: 'test@test.com', fullName: 'John Doe' };
    render(<UserCard user={user} />);
    expect(screen.getByText('John Doe')).toBeInTheDocument();
  });
});
```

**Backend:**
```python
import pytest
from app.agents.finance_agent import FinanceAgent
from app.models.schemas import AgentTask

@pytest.mark.asyncio
async def test_finance_agent_runway_calculation():
    agent = FinanceAgent()
    task = AgentTask(
        task_id="test",
        agent_type="finance",
        question="Calculate runway",
        context={"company_data": {"cash_balance": 100000, "monthly_expenses": 10000}},
        user_id="user123",
        company_id="comp123"
    )

    result = await agent.process(task)

    assert result.data["runway_months"] == 10.0
    assert "10 months" in result.answer.lower()
```

## Adding New Features

### Adding a New Specialist Agent

1. **Create agent file**: `apps/agents/app/agents/your_agent.py`

```python
from app.agents.base_agent import BaseAgent
from app.models.schemas import AgentTask, AgentResponse

class YourAgent(BaseAgent):
    @property
    def agent_type(self) -> str:
        return "your_agent"

    @property
    def system_prompt(self) -> str:
        return """You are an expert in..."""

    async def process(self, task: AgentTask) -> AgentResponse:
        # Your logic here
        insights = await self._call_llm(task.question, task.context)

        return AgentResponse(
            task_id=task.task_id,
            agent_type=self.agent_type,
            answer=insights,
            confidence=0.8,
        )
```

2. **Add to orchestrator**: Update `apps/agents/app/orchestrator/main.py`

3. **Add API endpoint**: Update `apps/agents/app/api/agents.py`

4. **Write tests**: Create `tests/test_your_agent.py`

5. **Update documentation**

### Adding a New Tool

1. **Create tool file**: `apps/agents/app/tools/your_tool.py`

```python
def your_calculation(param1: float, param2: float) -> dict:
    """
    Your calculation description.

    Args:
        param1: Description
        param2: Description

    Returns:
        Result dictionary
    """
    result = param1 + param2

    return {
        "result": result,
        "methodology": "Description",
    }
```

2. **Import in agent**: Use in relevant agent

3. **Write tests**

## Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new features
3. **Ensure CI passes**
4. **Request review** from maintainers
5. **Address feedback**
6. **Squash commits** if requested

## Code Review Guidelines

### For Authors

- Keep PRs focused and small
- Write descriptive PR descriptions
- Link related issues
- Respond to feedback promptly

### For Reviewers

- Be constructive and respectful
- Focus on code quality, not style
- Ask questions, don't command
- Approve when ready

## Release Process

1. Update version in `package.json` and `pyproject.toml`
2. Update CHANGELOG.md
3. Create release tag
4. Deploy to production

## Questions?

- Open a GitHub Discussion
- Ask in pull request comments
- Check existing issues

Thank you for contributing! 🎉
