# TEF Skills

TEF includes Claude Code skills for enhanced capabilities.

## Installed Skills

### Chrome DevTools MCP Skill

**Source**: https://github.com/justfinethanku/cc_chrome_devtools_mcp_skill

**Capabilities**:
- Browser automation and inspection via Chrome DevTools Protocol
- Performance testing (Core Web Vitals: INP, LCP, CLS)
- Network analysis (HAR export, timing breakdowns)
- Accessibility validation (WCAG compliance)
- Device emulation (mobile, tablet, desktop)
- Visual regression testing (screenshots)
- Console monitoring

**Prerequisites**:
- chrome-devtools MCP server installed globally
- Chrome browser installed

**Usage**: Skill activates automatically when you ask Claude Code to test, analyze, or debug frontend applications.

**Examples**:
- "Test the performance of https://example.com"
- "Check accessibility issues on my login form"
- "Take screenshots at mobile and desktop sizes"

**Tools Available**: 27 professional-grade tools across 6 categories (input automation, navigation, emulation, performance, network, debugging)

## Deployment

Skills are deployed via bootstrap script:
```bash
./tef_bootstrap.sh --global  # Deploy to ~/.claude/skills/
./tef_bootstrap.sh --local   # Deploy to ./.claude/skills/
```

## Adding New Skills

1. Clone skill repo to `docs/skills/[skill-name]/`
2. Remove `.git` directory
3. Document in this README
4. Commit to TEF repo
5. Run bootstrap script to deploy
