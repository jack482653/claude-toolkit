# Git Setup & Push Guide

This guide walks you through initializing Git, performing security checks, and pushing to GitHub.

## Prerequisites

- [ ] Git installed on your system
- [ ] GitHub account created (username: jack482653)
- [ ] Repository created on GitHub: `claude-toolkit`

## Step 1: Initialize Git Repository

```bash
cd /Users/wuxian/Code/me/claude-toolkit

# Initialize Git (if not already done)
git init

# Set default branch to main
git branch -M main

# Configure Git user (if not configured globally)
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

## Step 2: Security Checks (CRITICAL!)

**⚠️ Run these checks before adding files:**

### Search for Sensitive Data

```bash
# Check for API keys, tokens, passwords
grep -rn "api_key" --exclude-dir=.git --exclude-dir=node_modules --exclude="*.md" .
grep -rn "token" --exclude-dir=.git --exclude-dir=node_modules --exclude="*.md" .
grep -rn "password" --exclude-dir=.git --exclude-dir=node_modules --exclude="*.md" .
grep -rn "secret" --exclude-dir=.git --exclude-dir=node_modules --exclude="*.md" .

# Check for private keys
grep -rn "BEGIN.*PRIVATE KEY" --exclude-dir=.git .

# Check for hardcoded credentials
grep -rn "credential" --exclude-dir=.git --exclude-dir=node_modules --exclude="*.md" .
```

### Review Output

If any sensitive data is found:
1. ❌ **STOP** - Do not proceed
2. Remove or replace sensitive data
3. Re-run security checks
4. Only continue when all checks are clean

## Step 3: Review Files to be Added

```bash
# See what will be committed
git status

# Review specific file if needed
cat path/to/file
```

### Expected Files

You should see these files:
- `.gitignore`
- `LICENSE`
- `README.md`
- `SECURITY_CHECKLIST.md`
- `skills/sdkman/SKILL.md`
- `skills/sdkman/README.md`
- `skills/README.md`
- `commands/README.md`
- `docs/*.md`

### Files that Should NOT be Committed

- `.env` files
- `*.key`, `*.pem`, `*.token`
- `node_modules/`
- Any file with credentials
- Private configuration files

## Step 4: Stage Files

```bash
# Add all files
git add -A

# Or add selectively
git add .gitignore
git add LICENSE
git add README.md
git add SECURITY_CHECKLIST.md
git add skills/
git add commands/
git add docs/

# Verify staged files
git status
```

## Step 5: Create First Commit

```bash
git commit -m "Initial commit: Claude Toolkit with SDKMAN skill

- Add comprehensive SDKMAN! skill with command reference
- Include security checklist and .gitignore
- Add documentation structure
- Setup MIT license"
```

## Step 6: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `claude-toolkit`
3. Description: "A curated collection of Claude AI skills and command references"
4. Visibility: **Public**
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

## Step 7: Add Remote and Push

```bash
# Add GitHub remote
git remote add origin https://github.com/jack482653/claude-toolkit.git

# Verify remote
git remote -v

# Push to GitHub
git push -u origin main
```

### If Push Fails

If you get authentication errors:

**Option 1: Use Personal Access Token (Recommended)**
```bash
# Create a token at: https://github.com/settings/tokens
# Select scopes: repo (all)
# Use token as password when prompted
```

**Option 2: Use SSH (More Secure)**
```bash
# Generate SSH key (if you don't have one)
ssh-keygen -t ed25519 -C "your.email@example.com"

# Add to SSH agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Copy public key
cat ~/.ssh/id_ed25519.pub

# Add to GitHub: https://github.com/settings/keys
# Then change remote to SSH
git remote set-url origin git@github.com:jack482653/claude-toolkit.git
git push -u origin main
```

## Step 8: Verify on GitHub

1. Visit https://github.com/jack482653/claude-toolkit
2. Verify all files are present
3. Check that README.md displays correctly
4. Ensure no sensitive data is visible

## Step 9: Optional - Add GitHub Topics

On your repository page:
1. Click the gear icon next to "About"
2. Add topics: `claude-ai`, `sdkman`, `claude-skills`, `development-tools`, `sdk-management`
3. Save changes

## Common Issues

### Issue: "Repository not found"
**Solution**: Make sure the repository exists on GitHub

### Issue: "Authentication failed"
**Solution**: Use a Personal Access Token or SSH key

### Issue: "Git not found"
**Solution**: Install Git from https://git-scm.com/

### Issue: "Files still showing after .gitignore"
**Solution**: 
```bash
git rm -r --cached .
git add -A
git commit -m "Apply .gitignore rules"
```

## Final Security Check

After pushing, review your repository on GitHub:

```bash
# Clone in a temporary location to verify
cd /tmp
git clone https://github.com/jack482653/claude-toolkit.git
cd claude-toolkit

# Search for any sensitive data
grep -r "password\|secret\|token\|api_key" --exclude-dir=.git .

# If anything found, immediately:
# 1. Delete the repository on GitHub
# 2. Remove sensitive data from local repo
# 3. Create new repository and push again
```

## Success Checklist

- [ ] Git repository initialized
- [ ] All security checks passed
- [ ] Files committed locally
- [ ] GitHub repository created
- [ ] Code pushed to GitHub
- [ ] Repository verified online
- [ ] No sensitive data exposed
- [ ] README.md displays correctly

## Next Steps

After successful push:

1. Add repository description and topics on GitHub
2. Enable GitHub Actions (optional)
3. Set up branch protection rules (optional)
4. Create a release with packaged `.skill` file
5. Share with the community!

---

**Remember**: Always review before pushing. Prevention is better than cure!
