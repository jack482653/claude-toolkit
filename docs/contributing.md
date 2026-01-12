# Contributing

## How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-skill`)
3. Make your changes
4. Test thoroughly
5. Submit a Pull Request

## Adding a New Skill

1. Create `skills/your-skill-name/`
2. Add `SKILL.md` with frontmatter:
   ```markdown
   ---
   name: your-skill-name
   description: What it does and when to use it
   ---
   ```
3. Add `README.md` with usage examples
4. Test in Claude.ai

## Adding a New Command

1. Create `commands/your-command.md`
2. Define the task and guidelines
3. Test in Claude Code

## Pull Request Guidelines

- Clear title: `[Skill] Add Docker skill` or `[Command] Add review command`
- Brief description of changes
- Confirm you've tested the changes

## Security

Never commit:
- API keys or tokens
- Passwords or credentials
- Personal information

## License

By contributing, you agree your contributions will be licensed under MIT.
