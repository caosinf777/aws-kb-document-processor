from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="aws-kb-document-processor",
    version="1.0.0",
    author="THAÄROS System",
    author_email="your.email@example.com",
    description="Advanced document processor for AWS Bedrock Knowledge Base",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/aws-kb-document-processor",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "boto3>=1.34.0",
        "PyPDF2>=3.0.0",
        "pdfplumber>=0.10.0",
        "python-docx>=1.1.0",
        "markdown>=3.5.0",
        "beautifulsoup4>=4.12.0",
        "tqdm>=4.66.0",
        "colorama>=0.4.6",
        "pandas>=2.1.0",
        "tiktoken>=0.5.0",
    ],
    entry_points={
        "console_scripts": [
            "process-docs=src.process_docs:main",
        ],
    },
)