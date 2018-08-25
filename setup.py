from setuptools import setup

setup(
    name='tinyvirt',
    description="Lightweight libvirt web interface.",
    url='https://github.com/DragoonAethis/tinyvirt',
    license='MIT',

    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Topic :: System :: Systems Administration'
    ],

    author="Dragoon Aethis",
    author_email="rk@dragonic.eu",

    version='0.0.2',
    packages=['tinyvirt'],
    py_modules=['tinyvirt'],
    python_requires='>=3.6.0',
    include_package_data=True,

    install_requires=[
        'Flask>=1.0.0,<1.1.0',
        'flask-classful>=0.14.1,<0.15.0',
        'libvirt-python'
    ]
)
