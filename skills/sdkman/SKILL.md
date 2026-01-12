---
name: sdkman
description: SDKMAN! command reference and usage guide for managing multiple SDK versions on Unix-based systems. Use when users ask about SDKMAN commands, how to install/manage SDKs (Java, Groovy, Scala, Kotlin, etc.), switch versions, or configure SDKMAN settings.
---

# SDKMAN! Usage Guide

## Overview

SDKMAN! is a tool for managing parallel versions of multiple Software Development Kits on Unix-based systems. It allows installation, switching, and management of SDK versions for Java, Groovy, Scala, Kotlin, and many other development tools.

## Quick Command Reference

### Essential Commands

**Install SDK**
```bash
sdk install <candidate>              # Latest stable version
sdk install <candidate> <version>    # Specific version
sdk install <candidate> <version> <path>  # Local version
```

**List & Discover**
```bash
sdk list                            # All available candidates
sdk list <candidate>               # Versions of specific candidate
```

**Switch Versions**
```bash
sdk use <candidate> <version>      # Current shell only
sdk default <candidate> <version>  # Set as default for all shells
```

**Check Status**
```bash
sdk current                        # All current versions
sdk current <candidate>           # Specific candidate version
```

**Maintenance**
```bash
sdk update                         # Refresh candidate cache
sdk upgrade <candidate>           # Check for outdated versions
sdk uninstall <candidate> <version>  # Remove version
```

## Installing SDKs

### Latest Stable Version
Install the latest stable version:
```bash
sdk install java
```
Prompts to set as default. Answer `Y` (or press Enter) to make it the default for all new shells.

### Specific Version
Install a specific version:
```bash
sdk install scala 3.4.2
sdk install java 21.0.4-tem
```

### Local Version
Register an existing local installation:
```bash
sdk install groovy 3.0.0-SNAPSHOT /path/to/groovy-3.0.0-SNAPSHOT
sdk install java 17-zulu /Library/Java/JavaVirtualMachines/zulu-17.jdk/Contents/Home
```
Note: Local version name must be unique and not in the available versions list.

## Version Management

### Use Version (Current Shell Only)
Switch version for current terminal session only:
```bash
sdk use scala 3.4.2
```
**Important**: Change is temporary and only affects current shell.

### Set Default Version
Make a version the default for all future shells:
```bash
sdk default scala 3.4.2
```
All subsequent shells will use this version.

### Check Current Versions
```bash
sdk current java          # Java version in use
sdk current              # All SDKs in use
```

Example output:
```
Using:
groovy: 4.0.22
java: 21.0.4-tem
scala: 3.4.2
```

## Environment Management (.sdkmanrc)

### Auto-Switching for Projects
Create `.sdkmanrc` in project directory:
```bash
sdk env init
```

Generated file:
```bash
# Enable auto-env through the sdkman_auto_env config
# Add key=value pairs of SDKs to use below
java=21.0.4-tem
```

### Using .sdkmanrc
Switch to project SDK versions:
```bash
sdk env
```

Reset to defaults when leaving project:
```bash
sdk env clear
```

Install missing SDKs from .sdkmanrc:
```bash
sdk env install
```

### Auto-Switching on Directory Change
Enable automatic version switching in `~/.sdkman/etc/config`:
```bash
sdkman_auto_env=true
```
SDKs will auto-switch when entering/leaving directories with `.sdkmanrc`.

## Listing & Discovery

### List All Candidates
```bash
sdk list
```
Shows all available SDKs with descriptions, URLs, and install commands.

### List Candidate Versions
```bash
sdk list groovy
```

Output shows:
- `>` = currently in use
- `*` = installed
- `+` = local version

Example:
```
> * 2.4.4                2.3.1                2.0.8
  2.4.3                2.3.0                2.0.7
```

## Upgrade & Maintenance

### Check for Outdated Versions
```bash
sdk upgrade springboot   # Single candidate
sdk upgrade             # All candidates
```

Example output:
```
Upgrade:
springboot (1.2.4.RELEASE, 1.2.3.RELEASE < 3.3.1)
```

### Update Candidate Cache
Refresh local cache of available candidates:
```bash
sdk update
```
Run when warned that SDKMAN is out-of-date.

### Self-Update SDKMAN
Update SDKMAN itself:
```bash
sdk selfupdate
sdk selfupdate force    # Force reinstall
```

### Flush Cache
Clear SDKMAN's local state (rarely needed):
```bash
sdk flush
```
**Warning**: Never manually delete `.sdkman/tmp` or other directories. Always use `sdk flush`.

## Offline Mode

Enable when working without internet:
```bash
sdk offline enable
sdk offline disable
```

In offline mode:
- Most commands work with reduced functionality
- List commands only show installed versions
- Automatically enables/disables based on connectivity

## Advanced Features

### Get SDK Home Path
Get absolute path to SDK installation (useful in scripts):
```bash
sdk home java 21.0.4-tem
# Output: /home/user/.sdkman/candidates/java/21.0.4-tem
```

### Version Information
```bash
sdk version
```
Shows SDKMAN script and native versions.

### Help
```bash
sdk help              # General help
sdk help install     # Command-specific help
```

## Configuration

Edit configuration file:
```bash
sdk config
```

Location: `~/.sdkman/etc/config`

### Key Settings

```bash
# Non-interactive mode (for CI/CD)
sdkman_auto_answer=true|false

# Auto-update checks
sdkman_selfupdate_feature=true|false

# Disable SSL verification (not recommended)
sdkman_insecure_ssl=true|false

# Curl timeout settings
sdkman_curl_connect_timeout=5
sdkman_curl_max_time=10

# Beta channel
sdkman_beta_channel=true|false

# Debug mode
sdkman_debug_mode=true|false

# Color output
sdkman_colour_enable=true|false

# Auto environment switching
sdkman_auto_env=true|false

# Auto-completion
sdkman_auto_complete=true|false
```

## Common Patterns

### CI/CD Setup
```bash
# Install specific Java version in CI
sdk install java 21.0.4-tem
sdk default java 21.0.4-tem

# Or use .sdkmanrc
sdk env install
sdk env
```

### Multi-Project Development
```bash
# Create .sdkmanrc in each project
cd project-a && sdk env init
cd project-b && sdk env init

# Enable auto-switching
# In ~/.sdkman/etc/config: sdkman_auto_env=true
```

### Testing Multiple Versions
```bash
# Install multiple versions
sdk install java 17.0.10-tem
sdk install java 21.0.4-tem

# Quick switch for testing
sdk use java 17.0.10-tem
./run-tests.sh

sdk use java 21.0.4-tem
./run-tests.sh
```

## Best Practices

1. **Use Default for Consistency**: Set preferred versions as default with `sdk default`
2. **Project .sdkmanrc Files**: Always create `.sdkmanrc` for project-specific requirements
3. **CI/CD**: Use `sdkman_auto_answer=true` in CI environments
4. **Version Naming**: Use descriptive names for local versions (e.g., `17-custom-build`)
5. **Regular Updates**: Run `sdk update` periodically to refresh candidate cache
6. **Check Before Uninstall**: Use `sdk current` to verify which version is in use

## Troubleshooting

### Version Not Switching
- Check if using `sdk use` (current shell only) vs `sdk default` (all shells)
- Verify version is installed: `sdk list <candidate>`
- Restart shell after `sdk default`

### Auto-env Not Working
- Verify `sdkman_auto_env=true` in config
- Check `.sdkmanrc` exists in directory
- Ensure `.sdkmanrc` has correct format: `candidate=version`

### Installation Fails
- Check internet connectivity
- Try offline mode: `sdk offline enable` then `sdk offline disable`
- Verify curl settings in config
- Check disk space

### Command Not Found
- Ensure SDKMAN is initialized in shell rc file (~/.bashrc, ~/.zshrc)
- Source the initialization: `source ~/.sdkman/bin/sdkman-init.sh`
