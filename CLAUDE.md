# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RadioForms is a production-ready desktop application for managing FEMA Incident Command System (ICS) forms. Built with modern web technologies wrapped in a native desktop application, it provides offline-first form management with multiple export formats for emergency management professionals.

**Current Status:** Production-ready foundation with real Rust backend - ready for feature development

## Technology Stack

- **Framework:** Tauri 2.x (Rust backend, web frontend)
- **Frontend:** React 18+ with TypeScript 5.8+
- **UI Library:** Enterprise UI/UX System (based on ui-ux-spec-complete.md)
- **Database:** SQLite 3.x with SQLx 0.8+
- **State Management:** Zustand for global state
- **Forms:** React Hook Form with Zod validation
- **PDF Generation:** jsPDF 3.x+ (secure version)
- **Build Tool:** Vite 6.x for fast development and building
- **Testing:** Vitest 3.x + React Testing Library + Playwright
- **Linting:** ESLint 9.x with flat config (modern)

## Architecture

The application follows a modern web-based architecture with native desktop integration:

### Frontend Layer (React/TypeScript)
- **React Components**: Modular, reusable UI components following Enterprise UI spec
- **TypeScript**: Type safety throughout the application (5.8+)
- **Enterprise UI System**: Professional design system for business applications
- **React Hook Form**: Performant form handling with Zod validation
- **Zustand**: Lightweight state management for UI state

### IPC Layer (Tauri Commands)
- **Database Commands**: CRUD operations for forms and metadata
- **File System Commands**: Backup, restore, export operations
- **System Integration**: Native file dialogs, OS notifications

### Backend Layer (Rust)
- **SQLite Operations**: Database management with SQLx 0.8+
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

## 🚨 CRITICAL DEVELOPMENT RULES

### Core Philosophy

**The #1 Rule**: Zero technical debt at all times. No exceptions.

### 🔒 Security & Compliance Rules

#### MANDATORY Security Rules
- ✅ **NEVER use deprecated technology** - Always use latest stable versions
- ✅ **ALWAYS use context7 MCP** to verify latest official documentation before implementation
- ✅ **NEVER use technology with security risks or warnings** - Address immediately
- ✅ **NEVER bypass blockers or create workarounds** - Fix blockers immediately
- ✅ **STOP and ask for help** if blockers cannot be resolved
- ✅ **Provide explicit instructions** for resolving any blockers encountered

#### Technology Version Requirements
- ✅ **Use latest stable major versions** - no deprecated packages allowed
- ✅ **Run `npm audit` regularly** - zero vulnerabilities policy
- ✅ **Update dependencies monthly** - keep everything current
- ✅ **Check context7 for latest docs** before using any technology

### 🛡️ Blocker Resolution Policy

#### When You Hit a Blocker:
1. **NEVER create workarounds** or mock implementations
2. **IMMEDIATELY stop development** and address the blocker
3. **Research the root cause** using context7 and official documentation
4. **Provide explicit step-by-step instructions** for resolution
5. **Ask for help if needed** - don't proceed with technical debt
6. **Test the fix thoroughly** before continuing

#### Examples of Blockers:
- Missing system dependencies
- Deprecated package versions
- Security vulnerabilities
- Build/compilation failures
- Type errors that require workarounds

### 📚 Documentation & Research Rules

#### Before Using ANY Technology:
- ✅ **Use context7 MCP** to get latest official documentation
- ✅ **Verify version compatibility** with our stack
- ✅ **Check for security advisories** or deprecation notices
- ✅ **Read migration guides** for major version updates
- ✅ **Test in isolation** before integration

#### Documentation Standards:
- ✅ **Document all architectural decisions** and rationale
- ✅ **Update docs immediately** when making changes
- ✅ **Include migration guides** for breaking changes
- ✅ **Maintain zero-debt policy** in documentation

### 🏗️ Development Standards

#### Anti-Complexity Principles
- ✅ **Simplicity First**: Choose boring, stable technology over bleeding edge
- ✅ **Build incrementally**: Complete each feature fully before starting the next
- ✅ **Test continuously**: Write tests as you develop, not after
- ✅ **Real implementation only**: No mocks, placeholders, or workarounds

#### Code Quality Gates
- ✅ **Zero TypeScript errors** - all types must be properly defined
- ✅ **Zero ESLint errors** - all linting rules must pass
- ✅ **Zero security vulnerabilities** - must pass npm audit
- ✅ **All tests passing** - comprehensive test coverage required
- ✅ **Production build working** - verify before committing

### 🚫 CRITICAL: Error Prevention Protocol

#### The Meta-Problem Prevention Strategy
**Core Issue**: Treating development as code generation rather than software engineering.
**Solution**: Mandatory engineering discipline with verification gates.

#### 1. Mandatory Compilation Gates
- ✅ **NEVER write more than 20-30 lines without compiling**
- ✅ **Treat ANY compilation error as a blocking issue**
- ✅ **No new features until ALL errors are resolved**
- ✅ **No warnings allowed in production code**
- ✅ **One error fix at a time - understand each fix before continuing**

#### 2. Technology Verification Protocol
- ✅ **Before using ANY external crate pattern, create a minimal test**
- ✅ **Always check documentation for the EXACT version being used**
- ✅ **Verify breaking changes in major version updates with context7**
- ✅ **Test basic patterns in isolation before building complex systems**
- ✅ **Never assume API compatibility across major versions**

#### 3. Incremental Development Discipline
- ✅ **Start with the simplest possible working implementation**
- ✅ **Add complexity only when requirements explicitly demand it**
- ✅ **Each addition must compile and pass basic tests**
- ✅ **Refactor working code, never fix broken code by adding complexity**
- ✅ **Delete code that doesn't compile rather than trying to fix it**

#### 4. Error-Driven Learning Protocol
- ✅ **When encountering errors, understand the root cause before fixing**
- ✅ **Read error messages completely - don't skim**
- ✅ **Fix one error at a time, compile after each fix**
- ✅ **Document what was learned from each error**
- ✅ **Build understanding rather than just fixing symptoms**

#### 5. Premature Optimization Prevention
- ✅ **Implement features only when explicitly requested**
- ✅ **Build abstractions only when patterns emerge (3+ repetitions)**
- ✅ **Prioritize working code over impressive-looking code**
- ✅ **Question every layer of abstraction - can this be simpler?**
- ✅ **Optimize for readability and correctness, not cleverness**

#### 6. Foundation-First Development
- ✅ **Verify basic operations work before building complex systems**
- ✅ **Use official examples from documentation as starting points**
- ✅ **Build confidence in the foundation before adding features**
- ✅ **Create minimal working examples for any uncertain patterns**
- ✅ **Test technology integrations in isolation first**

### 🔄 Dependency Management

#### Dependency Health Policy
- ✅ **Monthly dependency audits** - keep everything current
- ✅ **Remove unused dependencies** immediately
- ✅ **Document dependency choices** and rationale
- ✅ **Test updates in isolation** before applying
- ✅ **Use exact versions** in package-lock.json

#### Acceptable Dependency Criteria
- ✅ **Well-maintained** (updated within 6 months)
- ✅ **No security vulnerabilities** (check npm audit)
- ✅ **Compatible with our stack** (test thoroughly)
- ✅ **Has good documentation** and community support
- ✅ **Stable API** (no frequent breaking changes)

## 🎨 UI/UX Standards

### Enterprise UI/UX System
The application uses a comprehensive Enterprise UI/UX System defined in `docs/ui-ux-spec-complete.md`. This replaces the deprecated `docs/ui.md`.

#### Design System Requirements
- ✅ **Base Framework**: shadcn/ui components with Tailwind CSS
- ✅ **Typography**: System font stack with consistent type scale (8px base unit)
- ✅ **Colors**: Enterprise color palette with WCAG AA compliance
- ✅ **Accessibility**: WCAG 2.1 AA compliance mandatory
- ✅ **Performance**: Strict component performance budgets

#### Component Performance Budgets
| Component | Max Initial Render | Max Interaction Time |
|-----------|-------------------|---------------------|
| Button | < 16ms | < 50ms |
| Form Input | < 16ms | < 50ms |
| Modal | < 100ms | < 50ms |
| Data Table | < 200ms | < 100ms |

#### Mobile-First Requirements
- ✅ **Touch targets ≥ 44px** for accessibility
- ✅ **Form inputs ≥ 48px height** on mobile devices
- ✅ **Font size ≥ 16px** to prevent zoom on iOS
- ✅ **Responsive breakpoint strategy** with mobile-first approach

### Component Development Standards
- ✅ **Use shadcn/ui base components** before creating custom ones
- ✅ **Follow accessibility-first** design principles
- ✅ **Implement proper keyboard navigation** and focus management
- ✅ **Include loading states, error states, and empty states**
- ✅ **Support dark mode** through CSS custom properties
- ✅ **Test with real data** - comprehensive validation

## 🧪 Testing Standards

### Testing Requirements
- ✅ **Unit tests for all utilities** and core logic
- ✅ **Component tests for UI behavior** 
- ✅ **Integration tests with real backend** - no mocks allowed
- ✅ **E2E tests for critical workflows**
- ✅ **Accessibility tests** - automated and manual
- ✅ **Performance tests** - measure and optimize

### Test Quality Standards
- ✅ **Tests must use real backend** - no mock services
- ✅ **Fast execution** - total test suite < 30 seconds
- ✅ **Reliable tests** - no flaky or intermittent failures
- ✅ **Clear test names** - describe what is being tested
- ✅ **Test edge cases** - not just happy paths

## 🚀 Build & Deployment

### Production Readiness
- ✅ **Single executable deployment** - optimized for size and performance
- ✅ **Cross-platform builds** - Windows, macOS, Linux
- ✅ **Portable operation** - runs from any location
- ✅ **No external dependencies** - everything bundled
- ✅ **Automated build process** - repeatable and reliable

### Performance Standards
- ✅ **App startup < 3 seconds** on minimum hardware
- ✅ **Form operations < 1 second** for typical use
- ✅ **Memory usage < 512MB** for normal operation
- ✅ **Bundle size optimized** - remove unused code
- ✅ **Database operations optimized** - proper indexing

## 📊 Project Status Tracking

### Current State Assessment
- ✅ **Rust Backend**: Production-ready with SQLx 0.8, all commands implemented
- ✅ **Frontend**: Modern React 18+ with TypeScript 5.8+
- ✅ **Security**: All vulnerabilities resolved, latest packages
- ✅ **Build System**: Tauri 2.x with optimized single executable output
- ✅ **Technical Debt**: Zero - all mock backends removed, real implementation only

### Quality Metrics
- ✅ **Zero npm audit vulnerabilities**
- ✅ **Zero TypeScript errors**
- ✅ **Zero ESLint errors**
- ✅ **All tests passing**
- ✅ **Production build working**

## 🛠️ Development Commands

### Setup
```bash
# Verify environment (run first!)
rustc --version        # Should be 1.87+
npm --version          # Should be latest LTS
node --version         # Should be latest LTS

# Install dependencies
npm install

# Verify no vulnerabilities
npm audit              # Should show 0 vulnerabilities

# Test Rust compilation
cd src-tauri && cargo check

# Test frontend compilation
npm run type-check

# Test linting
npm run lint
```

### Development
```bash
# Start development server (with real backend)
npm run tauri dev

# Run tests
npm run test
npm run test:e2e

# Check for issues
npm run lint
npm run type-check
cargo check
```

### Production
```bash
# Build for production
npm run tauri build

# Verify single executable
ls -la src-tauri/target/release/
```

## 🔍 Pre-Commit Checklist

Before committing ANY code:
- [ ] ✅ **Zero TypeScript errors** (`npm run type-check`)
- [ ] ✅ **Zero ESLint errors** (`npm run lint`)
- [ ] ✅ **Zero security vulnerabilities** (`npm audit`)
- [ ] ✅ **All tests passing** (`npm run test`)
- [ ] ✅ **Rust code compiles** (`cargo check`)
- [ ] ✅ **Production build works** (`npm run tauri build`)
- [ ] ✅ **No temporary files** committed
- [ ] ✅ **Documentation updated** if needed

## 🚨 Red Flags - Stop Immediately If:

### Code Quality Red Flags
- **Any security vulnerability appears** in npm audit
- **Any deprecated package warnings** appear
- **TypeScript errors that require `@ts-ignore`** 
- **ESLint errors that require disabling rules**
- **Build failures that require workarounds**
- **Mock implementations being created** instead of fixing blockers
- **Temporary files or fixtures** being committed
- **Documentation becoming outdated**

### Meta-Problem Red Flags (System Failure Indicators)
- **Writing code without compiling for more than 30 lines**
- **Adding features while compilation errors exist**
- **Implementing complex patterns without testing basic versions first**
- **Copy-pasting code without understanding what it does**
- **Trying to fix multiple errors simultaneously**
- **Adding abstractions to solve problems that don't exist yet**
- **Treating warnings as "nice to fix later" rather than immediate issues**
- **Building enterprise features before basic CRUD operations work**
- **Using advanced language features without verifying they work in our context**
- **Prioritizing impressive code over working code**

### Emergency Stop Conditions
If ANY of these occur, immediately stop development and fix:
1. **Compilation errors while writing new features**
2. **More than 3 warnings in the codebase**
3. **Any pattern copied from documentation without verification**
4. **Adding complexity to fix existing complexity**
5. **Uncertainty about why a fix worked**

## 💡 Success Indicators

Your development is on track when:
- ✅ **All builds pass** without warnings or errors
- ✅ **Dependencies are current** and secure
- ✅ **Tests are comprehensive** and use real backend
- ✅ **Documentation is complete** and up-to-date
- ✅ **Performance targets are met** on minimum hardware
- ✅ **Accessibility standards** are followed
- ✅ **Code follows design system** standards

## 📚 Key Documentation References

- **UI/UX Standards**: `docs/ui-ux-spec-complete.md` (**PRIMARY** - Enterprise UI/UX System)
- **Product Requirements**: `docs/prd.md`
- **Technical Design**: `docs/tdd.md`
- **ICS Forms Analysis**: `docs/ICS-Forms-Analysis-Summary.md`
- **Development Plan**: `PLAN.md`

### ⚠️ Deprecated Documentation
- **`docs/ui.md`**: DEPRECATED - replaced by ui-ux-spec-complete.md. Do not use for new development.

## 🎯 Remember

> **Zero technical debt policy means:**
> - No mock implementations
> - No deprecated packages
> - No security vulnerabilities  
> - No workarounds for blockers
> - No temporary fixes
> - No outdated documentation

## 🛡️ Meta-Problem Mitigation Strategy

### The Core Issue
**Problem**: Treating development as code generation rather than software engineering.
**Root Cause**: Prioritizing feature velocity over correctness, leading to cascade failures.

### Mitigation Approach

#### 1. Mindset Shift Protocol
- **Before writing ANY code**: Ask "What is the simplest thing that could possibly work?"
- **Before adding complexity**: Ask "Is this solving a real problem or an imagined one?"
- **Before copying patterns**: Ask "Do I understand what this code actually does?"
- **Before continuing with errors**: Ask "What is the compiler trying to tell me?"

#### 2. Verification Checkpoints
Every 10-15 minutes during development:
- [ ] "Does my code compile?"
- [ ] "Do I understand every line I just wrote?"
- [ ] "Am I solving the right problem?"
- [ ] "Is this the simplest approach?"

#### 3. Complexity Debt Prevention
- **Mandatory Justification**: Every abstraction must solve a proven, recurring problem
- **Delete Over Fix**: If code doesn't work, delete it rather than patch it
- **Understand Over Copy**: Never use code you don't fully understand
- **Build Over Engineer**: Build solutions, don't engineer impressive systems

#### 4. Feedback Loop Optimization
- **Compilation as Truth**: The compiler is always right, developer assumptions are always suspect
- **Error Messages as Teachers**: Read them completely, learn from them
- **Simplicity as Strategy**: Boring, working code beats clever, broken code every time

### Emergency Recovery Protocol
When the meta-problem manifests (cascade errors, growing complexity, decreasing understanding):

1. **STOP** adding features immediately
2. **DELETE** all non-compiling code
3. **START** with the simplest possible working version
4. **BUILD** incrementally with continuous verification
5. **LEARN** from what went wrong before proceeding

**When in doubt, stop and ask for help. It's better to get it right than to accumulate technical debt.**