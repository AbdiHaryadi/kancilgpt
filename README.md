# KancilGPT

## How to Use
1. `git submodule update --init --recursive`
2. `pip install -r requirements.txt`
3. Generate a story: `py kancilgpt.py`
4. Validate the originality of a story: `py check_originality.py <path>`

To publish the story to Story3:
1. Copy `config_template.json` to `config.json`, and set the API key.
2. Publish to Story3: `py story3.py publish <path>`
