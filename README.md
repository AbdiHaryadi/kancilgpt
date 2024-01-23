# KancilGPT
This README only focuses on "how to use". For more information about the model itself, please go to [Huggingface](https://huggingface.co/abdiharyadi/kancilgpt).

## How to Use
1. `git submodule update --init --recursive`
2. `pip install -r requirements.txt`
3. Generate a story: `py kancilgpt.py`
4. Validate the originality of a story: `py check_originality.py <path>`

To publish the story to Story3:
1. Copy `config_template.json` to `config.json`, and set the API key.
2. Publish to Story3: `py story3.py publish <path>`

## Limitations
- KancilGPT can generate a low-coherent, illogical story, and sometimes it's humorous. Please validate what you publish in Story3.
- The analytics were not used. It should be done manually.
- The originality validation doesn't take accounts of other published stories in Story3. That's why it can't be automatically run forever to generate and publish massive number of stories. The current story can be a little variation of the previous one.
- There are no safety algorithm to prevent inapproriate stories. 
