
# Keyboard Layouter Plugin

[![MIT License](https://img.shields.io/github/license/mashape/apistatus.svg)](LICENSE)

Keyboard Layouter is a plugin for [KiCad](http://kicad-pcb.org/)(pcbnew).
This plugin places switch footprints in the location specified by JSON of
[Keyboard Layout Editor](http://www.keyboard-layout-editor.com/).

I have confirmed that it works with pcbnew version (5.1.0)-1 release build on Windows.

![demo](https://raw.githubusercontent.com/yskoht/keyboard-layouter/images/demo.gif)

## Install

Download [keyboard_layouter.py](https://github.com/yskoht/keyboard-layouter/blob/master/keyboard_layouter.py) and put it to the following directory:

- Windows: %APPDATA%/Roaming/kicad/scripting/plugins
- macOS: /Applications/KiCad/kicad.app/Contents/SharedSupport/scripting/plugins
- Linux: ~/.kicad/scripting/plugins

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

Supported switch footprints are Cherry MX in [kicad-footprints/Button_Switch_Keyboard.pretty](https://github.com/KiCad/kicad-footprints/tree/master/Button_Switch_Keyboard.pretty) only. Therefore, the size of switch that can be userd is limited to the following.

- 1.00u (1 x 1)
- 1.25u (1.25 x 1)
- 1.50u (1.5 x 1)
- 1.75u (1.75 x 1)
- 2.00u (2 x 1, 1 x 2)
- 2.25u (2.25 x 1)
- 2.75u (2.75 x 1)
- 6.25u (6.25 x 1)
- ISO Enter

## License

This software is released under the MIT License, see LICENSE.
