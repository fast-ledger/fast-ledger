from setuptools import setup, find_packages

setup(
    name="ledger_parser",
    version="0.1.0",
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*"]),
    install_requires=[
        "python-dateutil>=2.8.2",
    ],
    entry_points={
        "console_scripts": [
            # 安裝後即可在終端呼叫 `ledger-parser` 指令
            "ledger-parser=ledger_parser.main:main",
        ],
    },
    include_package_data=True,
    author="lilian",
    description="A parser & report generator for ledger-cli journals",
    python_requires=">=3.8",
)