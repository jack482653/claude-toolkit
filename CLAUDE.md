# Claude Toolkit - AI Agent Guide

## Project Overview

This project contains:
- **Skills** - Custom knowledge packs for Claude.ai
- **Commands** - Custom commands for Claude Code CLI

## Project Structure

```
claude-toolkit/
├── skills/           # Claude.ai skills
│   └── <name>/
│       ├── SKILL.md      # Main skill definition (required)
│       ├── README.md     # Documentation (required)
│       └── references/   # Additional resources (optional)
├── commands/         # Claude Code commands
│   └── <name>.md
└── docs/             # Documentation
```

## Development Tasks

### Adding a New Skill

**Method 1: Use skill-creator (Recommended)**

Use Claude's built-in `skill-creator` skill to generate the skill structure and content.

**Method 2: Manual Creation**

1. Create directory: `skills/<skill-name>/`
2. Create `SKILL.md` with frontmatter:
   ```markdown
   ---
   name: skill-name
   description: Brief description and trigger phrases
   ---
   ```
3. Create `README.md` with usage examples

**After creating:**
- Update `skills/README.md` table
- Update root `README.md` skills table

### Adding a New Command

1. Create `commands/<command-name>.md`
2. Define task guidelines and format
3. Update `commands/README.md` table
4. Update root `README.md` commands table

## Reference Documents

- `GIT_SETUP.md` - Guide for Git initialization and pushing to GitHub
- `SECURITY_CHECKLIST.md` - Security verification before pushing code
- `docs/contributing.md` - Contribution workflow

## Conventions

- Keep documentation concise
- Use tables for listing items
- Skill names: lowercase with hyphens (e.g., `bilingual-translator`)
- Command names: short, lowercase (e.g., `gc`)
