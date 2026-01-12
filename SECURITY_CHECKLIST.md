# Security Pre-Push Checklist

**⚠️ IMPORTANT: Complete this checklist before pushing to GitHub**

## 🔍 Automated Checks

Run these commands in your terminal before committing:

### 1. Search for Common Sensitive Patterns

```bash
# Search for potential API keys, tokens, and secrets
cd /Users/wuxian/Code/me/claude-toolkit

# Check for API keys
grep -r "api_key" --exclude-dir=node_modules --exclude-dir=.git --exclude="*.md" .

# Check for tokens
grep -r "token" --exclude-dir=node_modules --exclude-dir=.git --exclude="*.md" .

# Check for passwords
grep -r "password" --exclude-dir=node_modules --exclude-dir=.git --exclude="*.md" .

# Check for secrets
grep -r "secret" --exclude-dir=node_modules --exclude-dir=.git --exclude="*.md" .

# Check for credentials
grep -r "credential" --exclude-dir=node_modules --exclude-dir=.git --exclude="*.md" .

# Check for private keys
grep -r "BEGIN.*PRIVATE KEY" --exclude-dir=node_modules --exclude-dir=.git .
```

### 2. Check for Hardcoded Values

```bash
# Look for suspicious hardcoded values (adjust patterns as needed)
grep -rE "[0-9a-zA-Z]{32,}" --exclude-dir=node_modules --exclude-dir=.git --exclude="*.md" . | grep -v "sha\|hash\|example"
```

### 3. Review Staged Files

```bash
# List all files to be committed
git diff --cached --name-only

# Review each file's content
git diff --cached
```

## ✅ Manual Verification Checklist

- [ ] **Environment Files**
  - [ ] No `.env` files committed (should be in .gitignore)
  - [ ] `.env.example` exists with dummy values only
  - [ ] All sensitive configs use environment variables

- [ ] **Configuration Files**
  - [ ] No API keys in config files
  - [ ] No database credentials
  - [ ] No hardcoded URLs with credentials

- [ ] **Code Files**
  - [ ] No commented-out credentials
  - [ ] No debug code with sensitive data
  - [ ] No TODO comments with sensitive info

- [ ] **Documentation**
  - [ ] Example commands use placeholder values
  - [ ] No actual usernames/passwords in examples
  - [ ] Screenshots don't contain sensitive data

- [ ] **Skills & Commands**
  - [ ] Example code uses placeholder tokens
  - [ ] No actual API endpoints with auth
  - [ ] Instructions mention using environment variables

- [ ] **Git History**
  - [ ] Previous commits don't contain sensitive data
  - [ ] If sensitive data found, use `git filter-branch` or BFG Repo-Cleaner

## 🚨 What to Do If You Find Sensitive Data

### Option 1: Before First Push (Easiest)
```bash
# Remove the file
git rm --cached path/to/sensitive/file

# Or edit the file to remove sensitive data
git add path/to/file
git commit --amend
```

### Option 2: After Pushing (More Complex)
```bash
# Rotate/invalidate all exposed credentials immediately!
# Then clean Git history (this rewrites history):

# Install BFG Repo-Cleaner
brew install bfg  # macOS
# or download from https://rtyley.github.io/bfg-repo-cleaner/

# Remove sensitive data
bfg --delete-files sensitive-file.txt
bfg --replace-text passwords.txt  # file containing patterns to replace

# Clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push (⚠️ WARNING: This rewrites history!)
git push --force
```

## 📋 Pre-Commit Hook (Optional but Recommended)

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash

echo "Running security checks..."

# Check for common sensitive patterns
if git diff --cached | grep -iE "(api_key|password|secret|token|private.*key)" --exclude="*.md"; then
    echo "❌ ERROR: Potential sensitive data detected!"
    echo "Please review your changes and remove any sensitive information."
    exit 1
fi

# Check for large files (potential binary secrets)
if git diff --cached --name-only | xargs ls -l 2>/dev/null | awk '{if ($5 > 1048576) print $9}'; then
    echo "⚠️  WARNING: Large files detected. Make sure they don't contain sensitive data."
fi

echo "✅ Security checks passed!"
exit 0
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

## 🔐 Best Practices

1. **Use Environment Variables**: Never hardcode credentials
2. **Use `.env.example`**: Provide templates with dummy values
3. **Regular Audits**: Periodically review your repository
4. **Credential Rotation**: If anything is exposed, rotate immediately
5. **Secret Scanning Tools**: Consider tools like:
   - GitHub Secret Scanning (automatic)
   - GitGuardian
   - TruffleHog
   - git-secrets

## 📞 Emergency Contact

If you accidentally push sensitive data:

1. **Immediately** rotate/invalidate the exposed credentials
2. Clean your Git history (see above)
3. Force push the cleaned history
4. Monitor for unauthorized access
5. Consider reporting the incident if required

---

**Remember: Prevention is better than cure. Always review before pushing!**
