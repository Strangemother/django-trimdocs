# cli

The app can run as a website, its own compile tool (management command)

or exposed as a cli tool, allowing for stickier options.

## usage

### Browser mode

1. Apply setting to config
2. run server


### management compile

Run the management command

```bash
manage.py trimdocs compile
```

### cli

Run the CLI

```bash
trimdocs compile [.]
# searches for .trimdocs maybe
```

Forced options

```bash
trimdocs compile --src /abs/src/docs/ --dest ./docs/
# searches for .trimdocs maybe
```

With config file
```bash
trimdocs compile --settings ./my-settings.py
trimdocs compile --settings ./my-settings.yaml
trimdocs compile --settings ./my-settings.json
```
