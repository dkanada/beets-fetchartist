# fetchartist

A plugin that fetches artist covers from last.fm and places them in the artist directories.
They removed this functionality from their API a while ago so this library is parsing the HTML and manually grabbing the images off their site.
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
Only the `filename` option exists at the moment, which will determine the filename of the images.
It will default to empty and use the artist names.

```sh
fetchartist:
  filename: "poster"
```

## Usage

This plugin should be the same as any other plugin for beets when using a recent version.

```sh
Usage: beet fetchartist [options]

Options:
-h, --help   show this help message and exit
-f, --force  force overwrite existing artist covers
```
