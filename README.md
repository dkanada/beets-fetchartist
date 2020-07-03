# fetchartist

A plugin that fetches artist covers from last.fm and places them in the artist directories.

Automatically fetching artist covers during import is not yet supported.

## Installation

The plugin requires `pylast` and `requests` which can be installed using `pip` on the host machine.

```sh
sudo pip install pylast requests
```

Afterwards, beets has to be configured to use the plugin.

```sh
pluginpath:
  ~/fetchartist

plugins: fetchartist
```

## Configuration

The configuration is located in the fetchartist section.

```sh
fetchartist:
  filename: "poster"
```

* filename: If set the value will be used as filename for the artist covers.
  If it is empty, the artist's name will be used instead. Default: `""`

## Usage

```sh
Usage: beet fetchartist [options]

Options:
-h, --help   show this help message and exit
-f, --force  force overwrite existing artist covers
```
