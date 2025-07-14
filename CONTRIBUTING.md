# Contributing to AgentArena

[![Contributors Welcome](https://img.shields.io/badge/Contributors-Welcome-brightgreen.svg)](README.md)
[![Code Quality](https://img.shields.io/badge/Code%20Quality-A+-brightgreen.svg)](ARCHITECTURE.md)
[![Development](https://img.shields.io/badge/Development-Active-blue.svg)](README.md)

> **Welcome Contributors!** - We're excited you're interested in contributing to AgentArena. This guide will help you get started with contributing to our AI agent evaluation platform.

---

## 📋 Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contribution Guidelines](#contribution-guidelines)
- [Code Standards](#code-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation Standards](#documentation-standards)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Community Guidelines](#community-guidelines)
- [Recognition](#recognition)

---

## 🚀 Getting Started

### Prerequisites

Before contributing, ensure you have:

- **Python 3.11+** for backend development
- **Node.js 18+** for frontend development
- **Docker & Docker Compose** for containerized development
- **Git** for version control
- **Basic knowledge** of FastAPI, React, and SQLAlchemy

### First Contribution

1. **🍴 Fork** the repository
2. **📥 Clone** your fork locally
3. **🔧 Set up** the development environment
4. **🌿 Create** a feature branch
5. **✨ Make** your changes
6. **🧪 Test** your changes
7. **📝 Document** your changes
8. **🔀 Submit** a pull request

---

## 🛠️ Development Setup

### Quick Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/agentarena.git
cd agentarena

# Set up environment
chmod +x start_platform.sh
./start_platform.sh
```

### Manual Setup

#### Backend Development

```bash
# Navigate to server directory
cd Server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python setup_database.py

# Start development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Development

```bash
# Navigate to client directory
cd client

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your configuration

# Start development server
npm run dev
```

#### Docker Development

```bash
# Build and start all services
docker-compose -f docker-compose.dev.yml up --build

# Run in background
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Development Tools

#### Code Quality Tools

```bash
# Backend (Python)
pip install black flake8 mypy pytest-cov

# Frontend (JavaScript/TypeScript)
npm install -D prettier eslint @typescript-eslint/eslint-plugin
```

#### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

---

## 📝 Contribution Guidelines

### Types of Contributions

We welcome the following types of contributions:

#### 🐛 Bug Fixes
- Fix existing functionality that isn't working as expected
- Include tests that reproduce the bug
- Provide clear description of the issue and solution

#### ✨ Feature Development
- Implement new features described in our roadmap
- Propose new features through issues first
- Include comprehensive tests and documentation

#### 📚 Documentation
- Improve existing documentation
- Add missing documentation
- Create tutorials and guides
- Fix typos and improve clarity

#### 🧪 Testing
- Add missing test coverage
- Improve existing tests
- Add integration tests
- Performance testing

#### 🎨 UI/UX Improvements
- Enhance user interface design
- Improve user experience
- Fix accessibility issues
- Mobile responsiveness

#### ⚡ Performance Optimizations
- Database query optimizations
- Frontend performance improvements
- API response time improvements
- Memory usage optimizations

### Contribution Process

1. **Check existing issues** to avoid duplicate work
2. **Create an issue** to discuss major changes
3. **Fork the repository** and create a feature branch
4. **Follow coding standards** outlined in this guide
5. **Write comprehensive tests** for your changes
6. **Update documentation** as needed
7. **Submit a pull request** with clear description

---

## 🎯 Code Standards

### Python Code Standards

#### Style Guide

```python
# Use type hints for all functions
from typing import Optional, List, Dict, Any
from uuid import UUID

async def get_agent(agent_id: UUID) -> Optional[Agent]:
    """
    Retrieve an agent by ID.
    
    Args:
        agent_id: The unique identifier for the agent
        
    Returns:
        The agent if found, None otherwise
        
    Raises:
        DatabaseException: If database query fails
    """
    try:
        return await agent_repository.get_by_id(agent_id)
    except Exception as e:
        logger.error(f"Failed to get agent {agent_id}: {e}")
        raise DatabaseException(f"Failed to retrieve agent: {e}")
```

#### Code Formatting

```bash
# Format code with Black
black Server/app/

# Sort imports with isort
isort Server/app/

# Lint with flake8
flake8 Server/app/

# Type check with mypy
mypy Server/app/
```

#### Naming Conventions

- **Classes**: PascalCase (`AgentService`, `UserRepository`)
- **Functions/Methods**: snake_case (`get_agent`, `create_submission`)
- **Variables**: snake_case (`user_id`, `agent_config`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_RETRIES`, `DEFAULT_TIMEOUT`)
- **Files/Modules**: snake_case (`agent_service.py`, `user_repository.py`)

#### Documentation Standards

```python
class AgentService:
    """Service for managing AI agents.
    
    This service handles all business logic related to agent management,
    including creation, updates, and performance tracking.
    
    Attributes:
        repository: Repository for agent data access
        cache: Caching service for performance optimization
    """
    
    def __init__(self, repository: AgentRepository, cache: CacheService):
        """Initialize the agent service.
        
        Args:
            repository: Agent repository instance
            cache: Cache service instance
        """
        self.repository = repository
        self.cache = cache
    
    async def create_agent(self, agent_data: AgentCreate) -> Agent:
        """Create a new agent.
        
        Args:
            agent_data: Agent creation data
            
        Returns:
            The created agent instance
            
        Raises:
            ValidationException: If agent data is invalid
            DatabaseException: If database operation fails
        """
        # Implementation here
        pass
```

### JavaScript/TypeScript Standards

#### Code Style

```typescript
// Use TypeScript for type safety
interface Agent {
  id: string;
  name: string;
  agentType: string;
  configuration: Record<string, any>;
  createdAt: string;
  updatedAt: string;
}

// Use async/await for promises
const createAgent = async (agentData: AgentCreate): Promise<Agent> => {
  try {
    const response = await agentService.createAgent(agentData);
    return response.data;
  } catch (error) {
    logger.error('Failed to create agent:', error);
    throw new Error('Agent creation failed');
  }
};

// Use functional components with hooks
const AgentCard: React.FC<AgentCardProps> = ({ agent, onEdit, onDelete }) => {
  const [isLoading, setIsLoading] = useState(false);
  
  const handleEdit = useCallback(async () => {
    setIsLoading(true);
    try {
      await onEdit(agent.id);
    } finally {
      setIsLoading(false);
    }
  }, [agent.id, onEdit]);
  
  return (
    <Card className="agent-card">
      {/* Component JSX */}
    </Card>
  );
};
```

#### Formatting

```bash
# Format code with Prettier
npm run format

# Lint with ESLint
npm run lint

# Type check
npm run type-check
```

### Database Standards

#### Migration Guidelines

```python
# migrations/versions/001_create_agents_table.py
"""Create agents table

Revision ID: 001
Revises: 
Create Date: 2024-01-15 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Create agents table."""
    op.create_table(
        'agents',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('agent_type', sa.String(50), nullable=False),
        sa.Column('configuration', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    
    # Create indexes
    op.create_index('idx_agents_user_id', 'agents', ['user_id'])
    op.create_index('idx_agents_type', 'agents', ['agent_type'])

def downgrade():
    """Drop agents table."""
    op.drop_table('agents')
```

---

## 🧪 Testing Guidelines

### Backend Testing

#### Test Structure

```python
# tests/test_agent_service.py
import pytest
from unittest.mock import AsyncMock, Mock
from uuid import UUID

from app.services.agent_service import AgentService
from app.schemas.agent_schema import AgentCreate
from app.models.agent import Agent

class TestAgentService:
    """Test suite for AgentService."""
    
    @pytest.fixture
    def mock_repository(self):
        """Create mock repository."""
        repository = AsyncMock()
        repository.create.return_value = Agent(
            id=UUID("12345678-1234-5678-9012-123456789012"),
            name="Test Agent",
            agent_type="gpt-4"
        )
        return repository
    
    @pytest.fixture
    def agent_service(self, mock_repository):
        """Create agent service with mock repository."""
        return AgentService(mock_repository)
    
    async def test_create_agent_success(self, agent_service, mock_repository):
        """Test successful agent creation."""
        # Arrange
        agent_data = AgentCreate(
            name="Test Agent",
            agent_type="gpt-4",
            configuration={}
        )
        
        # Act
        result = await agent_service.create_agent(agent_data)
        
        # Assert
        assert result.name == "Test Agent"
        assert result.agent_type == "gpt-4"
        mock_repository.create.assert_called_once()
    
    async def test_create_agent_validation_error(self, agent_service):
        """Test agent creation with invalid data."""
        # Arrange
        invalid_data = AgentCreate(
            name="",  # Invalid: empty name
            agent_type="invalid-type",  # Invalid: unsupported type
            configuration={}
        )
        
        # Act & Assert
        with pytest.raises(ValidationException):
            await agent_service.create_agent(invalid_data)
```

#### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_agent_service.py

# Run specific test method
pytest tests/test_agent_service.py::TestAgentService::test_create_agent_success

# Run tests in parallel
pytest -n auto
```

### Frontend Testing

#### Component Testing

```typescript
// components/__tests__/AgentCard.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import AgentCard from '../AgentCard';

describe('AgentCard', () => {
  const mockAgent = {
    id: '1',
    name: 'Test Agent',
    agentType: 'gpt-4',
    configuration: {},
    createdAt: '2024-01-15T10:30:00Z',
    updatedAt: '2024-01-15T10:30:00Z'
  };
  
  const mockProps = {
    agent: mockAgent,
    onEdit: vi.fn(),
    onDelete: vi.fn(),
    onTest: vi.fn()
  };
  
  beforeEach(() => {
    vi.clearAllMocks();
  });
  
  it('renders agent information correctly', () => {
    render(<AgentCard {...mockProps} />);
    
    expect(screen.getByText('Test Agent')).toBeInTheDocument();
    expect(screen.getByText('gpt-4')).toBeInTheDocument();
  });
  
  it('calls onEdit when edit button is clicked', async () => {
    render(<AgentCard {...mockProps} />);
    
    const editButton = screen.getByRole('button', { name: /edit/i });
    fireEvent.click(editButton);
    
    await waitFor(() => {
      expect(mockProps.onEdit).toHaveBeenCalledWith('1');
    });
  });
  
  it('calls onDelete when delete button is clicked', async () => {
    render(<AgentCard {...mockProps} />);
    
    const deleteButton = screen.getByRole('button', { name: /delete/i });
    fireEvent.click(deleteButton);
    
    await waitFor(() => {
      expect(mockProps.onDelete).toHaveBeenCalledWith('1');
    });
  });
});
```

#### Running Frontend Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm test AgentCard.test.tsx
```

### Test Coverage Requirements

- **Backend**: Minimum 80% code coverage
- **Frontend**: Minimum 75% code coverage
- **Critical paths**: 100% coverage required
- **New features**: Must include comprehensive tests

---

## 📚 Documentation Standards

### API Documentation

Use OpenAPI/Swagger for API documentation:

```python
@router.post("/agents", response_model=AgentResponse)
async def create_agent(
    agent_data: AgentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new agent.
    
    This endpoint allows authenticated users to create new AI agents
    with custom configurations for evaluation tasks.
    
    Args:
        agent_data: Agent creation data including name, type, and configuration
        current_user: Currently authenticated user
        db: Database session
    
    Returns:
        AgentResponse: Created agent with generated ID and timestamps
    
    Raises:
        HTTPException: 400 if validation fails
        HTTPException: 409 if agent name already exists
        HTTPException: 422 if request data is invalid
    
    Example:
        ```python
        agent_data = {
            "name": "My GPT-4 Agent",
            "agent_type": "gpt-4",
            "configuration": {
                "temperature": 0.7,
                "max_tokens": 2000
            }
        }
        ```
    """
    # Implementation here
    pass
```

### Code Comments

```python
# Good comments explain WHY, not WHAT
def calculate_agent_score(submissions: List[Submission]) -> float:
    """Calculate weighted agent performance score."""
    if not submissions:
        return 0.0
    
    # Weight recent submissions more heavily to reflect current performance
    weights = [0.5 + (i * 0.1) for i in range(len(submissions))]
    
    # Normalize scores to 0-100 range for consistent comparison
    normalized_scores = [min(100, max(0, s.score)) for s in submissions]
    
    weighted_sum = sum(score * weight for score, weight in zip(normalized_scores, weights))
    total_weight = sum(weights)
    
    return weighted_sum / total_weight
```

### README Updates

When adding new features, update relevant README sections:

- **Features section** for new capabilities
- **Installation section** for new dependencies
- **Configuration section** for new environment variables
- **Usage section** for new functionality

---

## 🔀 Pull Request Process

### Before Submitting

1. **✅ Code Quality**
   - [ ] Code follows style guidelines
   - [ ] All tests pass locally
   - [ ] No linting errors
   - [ ] Type checking passes

2. **✅ Testing**
   - [ ] New features have tests
   - [ ] Bug fixes include regression tests
   - [ ] Test coverage meets requirements

3. **✅ Documentation**
   - [ ] Code is well-documented
   - [ ] API changes are documented
   - [ ] README updated if needed

### Pull Request Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review
- [ ] I have commented my code, particularly hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally

## Screenshots (if applicable)
Add screenshots for UI changes.

## Additional Notes
Any additional information for reviewers.
```

### Review Process

1. **🔍 Automated Checks**
   - CI/CD pipeline runs
   - Code quality checks
   - Security scans
   - Test execution

2. **👥 Code Review**
   - At least 2 reviewers required
   - Focus on code quality, logic, and maintainability
   - Constructive feedback

3. **✅ Approval**
   - All checks pass
   - Reviewers approve
   - Merge to main branch

---

## 🐛 Issue Reporting

### Bug Reports

Use the bug report template:

```markdown
**Bug Description**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
 - OS: [e.g. macOS, Windows, Linux]
 - Browser [e.g. chrome, safari] (if applicable)
 - Version [e.g. 22]

**Additional Context**
Add any other context about the problem here.
```

### Feature Requests

Use the feature request template:

```markdown
**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is.

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions.

**Additional context**
Add any other context or screenshots about the feature request here.
```

---

## 🤝 Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inspiring community for all. Please:

- **Be respectful** and inclusive
- **Be constructive** in feedback and discussions
- **Be collaborative** and help others learn
- **Be patient** with newcomers

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and community chat
- **Pull Requests**: Code review and collaboration

### Getting Help

1. **Check documentation** first
2. **Search existing issues** for similar problems
3. **Ask in discussions** for general questions
4. **Create an issue** for bugs or feature requests

---

## 🏆 Recognition

### Contributors

We recognize contributions in several ways:

- **Contributors file**: Listed in CONTRIBUTORS.md
- **Release notes**: Mentioned in version releases
- **GitHub profile**: Contribution activity visible
- **Community recognition**: Featured in project updates

### Types of Recognition

- **🐛 Bug Hunters**: Finding and reporting critical bugs
- **✨ Feature Developers**: Implementing new functionality
- **📚 Documentation Writers**: Improving project documentation
- **🧪 Test Engineers**: Improving test coverage and quality
- **🎨 Design Contributors**: UI/UX improvements
- **🛠️ DevOps Engineers**: Infrastructure and deployment improvements

---

## 📞 Contact

### Maintainers

- **Core Team**: Available through GitHub issues and discussions
- **Community Manager**: Handles community questions and feedback

### Response Times

- **Bug reports**: 24-48 hours
- **Feature requests**: 3-5 days
- **Pull requests**: 2-3 days
- **Security issues**: Same day

---

**Thank you for contributing to AgentArena! 🎉**

Your contributions help make AI agent evaluation better for everyone. Whether you're fixing a bug, adding a feature, or improving documentation, every contribution matters.

---

**Happy coding! 🚀**