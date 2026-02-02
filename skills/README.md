# Claude Skills

Custom skills for Claude.ai that extend Claude's capabilities in specific domains.

## Available Skills

| Skill | Description |
|-------|-------------|
| [SDKMAN](./sdkman/) | SDK version management on Unix systems |
| [Bilingual Translator](./bilingual-translator/) | English to Traditional Chinese with HTML output |
| [Grafana](./grafana/) | Dashboard management, metrics querying, and alert monitoring |

## Usage

1. Copy the content from `SKILL.md`
2. Paste into your Claude.ai project knowledge or conversation

## Skill Structure

```
skill-name/
├── SKILL.md          # Main skill definition (required)
├── README.md         # Skill documentation (required)
└── references/       # Additional resources (optional)
```

## Creating New Skills

1. Create a directory under `skills/`
2. Add `SKILL.md` with frontmatter:
   ```markdown
   ---
   name: skill-name
   description: What the skill does and when to use it
   ---
   ```
3. Add `README.md` with usage examples
4. Test in Claude.ai
5. Submit a pull request

## License

MIT License
