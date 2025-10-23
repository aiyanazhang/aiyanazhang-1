# Development Tools Repository

**English** | [日本語](./README.ja.md)

This repository is a comprehensive collection of 8 independent development tool projects designed to address various development needs, including file management, environment diagnostics, and learning resources.

---

## 📑 Table of Contents

- [Projects Overview](#projects-overview)
- [Quick Start Guide](#quick-start-guide)
- [Technology Stack](#technology-stack)
- [Contributing](#contributing)
- [Support](#support)
- [License](#license)

---

## Projects Overview

| Project | Technology | Category | Description | Status |
|---------|-----------|----------|-------------|--------|
| [file-cleaner](./file-cleaner/) | 🐍 Python | File Management | Safe and traceable file deletion tool | ✅ Available |
| [trash-cleaner](./trash-cleaner/) | 🐚 Shell Script | File Management | Cross-platform trash cleaner | ✅ Available |
| [text-search-tool](./text-search-tool/) | 🐚 Shell Script | File Management | High-performance text search tool | ✅ Available |
| [java-environment-checker](./java-environment-checker/) | ☕ Java | Environment Check | Java environment diagnostic tool | ✅ Available |
| [java-config-management](./java-config-management/) | ☕ Java + Spring Boot | Backend Framework | Enterprise-grade configuration management | ✅ Available |
| [linux-file-commands](./linux-file-commands/) | 🐍 Python | Learning Resource | Linux command learning tool | ✅ Available |
| [python-threading-demo](./python-threading-demo/) | 🐍 Python | Learning Resource | Python multithreading practical demo | ✅ Available |
| [python-tuple-demo](./python-tuple-demo/) | 🐍 Python | Learning Resource | Python tuple complete learning system | ✅ Available |

### Categorized by Purpose

```
📦 Development Tools
├── 🗂️ File Management Tools
│   ├── file-cleaner - Safe file deletion
│   ├── trash-cleaner - Trash cleaner
│   └── text-search-tool - Text search
├── 🔧 Environment Check Tools
│   ├── java-environment-checker - Java environment diagnostics
│   └── java-config-management - Configuration management system
└── 📚 Learning Resources
    ├── linux-file-commands - Linux command learning
    ├── python-threading-demo - Multithreading learning
    └── python-tuple-demo - Tuple learning
```

---

## Quick Start Guide

### Prerequisites

Different projects require different environments:

| Technology | Version | Purpose | Installation |
|-----------|---------|---------|-------------|
| Python | 3.6+ | For Python projects | `sudo apt install python3` |
| Java | 8+ | For Java projects | `sudo apt install openjdk-17-jdk` |
| Bash | 4.0+ | For Shell scripts | Pre-installed |
| Maven | 3.6+ | For Java builds | `sudo apt install maven` |

### General Setup

```bash
# 1. Clone the repository
git clone <repository-url>
cd <repository-name>

# 2. Navigate to desired project
cd <project-name>

# 3. Check project-specific README
cat README.md

# 4. Run the project (varies by project)
# For Python projects:
python3 main.py

# For Java projects:
mvn spring-boot:run

# For Shell scripts:
chmod +x script-name.sh
./script-name.sh
```

---

## Technology Stack

### Languages and Frameworks

| Technology | Projects Count | Projects |
|-----------|----------------|----------|
| 🐍 **Python 3.6+** | 4 | file-cleaner, linux-file-commands, python-threading-demo, python-tuple-demo |
| ☕ **Java 8+** | 2 | java-environment-checker, java-config-management |
| 🐚 **Shell Script (Bash)** | 2 | text-search-tool, trash-cleaner |
| 🍃 **Spring Boot** | 1 | java-config-management |

---

## Contributing

Contributions are welcome!

### How to Contribute

1. Fork the project
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- **Python projects**: Follow PEP 8 coding standards
- **Java projects**: Follow Java coding conventions
- **Comments**: Add appropriate comments
- **Tests**: Write unit tests for new features
- **Documentation**: Update README for changes

---

## Support

### Getting Help

1. **Check project-specific README** - Refer to README.md in each project directory
2. **Search Issues** - Check existing issues for similar problems
3. **Create new Issue** - Describe your problem in detail
4. **Join Discussions** - Participate in general questions and discussions

---

## License

Unless otherwise specified, all projects in this repository are released under the **MIT License**.

See individual project LICENSE files for details.

---

<div align="center">

**🎉 Welcome to the Development Tools Repository!**

We hope these tools help streamline your development work and support your learning.

⭐ If you like it, please give us a star!

</div>
