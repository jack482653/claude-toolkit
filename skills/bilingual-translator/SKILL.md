---
name: bilingual-translator
description: Translate English articles into Traditional Chinese and create bilingual side-by-side comparison artifacts in HTML format. Use when user requests translation with dual-column layout, bilingual comparison, or wants to translate articles for reference with source URL.
---

# Bilingual Article Translator

This skill translates English articles into Traditional Chinese (繁體中文) and creates HTML artifacts with side-by-side bilingual comparison.

## When to Use This Skill

Trigger this skill when the user:
- Requests translation of English articles into Traditional Chinese
- Wants a bilingual side-by-side comparison format
- Asks to translate with source URL reference
- Mentions "雙語對照", "翻譯對照", or "bilingual translation"

## Input Requirements

The skill requires:
1. **Article content** - The English text to translate
2. **Source URL** (optional) - Reference link to the original article

## Output Format

Create an HTML artifact with:
- Dual-column layout (English left, Chinese right)
- Source URL reference at the top (if provided)
- Responsive design that switches to single-column on mobile
- Professional styling with proper typography and spacing

## Translation Guidelines

1. **Accuracy**: Translate content accurately while maintaining technical terms where appropriate
2. **Readability**: Use natural Traditional Chinese expressions
3. **Technical terms**: Keep technical terms in English if commonly used (e.g., TTL, ISO, RAW)
4. **Formatting**: Preserve all headings, paragraphs, and structure
5. **Context**: Consider the full context when translating idioms or specialized terminology

## HTML Template Structure

Use the template structure defined in `references/html_template.md`. The template includes:
- Responsive CSS grid layout
- Professional color scheme and typography
- Source reference section
- Mobile-responsive breakpoints

## Workflow

1. Parse the article content and source URL (if provided)
2. Translate each section from English to Traditional Chinese
3. Generate HTML using the template from references
4. Create the artifact in `/mnt/user-data/outputs/`
5. Provide the download link to the user

When translating, maintain paragraph-by-paragraph correspondence to ensure easy side-by-side comparison.
