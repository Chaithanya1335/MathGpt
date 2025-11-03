from setuptools import setup,find_packages


def get_requirements(path="requirements.txt"):

    with open(path,"r") as f:
        requirements = f.readlines()

    requirements = [req for req in requirements if req!="-e ."]
    
    return requirements


setup(
    name="MathRag",
    version="0.1",
    author="Gnana Chaithanya Mangammagari",
    packages=find_packages(),
    install_requires = get_requirements()

)