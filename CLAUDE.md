# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RadioForms is a desktop application for managing FEMA Incident Command System (ICS) forms. Built with modern web technologies wrapped in a native desktop application, it provides offline-first form management with multiple export formats for emergency management professionals.

**Current Status:** Documentation and specification phase - implementation ready to begin

## Technology Stack

- **Framework:** Tauri 1.5+ (Rust backend, web frontend)
- **Frontend:** React 18+ with TypeScript
- **UI Library:** Tailwind CSS + shadcn/ui components  
- **Database:** SQLite with Tauri SQL plugin
- **State Management:** Zustand for global state, React Query for server state
- **Forms:** React Hook Form with Zod validation
- **PDF Generation:** jsPDF for form exports
- **Build Tool:** Vite for fast development and building
- **Testing:** Vitest + React Testing Library + Playwright

## Architecture

The application follows a modern web-based architecture with native desktop integration:

### Frontend Layer (React/TypeScript)
- **React Components**: Modular, reusable UI components using shadcn/ui
- **TypeScript**: Type safety throughout the application
- **Tailwind CSS**: Utility-first styling framework
- **React Hook Form**: Performant form handling with Zod validation
- **Zustand**: Lightweight state management for UI state
- **React Query**: Server state management and caching

### IPC Layer (Tauri Commands)
- **Database Commands**: CRUD operations for forms and metadata
- **File System Commands**: Backup, restore, export operations
- **System Integration**: Native file dialogs, OS notifications

### Backend Layer (Rust)
- **SQLite Operations**: Database management with sqlx
- **File Management**: Backup/restore functionality
- **Export Engines**: PDF, JSON, and ICS-DES generation

### Data Flow
```
User Interaction → React Component → State Management → Tauri Command → 
Rust Handler → SQLite/File System → Response → State Update → UI Update
```

## Core Features

- Create, edit, and manage 20+ ICS forms (ICS-201 through ICS-225)
- Multiple export formats: PDF, JSON, ICS-DES (radio transmission)
- Offline-first operation with local SQLite database
- Dynamic form generation from JSON schemas
- Real-time validation with comprehensive business rules
- Version tracking and audit trail functionality
- Responsive design with accessibility support
- Keyboard shortcuts and native OS integration

## Development Guidelines

This project follows strict anti-complexity principles with comprehensive development rules:

### Core Philosophy

**The #1 Rule**: If it's not working simply, it won't work complexly.

#### Fundamental Principles
- **Simplicity First:** Start with the simplest solution that works, use native/built-in solutions before adding dependencies
- **Incremental Development:** Build one feature completely before starting the next, get user feedback before adding complexity
- **Pragmatic Engineering:** Choose boring, stable technology over bleeding edge, working code is better than perfect code
- **User Value First:** User feedback trumps developer assumptions, build for today's requirements not tomorrow's possibilities

### 🚨 Critical Anti-Patterns to Avoid

#### Premature Optimization
- ❌ DON'T implement advanced features (real-time, complex state management, micro-optimizations) before basic CRUD works
- ❌ DON'T optimize performance before establishing functionality
- ❌ DON'T add complex libraries (virtual scrolling, advanced caching) until proven necessary
- ✅ DO build incrementally: Basic functionality → Tests → Enhancements → Advanced features
- ✅ DO measure before optimizing

#### Over-Engineering
- ❌ DON'T create complex abstractions for simple problems
- ❌ DON'T add dependencies unless absolutely necessary
- ❌ DON'T implement features "just in case" or "for the future"
- ❌ DON'T create custom hooks for every piece of logic
- ❌ DON'T abstract everything into reusable components immediately
- ✅ DO use the simplest solution that works
- ✅ DO refactor only when complexity is proven necessary

#### Test Complexity
- ❌ DON'T create elaborate mocking systems
- ❌ DON'T write integration tests before unit tests work
- ❌ DON'T spend more time writing test infrastructure than tests
- ✅ DO write simple, fast tests that actually run (< 30 seconds total)
- ✅ DO mock only external dependencies (database, API calls, file system)

#### Dependency Chaos
- ❌ DON'T use alpha/beta/RC versions in production code
- ❌ DON'T adopt new major versions immediately (wait 3-6 months)
- ❌ DON'T add a dependency when native solutions exist
- ❌ DON'T add utility libraries (lodash, ramda) without justification
- ✅ DO use stable, well-tested versions
- ✅ DO audit and remove unused dependencies regularly

#### React Anti-Patterns
- ❌ DON'T create deeply nested component hierarchies
- ❌ DON'T pass data through many component layers (prop drilling)
- ❌ DON'T create components that do too many things
- ❌ DON'T use useEffect for everything
- ❌ DON'T create custom hooks for simple state
- ✅ DO keep components focused and simple
- ✅ DO use proper state management (local state > context > global store)

#### TypeScript Overuse
- ❌ DON'T create overly complex type definitions
- ❌ DON'T use advanced TypeScript features unless necessary
- ❌ DON'T spend hours making TypeScript happy instead of solving problems
- ✅ DO start with simple types and evolve them
- ✅ DO use `unknown` instead of `any` when you're unsure

### 📋 Development Workflow

#### Before Starting ANY Feature
**Ask yourself:**
1. [ ] Is the current code stable and tested?
2. [ ] Can this be done with existing dependencies?
3. [ ] Is this feature actually required now?
4. [ ] Have I written tests for existing features?
5. [ ] Can I explain this simply to a non-technical person?

#### Implementation Order (ALWAYS Follow This)

1. **Requirements Analysis**
   - Thoroughly understand user needs from their perspective
   - Act as a product manager to identify requirement gaps
   - Prioritize simple solutions that meet actual needs
   - Document what you're building and why

2. **Design & Planning**
   - Create/update README.md with project objectives
   - Document architecture decisions and rationale
   - Plan the simplest possible implementation
   - Identify what can be reused from existing code
   - ALWAYS use context7 mcp to review the latest official documentation for any tools, components, libraries, etc.

3. **Core Implementation**
   - Database schema and data models first
   - Basic CRUD operations with error handling
   - Type definitions and validation
   - Simple, working UI components
   - Wire components to backend

4. **Testing & Validation**
   - Unit tests for utilities and core logic
   - Component tests for UI behavior
   - Manual testing of happy paths
   - Tests must run in < 5 seconds individually

5. **Enhancement** (Only After Core Works)
   - Add validation and error handling
   - Implement search and filtering
   - Add permission systems
   - Improve UI/UX based on feedback

6. **Advanced Features** (Only After User Request)
   - Real-time updates
   - Offline functionality
   - Complex state management
   - Performance optimizations

#### Feature Complexity Guidelines
**Never implement Advanced features until:**
1. All Basic features are complete and tested
2. Intermediate features are stable
3. Users have specifically requested them
4. You have a rollback plan

**Complexity Levels:**
- **Basic (Do First)**: CRUD, forms, lists, authentication, basic UI
- **Intermediate (After Basic Works)**: Search, filters, validation, permissions, API integrations
- **Advanced (After User Feedback)**: Real-time updates, offline mode, AI features, complex visualizations

## Project Structure

```
src-tauri/               # Rust backend
├── src/
│   ├── commands/        # Tauri command handlers
│   ├── database/        # Database operations
│   ├── models/          # Data models
│   ├── exporters/       # Export functionality
│   └── main.rs          # Application entry point
├── migrations/          # Database migrations
└── Cargo.toml          # Rust dependencies

src/                    # React frontend
├── components/         # Reusable UI components
│   ├── ui/            # shadcn/ui base components
│   ├── forms/         # Form-specific components
│   ├── layout/        # Layout components
│   └── common/        # Shared utility components
├── pages/             # Page-level components
├── hooks/             # Custom React hooks
├── stores/            # Zustand state stores
├── services/          # Tauri command services
├── utils/             # Utility functions
├── types/             # TypeScript type definitions
├── schemas/           # Zod validation schemas
└── assets/            # Static assets

docs/                  # Comprehensive documentation
tests/                 # Test suite
```

## 🚩 Red Flags & Warning Signs

### You're Over-Engineering If:
- You're writing more infrastructure than features
- Tests take longer to write than the code
- You need a diagram to explain the data flow
- You're adding "just in case" functionality
- The PR/commit has more than 500 lines changed
- You can't demo the feature in 2 minutes
- New developers need more than 30 minutes to understand
- You're using TypeScript features you have to look up
- You're creating abstractions for fewer than 3 use cases

### When Complexity Creeps In:
1. **Stop immediately** - Complexity is a warning sign
2. **List assumptions** - What are you assuming users need?
3. **Simplify ruthlessly** - Can you remove half the code?
4. **Start over** - Sometimes a fresh approach is faster

## 🔧 Problem-Solving Approach

### When Things Don't Work:
1. **Simplify First**
   - Remove all optional features
   - Comment out complex logic
   - Get the minimal case working
   - Add complexity back incrementally

2. **Debug Systematically**
   - Review error messages carefully
   - Check browser console for errors
   - Use React Developer Tools
   - Isolate the problem area
   - Test assumptions with simple cases

3. **When Stuck:**
   - Can you explain the problem in one sentence?
   - What's the simplest thing that could work?
   - What would you do with unlimited time? Now do 10% of that
   - Is there existing code that solves a similar problem?

## 📊 Success Metrics

### Your Code is Successful When:
- New developers understand it in < 30 minutes
- Tests run in < 30 seconds
- Features can be demo'd immediately
- Users actually use what you built
- Bugs are easy to find and fix
- Adding features doesn't break existing ones
- Components can be reused without modification
- TypeScript helps instead of hindering development

### Project Health Indicators:
- ✅ Clear, updated documentation
- ✅ All tests passing
- ✅ No TypeScript errors or warnings
- ✅ Dependencies are current and minimal
- ✅ Code follows consistent patterns
- ✅ Features match user needs (not developer wants)
- ✅ Fast development feedback loops
- ✅ Predictable component behavior

## 🎯 Decision Framework

### When Making Technical Decisions:

1. **Choose Boring Technology**
   - Proven solutions over new experiments
   - Well-documented over cutting-edge
   - Community support over unique features
   - React patterns over custom solutions

2. **Minimize Technical Debt**
   - Fix issues immediately, not "later"
   - Refactor when patterns emerge, not preemptively
   - Keep dependencies updated monthly
   - Remove unused code and dependencies

3. **Maximize Maintainability**
   - Code for the next developer (it might be you)
   - Prefer clarity over performance (until measured)
   - Document why, not just what
   - Use TypeScript to catch errors, not to show off

### Dependency Management Rules

#### Before Adding ANY Dependency:
- Is there a native/built-in solution?
- Is it well-maintained (check last update, issues, downloads)?
- Is it compatible with current versions?
- Have you tested it in isolation first?
- Can you implement the needed functionality yourself in < 100 lines?

#### Dependency Health Checks:
- Monthly audit of all dependencies
- Remove unused dependencies immediately
- Document why each dependency is needed
- Prefer fewer, well-established packages

## 🌐 Web Development Specific Guidelines

### React Best Practices

#### Component Design
```typescript
// ✅ Good: Simple, focused component
interface ButtonProps {
  children: React.ReactNode;
  onClick: () => void;
  variant?: 'primary' | 'secondary';
}

const Button: React.FC<ButtonProps> = ({ children, onClick, variant = 'primary' }) => {
  return (
    <button 
      className={`btn btn-${variant}`}
      onClick={onClick}
    >
      {children}
    </button>
  );
};

// ❌ Bad: Overly complex component
const SuperButton = ({ children, onClick, variant, size, icon, loading, disabled, tooltip, ...props }) => {
  // 50+ lines of complex logic
};
```

#### State Management Progression
```typescript
// ✅ Good: Start with local state
const [count, setCount] = useState(0);

// ✅ Good: Use context for related data
const UserContext = createContext<User | null>(null);

// ✅ Good: Use store for global state
const useAppStore = create<AppStore>((set) => ({
  theme: 'light',
  setTheme: (theme) => set({ theme }),
}));

// ❌ Bad: Everything in global store
const useEverythingStore = create(() => ({
  users, posts, comments, notifications, ui, settings, cache, ...
}));
```

#### Custom Hooks Best Practices
```typescript
// ✅ Good: Simple, reusable logic
const useLocalStorage = <T>(key: string, defaultValue: T) => {
  const [value, setValue] = useState<T>(() => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch {
      return defaultValue;
    }
  });
  
  const setStoredValue = (value: T) => {
    setValue(value);
    localStorage.setItem(key, JSON.stringify(value));
  };
  
  return [value, setStoredValue] as const;
};

// ❌ Bad: Complex hook doing too much
const useEverything = () => {
  // 100+ lines managing multiple concerns
};
```

### TypeScript Best Practices

#### Type Definitions
```typescript
// ✅ Good: Simple, clear types
interface User {
  id: number;
  name: string;
  email: string;
}

interface FormData {
  id?: number;
  formType: ICSFormType;
  incidentName: string;
  data: Record<string, unknown>;
}

// ❌ Bad: Overly complex types
type ComplexType<T extends Record<string, any>, K extends keyof T> = {
  [P in K]: T[P] extends infer U ? U extends string ? `prefix_${U}` : never : never;
};
```

#### Error Handling
```typescript
// ✅ Good: Simple error handling
const fetchUser = async (id: number): Promise<User | null> => {
  try {
    const response = await api.get(`/users/${id}`);
    return response.data;
  } catch (error) {
    console.error('Failed to fetch user:', error);
    return null;
  }
};

// ❌ Bad: Overly complex error handling
const fetchUserComplex = async <T extends UserLike>(
  id: number,
  options: FetchOptions<T>
): Promise<Result<T, ErrorType[]>> => {
  // Complex error handling logic
};
```

### Styling Best Practices

#### Tailwind CSS Usage
```tsx
// ✅ Good: Simple, semantic classes
<div className="flex items-center gap-4 p-4 bg-white rounded-lg shadow">
  <button className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
    Save
  </button>
</div>

// ❌ Bad: Overly complex utility classes
<div className="flex items-center justify-between lg:justify-start xl:justify-center gap-2 sm:gap-4 lg:gap-6 p-2 sm:p-4 lg:p-6 bg-gradient-to-r from-blue-50 via-white to-blue-50 rounded-sm sm:rounded lg:rounded-xl shadow-sm hover:shadow-md transition-all duration-300 ease-in-out">
```

#### Component Styling
```typescript
// ✅ Good: Use established component library
import { Button, Card, Input } from '@/components/ui';

// ✅ Good: Simple custom components when needed
const FormField = ({ label, children, error }) => (
  <div className="space-y-2">
    <label className="text-sm font-medium">{label}</label>
    {children}
    {error && <p className="text-sm text-red-600">{error}</p>}
  </div>
);

// ❌ Bad: Complex styling logic
const ComplexFormField = ({ variant, size, theme, animation, ... }) => {
  // Complex styling calculations
};
```

## Development Commands

### Setup
```bash
# Install Rust (required for Tauri)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Install Node.js dependencies
npm install

# Install Tauri CLI
npm install -g @tauri-apps/cli

# Create initial database and run migrations
npm run db:setup
npm run db:migrate
```

### Development
```bash
# Start development server
npm run tauri dev

# Build for production
npm run tauri build

# Run frontend tests
npm run test

# Run frontend tests with UI
npm run test:ui

# Run Rust tests
cargo test

# Run end-to-end tests
npm run test:e2e
```

### Database
```bash
# Run database migrations
npm run db:migrate

# Reset database (development only)
npm run db:reset

# Generate database types
npm run db:generate-types
```

### Linting and Formatting
```bash
# Lint and fix frontend code
npm run lint
npm run lint:fix

# Format frontend code
npm run format

# Lint Rust code
cargo clippy

# Format Rust code
cargo fmt
```

## Key Documentation

- `docs/prd.md` - Product Requirements Document
- `docs/tdd.md` - Technical Design Document  
- `docs/generic-rules.md` - Development coding standards
- `docs/ics-des.md` - Radio transmission data encoding spec
- `docs/ICS-Forms-Analysis-Summary.md` - Analysis of all ICS forms
- `docs/ui.md` - UI/UX design guidelines

## Form Data Standards

The application handles ICS forms with specific requirements:
- Forms must validate against FEMA ICS standards
- Support for ICS-DES encoding for low-bandwidth transmission
- JSON export for data interchange
- PDF export matching official FEMA layouts
- Dynamic form generation from JSON schemas
- Comprehensive validation rules per form type

## Database Schema

Core entities:
- **forms**: Main form instances with JSON data storage
- **form_templates**: Schema definitions for each ICS form type
- **form_audit**: Change tracking for data integrity
- **app_settings**: Application configuration
- **schema_migrations**: Database version tracking

## State Management

### Zustand Stores
- **AppStore**: UI state, theme, sidebar, current database
- **FormsStore**: Form data, templates, CRUD operations
- **SettingsStore**: Application preferences and configuration

### React Query
- Form data fetching and caching
- Optimistic updates for form operations
- Background data synchronization
- Error handling and retry logic

## Testing Strategy

### Frontend Testing
- **Unit Tests**: Component logic with Vitest + React Testing Library
- **Integration Tests**: Form workflows and data flow
- **E2E Tests**: Complete user workflows with Playwright
- **Accessibility Tests**: WCAG compliance verification

### Backend Testing
- **Unit Tests**: Database operations and business logic
- **Integration Tests**: Tauri command handlers
- **Export Tests**: PDF, JSON, and ICS-DES generation
- **Database Tests**: Migration and schema validation

## Security Considerations

- Local SQLite database with optional encryption
- No network communication required for core functionality
- Input sanitization and validation at all layers
- SQL injection prevention via parameter binding
- XSS prevention via React's built-in escaping
- Audit trail for all form modifications
- Data integrity verification with checksums

## Performance Guidelines

- Lazy load large component trees
- Virtualize long lists (>100 items)
- Memoize expensive calculations
- Use React.memo for stable components
- Implement cursor-based pagination for large datasets
- Optimize database queries with proper indexing
- Bundle size monitoring and code splitting

## Accessibility Requirements

- WCAG 2.1 AA compliance
- Keyboard navigation for all functionality
- Screen reader compatibility
- Proper ARIA labels and roles
- Color contrast meeting accessibility standards
- Focus management and visual indicators
- Responsive design for various screen sizes and zoom levels

## 💡 Best Practices Summary

### Always:
- ✅ Build features incrementally
- ✅ Test as you go
- ✅ Get user feedback early
- ✅ Keep it simple
- ✅ Document decisions
- ✅ Remove unused code/dependencies
- ✅ Use TypeScript for safety, not complexity
- ✅ Prefer composition over inheritance
- ✅ Write code that reads like prose

### Never:
- ❌ Add features users haven't asked for
- ❌ Use unstable dependencies
- ❌ Write placeholder/stubbed code
- ❌ Duplicate code instead of refactoring
- ❌ Sacrifice clarity for cleverness
- ❌ Skip testing to "save time"
- ❌ Create abstractions for single use cases
- ❌ Ignore TypeScript errors
- ❌ Use complex state management for simple problems

## 🏁 Final Checklist

Before considering any feature "done":
- [ ] Does it solve the user's actual problem?
- [ ] Can you demo it in 2 minutes?
- [ ] Are all tests passing?
- [ ] Is the code self-documenting?
- [ ] Have you removed all unused code?
- [ ] Would a new developer understand it?
- [ ] Is it the simplest solution that works?
- [ ] Does TypeScript help or hinder?
- [ ] Can components be reused easily?
- [ ] Is the state management appropriate for the complexity?

## 🌐 Web-Specific Reminders

### React Development:
- Start with function components and hooks
- Use local state first, then context, then global store
- Keep components small and focused
- Test user interactions, not implementation details
- Use semantic HTML elements
- Implement proper loading and error states

### TypeScript Development:
- Start with simple types and evolve them
- Use strict mode and fix all errors
- Prefer interfaces over types for object shapes
- Use union types for known possibilities
- Don't fight TypeScript - if it's hard, simplify

### Performance:
- Don't optimize until you measure
- Use React.memo only when proven necessary
- Lazy load routes and large components
- Virtualize lists only when they're large (>100 items)
- Use React Developer Tools Profiler

## Remember

> "Perfection is achieved not when there is nothing more to add, but when there is nothing left to take away." - Antoine de Saint-Exupéry

**Focus on:**
- User value over technical elegance
- Simplicity over sophistication
- Today's problems over tomorrow's possibilities
- Maintenance over features
- Clarity over cleverness
- Working software over perfect architecture

**The goal is not to build the most technically impressive solution, but to solve real problems with the least complexity possible.**