# Claude Toolkit

A collection of Claude AI skills and custom commands for enhanced productivity.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## What's Included

### Skills (for Claude.ai)

Custom skills that extend Claude's capabilities:

| Skill | Description |
|-------|-------------|
| [SDKMAN](./skills/sdkman/) | SDK version management commands |
| [Bilingual Translator](./skills/bilingual-translator/) | English to Traditional Chinese translation with side-by-side HTML output |
| [Grafana](./skills/grafana/) | Dashboard management, metrics querying, and alert monitoring for Grafana v7.5 |

### Commands (for Claude Code)

Custom commands for Claude Code CLI:

| Command | Description |
|---------|-------------|
| [gc](./commands/gc.md) | Generate conventional commit messages |

## Quick Start

### Using Skills in Claude.ai

1. Download the skill ZIP from [releases](https://github.com/jack482653/claude-toolkit/releases)
2. Go to Claude.ai → Settings → Capabilities → Skills
3. Upload the ZIP file

### Using Commands in Claude Code

Place the `.md` files in your Claude Code commands directory.

## Documentation

- [Installation Guide](./docs/installation.md)
- [Usage Guide](./docs/usage.md)
- [Contributing Guidelines](./docs/contributing.md)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a Pull Request

See [Contributing Guidelines](./docs/contributing.md) for details.

## License

MIT License - see [LICENSE](LICENSE) for details.

---

*This is an independent project and is not officially affiliated with Anthropic.*
