import setuptools

from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setuptools.setup(
    name="PyFontConverter",
    version="1.0.2",
    description="Command line font converter.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="ftCLI",
    author_email="ftcli@proton.me",
    url="https://github.com/ftCLI/PyFontConverter",
    packages=setuptools.find_packages(),
    include_package_data=True,
    entry_points={"console_scripts": ["font-converter=font_converter.font_converter:cli"]},
    install_requires=[
        "fonttools>=4.39.2",
        "skia-pathops>=0.7.4",
        "cffsubr>=0.2.9.post1",
        "click>=8.1.3",
        "pathvalidate>=2.5.2",
        "PyQt5==5.15.9"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    zip_safe=False,
)
