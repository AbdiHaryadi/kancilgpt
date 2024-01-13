import sys
sys.path.append("./indobenchmark-toolkit/src")
from transformers import GPT2LMHeadModel
from indobenchmark import IndoNLGTokenizer

gpt_tokenizer = IndoNLGTokenizer.from_pretrained("indobenchmark/indogpt", cache_dir="./huggingface_cache")
gpt_tokenizer.pad_token = gpt_tokenizer.eos_token
kancilgpt = GPT2LMHeadModel.from_pretrained("abdiharyadi/kancilgpt", cache_dir="./huggingface_cache")

def generate_random_story_kancil_gpt():
    print("Generating story ....")

    prompt = "<s> awal cerita | judul:"
    gpt_input = gpt_tokenizer(prompt, return_tensors="pt")
    gpt_out = kancilgpt.generate(**gpt_input, do_sample=True, max_new_tokens=512, pad_token_id=gpt_tokenizer.eos_token_id)
    result = gpt_tokenizer.decode(gpt_out[0])

    _, judul_prompt, isi, *end_part = result.split(" | ")
    end_part = "".join(end_part)
    _, *judul_words = judul_prompt.split()
    judul = " ".join(judul_words)
    print(judul)
    print("-" * len(judul))

    contents = []

    i = 0
    in_quote = False
    end_sentence = False
    while i < len(isi) and not (end_sentence and (not in_quote) and isi[i] == " " and i >= 300):
        if isi[i] == "\"":
            in_quote = not in_quote

        if end_sentence:
            end_sentence = isi[i] in "abcdefghijklmnopqrstuvwxyz"
        else:
            end_sentence = isi[i] in ".?!"

        i += 1
    # i == len(isi) or (end_sentence and (not in_quote) and isi[i] == " " and i >= 300)

    print(isi[:i])
    contents.append(isi[:i])

    if i < len(isi):
        i += 1
        second_half_isi = isi[i:]
        print(second_half_isi)
        contents.append(second_half_isi)
    else:
        second_half_isi = ""

    if end_part.startswith("tamat"):
        print(isi)
        return {
            "judul": judul,
            "isi": isi
        }

    while not end_part.startswith("tamat"):
        prompt = f"<s> pertengahan cerita | judul: {judul} | {second_half_isi}"
        gpt_input = gpt_tokenizer(prompt, return_tensors="pt")
        gpt_out = kancilgpt.generate(**gpt_input, do_sample=True, max_new_tokens=512, pad_token_id=gpt_tokenizer.eos_token_id)
        result = gpt_tokenizer.decode(gpt_out[0])

        _, _, continued_isi, *end_part = result.split(" | ")
        end_part = "".join(end_part)

        if second_half_isi != "":
            i = len(second_half_isi) + 1
        else:
            i = 0

        second_half_isi = continued_isi[i:]
        second_half_isi = second_half_isi.strip()
        if second_half_isi != "":
            print(second_half_isi)
            contents.append(second_half_isi)
            isi += " " + second_half_isi

    # end_part startswith tamat
    print("(tamat)")
    return {
        "judul": judul,
        "contents": contents
    }

if __name__ == "__main__":
    import json
    import os

    story = generate_random_story_kancil_gpt()
    judul = "-".join(story["judul"].split())
    filename = f"{judul}.json"

    postfix_number = 1
    while os.path.isfile(f"drafts/{filename}"):
        postfix_number += 1
        filename = f"{judul}-{postfix_number}.json"
    # the file doesn't exists
    
    with open(f"drafts/{filename}", mode="w") as fp:
        json.dump(story, fp, indent=4)

    print(f"Story saved at \"drafts/{filename}\".")
