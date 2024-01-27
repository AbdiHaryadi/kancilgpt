import sys
sys.path.append("./indobenchmark-toolkit/src")
from transformers import GPT2LMHeadModel
from indobenchmark import IndoNLGTokenizer

gpt_tokenizer = IndoNLGTokenizer.from_pretrained("indobenchmark/indogpt", cache_dir="./huggingface_cache")
gpt_tokenizer.pad_token = gpt_tokenizer.eos_token
kancilgpt = GPT2LMHeadModel.from_pretrained("abdiharyadi/kancilgpt", cache_dir="./huggingface_cache")

def generate_random_story_kancil_gpt():
    print("Generating story, please wait ....")

    stop = False
    while not stop:
        gpt_input = gpt_tokenizer('<s> awal cerita | judul:', return_tensors='pt')
        gpt_out = kancilgpt.generate(**gpt_input, do_sample=True, max_length=512, pad_token_id=gpt_tokenizer.eos_token_id)
        result = gpt_tokenizer.decode(gpt_out[0])
        _, judul_prompt, isi, *end_part = result.split(" | ")
        end_part = "".join(end_part)
        _, *judul_words = judul_prompt.split()
        judul = " ".join(judul_words)

        print(f"Judul: {judul}")
        print(isi)

        if "</s>" in judul or "</s>" in isi or "|" in isi or (not any(end_part.startswith(x) for x in ["bersambung", "tamat"])):
            print("Invalid output! Regenerating ....")
            continue

        quote_count = 0
        for c in isi:
            if c == "\"":
                quote_count += 1

        if quote_count % 2 != 0:
            print("Invalid output! Regenerating ....")
            continue

        stop = True

    total_isi = isi

    while not end_part.startswith("tamat"):
        i = 0
        in_quote = False
        end_sentence = False
        limit = 1750
        while i < len(isi) and not (end_sentence and (not in_quote) and isi[i] == " " and (len(isi) - i) < limit):
            if isi[i] == "\"":
                in_quote = not in_quote

            if end_sentence:
                end_sentence = isi[i] not in "abcdefghijklmnopqrstuvwxyz"
            else:
                end_sentence = isi[i] in ".?!"

            i += 1
        # i == len(isi) or end_sentence or (not in_quote) or isi[i] == " "

        while i < len(isi) and not (isi[i] in "abcdefghijklmnopqrstuvwxyz\""):
            i += 1
        # i == len(isi) or isi[i] in "abcdefghijklmnopqrstuvwxyz\""

        if i == len(isi):
            raise ValueError("What???")

        next_isi = isi[i:]

        stop = False
        while not stop:
            gpt_input = gpt_tokenizer(f'<s> pertengahan cerita | judul: {judul} | {next_isi}', return_tensors='pt')
            gpt_out = kancilgpt.generate(**gpt_input, do_sample=True, max_length=512, pad_token_id=gpt_tokenizer.eos_token_id)
            result = gpt_tokenizer.decode(gpt_out[0])

            _, judul_prompt, isi, *end_part = result.split(" | ")
            end_part = "".join(end_part)
            _, *judul_words = judul_prompt.split()
            judul = " ".join(judul_words)

            if isi[len(next_isi) + 1:].strip() != "":
                print(isi[len(next_isi) + 1:])

            if "</s>" in isi or "|" in isi or (not any(end_part.startswith(x) for x in ["bersambung", "tamat"])):
                print("Invalid output! Regenerating ....")
                continue

            quote_count = 0
            for c in isi:
                if c == "\"":
                    quote_count += 1

            if quote_count % 2 != 0:
                print("Invalid output! Regenerating ....")
                continue

            stop = True

        total_isi += " " + isi[len(next_isi) + 1:]

    print("(tamat)")
    return {
        "judul": judul,
        "isi": total_isi
    }

if __name__ == "__main__":
    import json
    import os

    story = generate_random_story_kancil_gpt()
    judul = "-".join("".join([(x if x in "abcdefghijklmnopqrstuvwxyz" else " ") for x in story["judul"]]).strip().split())
    filename = f"{judul}.json"

    postfix_number = 1
    while os.path.isfile(f"drafts/{filename}"):
        postfix_number += 1
        filename = f"{judul}-{postfix_number}.json"
    # the file doesn't exists
    
    with open(f"drafts/{filename}", mode="w") as fp:
        json.dump(story, fp, indent=4)

    print(f"Story saved at \"drafts/{filename}\".")
