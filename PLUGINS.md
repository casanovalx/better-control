# Plugins for Better Control

## Requirements
1. Every plugin must be a Python file and put inside $HOME/.config/better-control/plugins/
2. The program wont search the directory recursively
3. The file must contain a class with the name of the file in the PascalCase format
4. The tab must initialise on itself without calling any functions
5. The class constructor will only be supplied with a Logger and an ArgParse instance (optional)

## Example Plugin
```python
# $HOME/.config/better-control/plugins/example_tab.py

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

from utils.logger import LogLevel, Logger


class ExampleTab(Gtk.Box):
    def __init__(self, logging: Logger) -> None:
        self.logging = logging
        self.set_margin_start(15)
        self.set_margin_end(15)
        self.set_margin_top(15)
        self.set_margin_bottom(15)
        self.set_hexpand(True)
        self.set_vexpand(True)

        hello_world = Gtk.Label()
        hello_world.set_markup("<span weight='bold' size='large'>Hello, World!</span>")

        self.pack_start(hello_world)
```