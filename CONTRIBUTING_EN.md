# Contributing to EVCC Scheduler

Thank you for your interest in contributing to the EVCC Scheduler project!

## Code of Conduct

This project and all participants are bound by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Bug reports are very valuable! Please use GitHub Issues with this format:

```
**Description**
A short description

**Steps to Reproduce**
1. ...
2. ...

**Expected Behavior**
What should happen?

**Current Behavior**
What actually happens?

**Environment**
- Home Assistant Version: 2025.12
- EVCC Version: 0.210.2
- Python Version: 3.12
- Logs: (Please add DEBUG logs)
```

Or use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md).

### Suggesting Features

Feature requests are welcome! Create an issue with:

```
**Description**
What feature would you like?

**Motivation**
Why is this feature important?

**Proposed Implementation**
How could we implement this?

**Alternative Solutions**
Are there other approaches?
```

Or use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md).

### Pull Requests

1. **Fork** the repository
2. **Clone** your fork locally
3. **Create a branch**: `git checkout -b feature/your-feature`
4. **Commit your changes**: `git commit -am 'Add your feature'`
5. **Push** to the branch: `git push origin feature/your-feature`
6. **Open a Pull Request**

#### Pull Request Checklist

- [ ] Code follows project style (PEP 8)
- [ ] All functions have type hints
- [ ] Logging added (debug level)
- [ ] Documentation updated
- [ ] Tests added/updated (if applicable)
- [ ] No breaking changes (or clearly documented)
- [ ] Commit messages are clear and descriptive

Use the [pull request template](.github/PULL_REQUEST_TEMPLATE.md).

## Development Setup

### Environment

```bash
git clone https://github.com/yourusername/ha-evcc-scheduler.git
cd evcc_scheduler
pip install -e .
```

### Code Style

- **Python**: PEP 8
- **Line Length**: 120 characters max
- **Type Hints**: Required for all functions
- **Imports**: Standard → Third-party → Home Assistant → Local
- **Logging**: Use `_LOGGER` with appropriate levels (debug, info, warning, error)
- **Indexing**: Plan indexing is 1-based for UI/services, 0-based for internal arrays

### Linting

```bash
pip install flake8 black isort
flake8 . --max-line-length=120
black --line-length=120 .
isort .
```

### Testing

```bash
# Currently manual testing is required:
# 1. Install integration in Home Assistant
# 2. Configure with test EVCC instance
# 3. Test services via Developer Tools
# 4. Test entity creation/deletion
# 5. Test WebSocket and polling modes
# 6. Test vehicle switching
```

Enable DEBUG logging for detailed output:

```yaml
# configuration.yaml
logger:
  logs:
    evcc_scheduler: debug
    evcc_scheduler.api: debug
    evcc_scheduler.coordinator: debug
    evcc_scheduler.entity_manager: debug
```

## Documentation

- Update [DOCUMENTATION.md](DOCUMENTATION.md) for technical changes
- Update [README.md](README.md) for user-facing changes
- Keep translations in sync (English & German)
- Add examples where relevant
- Use proper Markdown formatting

### Updating Documentation Files

**English Documentation**:
- `DOCUMENTATION.md` (primary technical doc)
- `README.md` (primary quick start)
- `DOCUMENTATION_EN.md` (variant)
- `README_EN.md` (variant)

**German Documentation**:
- `DOCUMENTATION_DE.md`
- `README_DE.md`

Keep English and German documentation in sync structurally.

## Architecture Guidelines

When making changes, please understand the architecture:

```
config_flow.py ──→ __init__.py ──→ coordinator.py ──→ api.py (REST)
                      ↓
              websocket_client.py (WS reconnection)
                      ↓
              entity_manager.py ←→ switch.py (entities)
                      ↓
              services.py (CRUD operations)
```

**Key Patterns**:
- Use async/await consistently
- Coordinator is the single source of truth
- Services use pull-modify-push-refresh pattern
- Entity IDs must be stable (vehicle-agnostic)
- Always validate user input in services

## Version Management

We follow [Semantic Versioning 2.0.0](https://semver.org/):

- **MAJOR.MINOR.PATCH**
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

When preparing a release:

1. Update `manifest.json` `version` field
2. Create GitHub release with tag matching version
3. Update `CHANGELOG.md` (if used)
4. Write release notes

See [GITHUB_RELEASES.md](GITHUB_RELEASES.md) for detailed release process.

## HACS Compatibility

Ensure changes maintain HACS compatibility:

- ✅ Keep `manifest.json` valid
- ✅ Keep `hacs.json` valid
- ✅ Update documentation
- ✅ Test manifest structure

See [HACS_INTEGRATION.md](HACS_INTEGRATION.md) for details.

## Testing Before Submitting

Before submitting a PR:

1. **Local Testing**:
   ```bash
   # Copy integration to HA custom_components/
   cp -r evcc_scheduler ~/config/custom_components/
   # Restart HA and test
   ```

2. **Service Testing**:
   - Test all affected services via Developer Tools
   - Verify error handling

3. **Entity Testing**:
   - Check entities appear correctly
   - Test entity attributes
   - Test entity removal

4. **WebSocket Testing**:
   - Test with WebSocket enabled
   - Test with polling fallback
   - Monitor logs for errors

5. **Vehicle Switching**:
   - Switch between vehicles in EVCC
   - Verify entities update correctly
   - Check entity IDs remain stable

## Security

- ❌ Never commit API tokens or secrets
- ✅ Use environment variables for sensitive data
- ✅ Validate all user inputs
- ✅ Don't leak sensitive info in error messages

See [SECURITY.md](.github/SECURITY.md) for details.

## Questions or Need Help?

- 📚 Read [DOCUMENTATION.md](DOCUMENTATION.md)
- 💬 Open a [Discussion](https://github.com/diestrohs/ha-evcc-scheduler/discussions)
- 🐛 Check existing [Issues](https://github.com/diestrohs/ha-evcc-scheduler/issues)
- 📧 Email the maintainers

## License

By contributing to this project, you agree that your contributions will be licensed under its MIT License.

---

Thank you for contributing! 🎉

**Happy coding!**
