import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="py-mon",
    version="1.1.0",
    author="trustedmercury",
    author_email="trustedmercury@gmail.com",
    description="Simple package to automatically restart application when file changes are detected!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/trustedmercury/py-mon",
    keywords="development, testing, monitor",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        "console_scripts": ["pymon=pymon.main:main"]
    }
)
