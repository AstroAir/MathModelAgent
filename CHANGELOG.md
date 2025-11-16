# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Language Auto-Detection**: Automatically detects Chinese or English input text
  - Smart heuristic-based detection with >90% accuracy
  - Confidence score reporting for user transparency
  - Default "自动检测" option in frontend UI
  - Manual language override still available
  - Comprehensive test coverage with 15+ test cases
- One-click startup scripts for Windows (.bat, .ps1), Linux, and macOS (.sh)
- Comprehensive GitHub project structure
  - Issue templates (bug report, feature request, question)
  - Pull request template with detailed checklist
  - GitHub Actions workflows (CI, CodeQL, dependency review, release)
- Complete project documentation
  - LICENSE file with commercial use restrictions
  - CONTRIBUTING.md with contribution guidelines
  - ARCHITECTURE.md with detailed system architecture
  - CODE_OF_CONDUCT.md for community standards
  - SECURITY.md with security policies
  - QUICK_START.md for rapid onboarding
- Development tool configurations
  - .editorconfig for consistent coding styles
  - .prettierrc.json for JavaScript/TypeScript formatting
  - .markdownlintrc.json for Markdown linting
- Enhanced .gitignore with comprehensive exclusion patterns
- requirements.txt for easy Python dependency installation
- **Complete English Support (MCM/ICM)**:
  - Bilingual prompts for all agents (Coordinator, Modeler, Coder, Writer)
  - English markdown templates (`md_template_en.toml`)
  - Language-aware system messages throughout workflow
  - Dynamic template selection based on language
  - Frontend language selection UI (Chinese, English, Auto-detect)

### Changed

- Enhanced .gitignore to cover more patterns (Python, Node.js, IDEs, OS files)
- Improved project structure for production readiness

### Fixed

- Clarified installation methods with multiple options
- Added dependency checking in startup scripts

## [0.1.0] - Previous Release

### Added

- Initial release with basic functionality
- Multi-agent system for mathematical modeling
- Web UI with Vue.js
- FastAPI backend
- Code interpreter (local and cloud)
- Paper generation capabilities
- Docker deployment support

[Unreleased]: https://github.com/jihe520/MathModelAgent/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/jihe520/MathModelAgent/releases/tag/v0.1.0
