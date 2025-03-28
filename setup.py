from setuptools import setup

setup(
    name='BrickDifference',
    version='0.1.0',
    description='This is a graphical Python program for calculating the difference between two LDraw files.',
    url='https://github.com/Nexusnui/Brick-Difference',
    author='Nexusnui',
    author_email='developer@nexusnui.de',
    license='GPL 3.0',
    packages=['BrickDifference',
              'BrickDifference.icons',
              ],
    package_data={
        'BrickDifference.icons': ['BrickDifference_Icon.ico', 'BrickDifference_Icon_*.png'],
    },
    install_requires=[
                      "PyQt6==6.8.1",
                      ],
    entry_points={
        'gui_scripts': [
            'BrickDifference = BrickDifference.app:run',
        ]
    },

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        "Operating System :: OS Independent",
        'Programming Language :: Python :: 3.12',
    ],
)
