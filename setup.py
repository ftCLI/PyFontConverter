import setuptools

setuptools.setup(
    name="PyFontConverter",
    version="1.0.0",
    description="Command line tools to convert font files.",
    author="ftCLI",
    author_email="ftcli@proton.ne",
    url="https://github.com/ftCLI/PyFontConverter",
    packages=setuptools.find_packages(),
    include_package_data=True,
    entry_points={"console_scripts": ["font-converter=font_converter.font_converter:cli"]},
    install_requires=[
        "fonttools==4.39.2",
        "skia-pathops==0.7.4",
        "cffsubr==0.2.9.post1",
        "click==8.1.3",
        "pathvalidate==2.5.2",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    zip_safe=False,
)
