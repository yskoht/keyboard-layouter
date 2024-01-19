# Keyboard Layouter Plugin

[![MIT License](https://img.shields.io/github/license/mashape/apistatus.svg)](LICENSE)

Keyboard Layouter is a plugin for [KiCad](http://kicad.org/)(pcbnew).
This plugin places switch footprints in the location specified by JSON of
[Keyboard Layout Editor](http://www.keyboard-layout-editor.com/).

I have confirmed that it works with following pcbnew versions

- (7.0.10) release build on Windows

![demo](https://raw.githubusercontent.com/yskoht/keyboard-layouter/images/demo.gif)

## Install

Download [keyboard_layouter.py](https://github.com/yskoht/keyboard-layouter/blob/master/keyboard_layouter.py) and put it to the following directory:

`Tools` > `External Plugins` > `Reveal Plugin Folder in Finder` (or `Open Plugin Directory` in Windows)

![](https://user-images.githubusercontent.com/34795067/168416745-5556e6a3-199a-4f32-bf00-bdd5998a3e13.png)

## Usage

### Preparation

Make keyboard layout at [Keyboard Layout Editor](http://www.keyboard-layout-editor.com/). Top left legend should be the reference number of the switch footprint. And download JSON file.

![keyboard-layout-editor](https://raw.githubusercontent.com/yskoht/keyboard-layouter/images/keyboard-layout-editor.png)

I have created [keyboard-layouter-playground](https://github.com/yskoht/keyboard-layouter-playground) so that you can quickly try the Keyboard Layouter plugin.
This repository has [sample-json](https://github.com/yskoht/keyboard-layouter-playground/tree/master/sample-json) and sample netlist.

### Execution

Open Pcbnew and choose "Tools" -> "External plugins" -> "Keyboard Layouter".

![pcbnew](https://raw.githubusercontent.com/yskoht/keyboard-layouter/images/pcbnew.png)

![keyboard-layouter](https://raw.githubusercontent.com/yskoht/keyboard-layouter/images/keyboard-layouter.png)

Select your JSON file and push "Run" button.

## Limitation

Supported switch footprints are Cherry MX in [kicad-footprints/Button_Switch_Keyboard.pretty](https://github.com/KiCad/kicad-footprints/tree/master/Button_Switch_Keyboard.pretty) only. Therefore, the size of switch that can be used is limited to the following.

- 1.00u (1 x 1)
- 1.25u (1.25 x 1)
- 1.50u (1.5 x 1)
- 1.75u (1.75 x 1)
- 2.00u (2 x 1, 1 x 2)
- 2.25u (2.25 x 1)
- 2.75u (2.75 x 1)
- 6.25u (6.25 x 1)
- ISO Enter

## For installation on older KiCad (v5, v6)

Please use [Release 0\.2\.0 · yskoht/keyboard\-layouter](https://github.com/yskoht/keyboard-layouter/releases/tag/0.2.0).

I have confirmed that it works with following pcbnew versions

- (5.1.0-1) release build on Windows
- (6.0.5) release build on Windows
- (6.0.5-0) release build on macOS

In KiCad v5, put the script in the following path

- Windows: `%APPDATA%/Roaming/kicad/scripting/plugins`
- macOS: `~/Library/Application Support/kicad/scripting/plugins` or `~/Library/Preferences/kicad/scripting/plugins`
- Linux: `~/.kicad/scripting/plugins` or `~/.kicad_plugins`

## License

This software is released under the MIT License, see LICENSE.
