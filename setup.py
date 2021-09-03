from setuptools import setup, find_packages


long_description = open("README.md").read()

setup(
    name="HASilla",
    version="0.1.0",
    license="MIT",
    url="https://github.com/DAVZAN/hasilla",
    author="Davide Zanatta",
    author_email="me@davidezanatta.com",
    description="Python module to help parse and construct Silla products MQTT messages. (Used in Silla Home Assistant integration)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    platforms="any",
    install_requires=list(val.strip() for val in open("requirements.txt")),
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires='>=3.6',
)