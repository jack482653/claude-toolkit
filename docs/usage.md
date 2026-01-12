# Usage Guide

## Using Skills

Once a skill is installed, simply ask questions naturally:

```
How do I install Java 17 using SDKMAN?
```

Claude will automatically reference the skill and provide accurate responses.

### Tips

- **Be specific**: "Install Java 21.0.4-tem with SDKMAN" works better than "install java"
- **Mention the tool**: "Using SDKMAN, how do I..."
- **Ask follow-ups**: Skills maintain context in conversations

## Using Commands

In Claude Code, invoke commands with the `/` prefix:

```
/gc
```

Follow the prompts to complete the command.

## Examples

### SDKMAN Skill

```
Q: How do I switch between Java versions in different projects?
A: [Claude explains .sdkmanrc files and auto-switching]
```

### gc Command

```
/gc
[Claude analyzes staged changes and generates a commit message]
```
