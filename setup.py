import setuptools
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")

setuptools.setup(
    name="sinara_firmware_compiler",
    version="2025.01.09",
    description="A pure-python library to automate firmware compilation and upload for Sinara devices.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    author="Dimitrios Tsevas",
    author_email="dimitsev@gmail.com",
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        'Programming Language :: Python :: 3'
    ],
    keywords="sinara, firmware, xilinx, vivado, artiq",
    package_dir={"" : "."},
    packages=setuptools.find_packages(where="."),
    python_requires=">=3.0",
    install_requires=[
    ],
    zip_safe=False,
)
