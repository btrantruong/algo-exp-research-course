# Previewing the site locally

Run these from the repo root.

## One-time setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements.txt
```

## Start

```bash
.venv/bin/python scripts/build_site.py
python3 -m http.server 8000 --directory build
```

Open <http://127.0.0.1:8000/> (Resources tab: <http://127.0.0.1:8000/#resources>).

## After editing

The server keeps serving the old build. Rebuild in a second terminal, then hard-refresh the browser (Cmd+Shift+R):

```bash
.venv/bin/python scripts/build_site.py
```

## Stop

Press `Ctrl+C` in the terminal running the server.
If it was started in the background: `pkill -f "http.server 8000"`.

If you see `Address already in use`, an old server is still running. Stop it as above, or use another port (`8001`).

`build/` is generated and git-ignored.
