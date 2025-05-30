<h1 align="center">🎨 artworker</h1>
<p align="center">A CLI tool to generate beautiful and compact posters for your favorite albums. Free, open-source and configurable print-it-yourself alternative to commercially available services offered by e.g. <a href="https://www.zeitgeistgalerie.de/collections/album-cover-poster">ZeitGeistGalerie</a>, <a href="https://www.redbubble.com/de/shop/album+cover+posters">
RedBubble</a> or <a href="https://www.amazon.com/s?k=album+cover+posters&crid=1NML8INJHOXOS&sprefix=album+cover+poster%2Caps%2C182&ref=nb_sb_noss_1">Amazon</a>.</p>
<div align="center">
    <a href="https://github.com/maxschroen/artworker"><img src="https://img.shields.io/github/stars/maxschroen/artworker" alt="Stars Badge"/></a>
    <a href="https://github.com/maxschroen/artworker/network/members"><img src="https://img.shields.io/github/forks/maxschroen/artworker" alt="Forks Badge"/></a>
    <a href="https://github.com/maxschroen/artworker/pulls"><img src="https://img.shields.io/github/issues-pr/maxschroen/artworker" alt="Pull Requests Badge"/></a>
    <a href="https://github.com/maxschroen/artworker/issues"><img src="https://img.shields.io/github/issues/maxschroen/artworker" alt="Issues Badge"/></a>
    <a href="https://github.com/maxschroen/artworker/graphs/contributors"><img alt="GitHub contributors" src="https://img.shields.io/github/contributors/maxschroen/artworker?color=2b9348"></a>
    <a href="https://github.com/maxschroen/artworker/blob/main/LICENSE"><img src="https://img.shields.io/github/license/maxschroen/artworker?color=2b9348" alt="License Badge"/></a>
</div>
<h4 align="center">Attributions</h4>
<p align="center"><a href="https://github.com/kazhala/InquirerPy">InquirerPy</a> - <a href="https://github.com/rsms/inter">Inter</a> - <a href="https://developer.apple.com/library/archive/documentation/AudioVideo/Conceptual/iTuneSearchAPI/index.html#//apple_ref/doc/uid/TP40017632-CH3-SW1">iTunes Search API</a> - <a href="https://github.com/scikit-learn/scikit-learn">scikit-learn</a> - <a href="https://github.com/python-pillow/Pillow">Pillow</a> - <a href="https://github.com/psf/requests">requests</a> - <a href="https://github.com/numpy/numpy">NumPy</a></p>


## Contents
- [Examples](#examples)
- [Changelog](#changelog)
- [Requirements](#requirements)
- [Installation](#installation)
- [How To Use](#how-to-use)
- [Roadmap](#roadmap)
- [Known Issues & Limitations](#known-issues--limitations)

## Examples
<p align="center">
  <img src="https://github.com/maxschroen/artworker/blob/main/.docs/knocked-loose-a-tear-in-the-fabric-of-life-ep.jpg?raw=true" width="300" />
  <img src="https://github.com/maxschroen/artworker/blob/main/.docs/lorde-melodrama.jpg?raw=true" width="300" /> 
  <img src="https://github.com/maxschroen/artworker/blob/main/.docs/misery-signals-of-malice-and-the-magnum-heart.jpg?raw=true" width="300">
  <img src="https://github.com/maxschroen/artworker/blob/main/.docs/counterparts-a-eulogy-for-those-still-here.jpg?raw=true" width="300" />
</p>

## Changelog

#### v0.2
- Added overflow checking and mitigation
  - Works for all single per-line elements (album title, artist and copyright notice)

<details>
  <summary>Older Versions</summary>
  <h4>v0.1</h4>
  <ul>
    <li>Removed Pylette dependency
      <ul>
        <li>Image color extraction implemented via K-Means-Clustering (initially seemd counterintuitive but results are of higher visual quality than those from median cut)</li>
      </ul>
    </li>
  </ul>
  <h4>v0.0</h4>
  <ul>
    <li>Initial release</li>
  </ul>
</details>

## Requirements
- [Python](https://www.python.org/downloads/) (tested for > 3.9)
- [Inter Typeface](https://github.com/rsms/inter)


## Installation
After installing all hard [requirements](#requirements), the simplest way to get the script is to clone the repository and then install the required packages via the ```requirements.txt``` file.
1. Clone repository
```bash
# Clone using web url
git clone https://github.com/maxschroen/artworker.git
# OR clone using GitHub CLI
gh repo clone maxschroen/artworker
```

2. Create virtual environment
```bash
# Navigate to folder
cd artworker
# Install virtualenv
pip install virtualenv
# Initiate venv
python3 -m venv artworker
# Activate venv
source artworker/bin/activate
```

3. Install required packages from ```requirements.txt```
```bash
# Install requirements
pip install -r requirements.txt
```

## How To Use
To run the script, simply navigate to the root of the repository and run:
```bash
# Run script
python main.py
```
The script will give you prompts to walk you through the process (see below).

<img src="https://github.com/maxschroen/artworker/blob/main/.docs/demo.gif?raw=true" width="600" />

Output is generated as a self-contained ```.svg``` file, which will be placed in the ```/out``` directory.

To generate a print-friendly file, you can use your favorite SVG rendering engine to open the generated ```.svg``` file and export as ```.png```.

A simple way to do this from the console is (assuming you have [Inkscape](https://inkscape.org/de/release/inkscape-0.40/) installed), would be:
```bash
inkscape --export-type="png" YOUR_FILE_NAME.svg
```
## Roadmap
- Fix of [known issues and limitations](#known-issues--limitations)
- Introduction of configurable iTunes QR codes & Spotify scan codes to integrate with the layouts


## Known Issues & Limitations
As the script is in a fairly early stage of development, there currently are some known issues and limitations. These are all on the [roadmap](#roadmap) and will be fixed at some point.
- Albums with more than 16 tracks are currently not supported. All tracks exceeding this limit will be cut off and missing in the generated file.
- Significantly long track titles will overflow to the right / left or collide with other track titles on the same line.