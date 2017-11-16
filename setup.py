from setuptools import setup

setup(
    name='tinyvirt',
    description="Lightweight libvirt web interface.",
    author="Dragoon Aethis",
    author_email="rk@dragonic.eu",

    version='0.0.1',
    packages=['tinyvirt'],
    py_modules=['tinyvirt'],
    include_package_data=True,

    install_requires=[
        'Flask==0.12.2',
        'flask-classful==0.14.1',
        'libvirt-python'
    ],

    extras_require={
        'DevelopmentServer': [
            'python-language-server',
            'pyls-mypy'
        ]
    }
)
