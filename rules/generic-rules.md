# AI Coding Rules: Simplicity, Maintainability, and Anti-Complexity Guide

## Core Philosophy

**The #1 Rule**: If it's not working simply, it won't work complexly.

### Fundamental Principles

1. **Simplicity First**
   - Start with the simplest solution that works
   - Use native/built-in solutions before adding external dependencies
   - Write readable code over clever code
   - Prefer explicit over implicit behavior

2. **Incremental Development**
   - Build one feature completely before starting the next
   - Each feature must have working tests before moving on
   - Deploy to staging after each feature completion
   - Get user feedback before adding complexity

3. **Pragmatic Engineering**
   - Choose boring, stable technology over bleeding edge
   - Build for today's requirements, not tomorrow's possibilities
   - Working code is better than perfect code
   - User feedback trumps developer assumptions

## 🚨 Critical Anti-Patterns to Avoid

### 1. Premature Optimization
- ❌ DON'T implement advanced features (real-time, offline, caching) before basic CRUD works
- ❌ DON'T optimize performance before establishing functionality
- ✅ DO build incrementally: Basic functionality → Tests → Enhancements → Advanced features
- ✅ DO measure before optimizing

### 2. Over-Engineering
- ❌ DON'T create complex abstractions for simple problems
- ❌ DON'T add dependencies unless absolutely necessary
- ❌ DON'T implement features "just in case" or "for the future"
- ✅ DO use the simplest solution that works
- ✅ DO refactor only when complexity is proven necessary

### 3. Test Complexity
- ❌ DON'T create elaborate mocking systems
- ❌ DON'T write integration tests before unit tests work
- ❌ DON'T spend more time writing test infrastructure than tests
- ✅ DO write simple, fast tests that actually run (< 30 seconds total)
- ✅ DO mock only external dependencies (database, API calls)

### 4. Dependency Chaos
- ❌ DON'T use alpha/beta/RC versions in production code
- ❌ DON'T adopt new major versions immediately (wait 3-6 months)
- ❌ DON'T add a dependency when native solutions exist
- ✅ DO use stable, well-tested versions
- ✅ DO audit and remove unused dependencies regularly

## 📋 Development Workflow

### Before Starting ANY Feature

**Ask yourself:**
1. [ ] Is the current code stable and tested?
2. [ ] Can this be done with existing dependencies?
3. [ ] Is this feature actually required now?
4. [ ] Have I written tests for existing features?
5. [ ] Can I explain this simply to a non-technical person?

### Implementation Order (ALWAYS Follow This)

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

## 🛠️ Technical Guidelines

### Code Quality Standards

1. **Documentation**
   - Every project needs a comprehensive README.md
   - Document purpose, usage, parameters, and return values
   - Write clear comments for complex logic
   - Keep documentation close to code

2. **Code Organization**
   - Follow established style guides for your language
   - Use consistent naming conventions
   - Keep files between 300-500 lines where possible
   - One responsibility per module/class/function

3. **Error Handling**
   - Implement proper error handling from the start
   - Use appropriate logging levels
   - Fail fast with clear error messages
   - Never silently swallow errors

4. **Testing Strategy**
   - Write tests that actually run and pass
   - Focus on testing behavior, not implementation
   - Keep test setup minimal
   - If test setup is complex, the code is too complex

### Dependency Management Rules

1. **Before Adding ANY Dependency:**
   - Is there a native/built-in solution?
   - Is it well-maintained (check last update, issues, downloads)?
   - Is it compatible with current versions?
   - Have you tested it in isolation first?
   - Can you implement the needed functionality yourself in < 100 lines?

2. **Dependency Health Checks:**
   - Monthly audit of all dependencies
   - Remove unused dependencies immediately
   - Document why each dependency is needed
   - Prefer fewer, well-established packages

### Feature Complexity Guidelines

**Complexity Levels:**
- **Basic (Do First)**: CRUD, forms, lists, authentication, basic UI
- **Intermediate (After Basic Works)**: Search, filters, validation, permissions, API integrations
- **Advanced (After User Feedback)**: Real-time updates, offline mode, AI features, complex visualizations

**Never implement Advanced features until:**
1. All Basic features are complete and tested
2. Intermediate features are stable
3. Users have specifically requested them
4. You have a rollback plan

## 🚩 Red Flags & Warning Signs

### You're Over-Engineering If:
- You're writing more infrastructure than features
- Tests take longer to write than the code
- You need a diagram to explain the data flow
- You're adding "just in case" functionality
- The PR/commit has more than 500 lines changed
- You can't demo the feature in 2 minutes
- New developers need more than 30 minutes to understand

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
   - Check logs at appropriate levels
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

### Project Health Indicators:
- ✅ Clear, updated documentation
- ✅ All tests passing
- ✅ No compiler/interpreter warnings
- ✅ Dependencies are current and minimal
- ✅ Code follows consistent patterns
- ✅ Features match user needs (not developer wants)

## 🎯 Decision Framework

### When Making Technical Decisions:

1. **Choose Boring Technology**
   - Proven solutions over new experiments
   - Well-documented over cutting-edge
   - Community support over unique features

2. **Minimize Technical Debt**
   - Fix issues immediately, not "later"
   - Refactor when patterns emerge, not preemptively
   - Keep dependencies updated monthly

3. **Maximize Maintainability**
   - Code for the next developer (it might be you)
   - Prefer clarity over performance (until measured)
   - Document why, not just what

## 💡 Best Practices Summary

### Always:
- ✅ Build features incrementally
- ✅ Test as you go
- ✅ Get user feedback early
- ✅ Keep it simple
- ✅ Document decisions
- ✅ Remove unused code/dependencies

### Never:
- ❌ Add features users haven't asked for
- ❌ Use unstable dependencies
- ❌ Write placeholder/stubbed code
- ❌ Duplicate code instead of refactoring
- ❌ Sacrifice clarity for cleverness
- ❌ Skip testing to "save time"

## 🏁 Final Checklist

Before considering any feature "done":
- [ ] Does it solve the user's actual problem?
- [ ] Can you demo it in 2 minutes?
- [ ] Are all tests passing?
- [ ] Is the code self-documenting?
- [ ] Have you removed all unused code?
- [ ] Would a new developer understand it?
- [ ] Is it the simplest solution that works?

## Remember

> "Perfection is achieved not when there is nothing more to add, but when there is nothing left to take away." - Antoine de Saint-Exupéry

**Focus on:**
- User value over technical elegance
- Simplicity over sophistication
- Today's problems over tomorrow's possibilities
- Maintenance over features
- Clarity over cleverness

**The goal is not to build the most technically impressive solution, but to solve real problems with the least complexity possible.**