---
title: Add TypeScript Equivalent of py_config_stack
labels: feature-request, typescript
---

# Add TypeScript Equivalent of py_config_stack

## Feature Request

### Overview
Create a TypeScript version of the Python config stack that loads configuration from const.toml and test_data.yml files, supporting layered configuration merging.

### Background
The existing Python implementation in src/py_config_stack provides a robust configuration loading system with layered overrides. To enable similar functionality in TypeScript projects, we need an equivalent implementation.

### User Story
- **As a** TypeScript developer
- **I want to** use a config loader equivalent to the Python version
- **So that** I can load and merge configurations from multiple sources including const.toml and test_data.yml

### Requirements
- TypeScript implementation of loadConfig function
- Support for loading const data from const.toml
- Support for loading test data from test_data.yml
- Layered configuration merging (env overrides cli overrides config)
- CLI argument parsing for config overrides
- Environment variable parsing with skip rules

### Acceptance Criteria
- [ ] loadConfig function implemented in TypeScript
- [ ] Loads const data from const.toml file
- [ ] Loads test data from test_data.yml file
- [ ] Merges configurations in correct order: env > cli > config file > defaults
- [ ] Parses CLI arguments with dot notation support
- [ ] Parses environment variables with double underscore conversion
- [ ] Skips specified environment variables and prefixes as defined in const.toml
- [ ] Type-safe implementation with proper error handling

### Technical Notes
- Place implementation in src/ts_config_stack.ts
- Use standard TypeScript libraries for TOML/YAML parsing
- Follow similar structure to py_config_stack.py
- Export constData and testData as loaded from files

### Proposed Implementation
1. Create src/ts_config_stack.ts file
2. Implement loadConfig function with type parameters
3. Add file loading for const.toml and test_data.yml
4. Implement CLI and env parsing logic
5. Add deep merge functionality
6. Export loaded data constants

### Alternatives Considered
- **Option A**: Use existing config libraries - Pros: faster implementation, Cons: may not match exact functionality
- **Option B**: Manual implementation - Pros: exact match to Python version, Cons: more development time
- **Option C**: ✓ Selected for consistency with existing Python implementation

### Estimated Effort
**2-3 days** (1 day implementation, 1 day testing, 1 day refinement)