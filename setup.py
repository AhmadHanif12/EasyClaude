from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    requirements = []
    if os.path.exists(requirements_path):
        with open(requirements_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    # Handle platform markers
                    if ";" in line:
                        requirements.append(line)
                    elif not line.startswith("pytest") and not line.startswith("pyinstaller"):
                        # Skip dev tools from main install
                        requirements.append(line)
    return requirements

setup(
    name="easyclaude",
    version="0.1.0",
    description="Windows system tray launcher for Claude Code",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="EasyClaude Team",
    author_email="noreply",
    url="https://github.com/easyclaude/easyclaude",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Desktop Environment",
    ],
    keywords="claude ai assistant launcher tray hotkey",
    python_requires=">=3.10",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "app": ["../assets/*"],
    },
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-mock>=3.12.0",
            "pytest-cov>=4.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "easyclaude=app.main:main",
            "easyclaude-autostart=app.autostart:main",
        ],
    },
    zip_safe=False,
)
