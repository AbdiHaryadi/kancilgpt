from collections import Counter
import json
import math
import sys

if len(sys.argv) < 2:
    raise ValueError("Need path as first argument.")

path = sys.argv[1]
with open("drafts/gajah-dan-monyet.json") as f:
    story = json.load(f)

content = " ".join(story["contents"])
content = "".join((c if c in "abcdefghijklmnopqrstuvwxyz" else " ") for c in content)
tokens = content.strip().split()

trigram_counter = Counter()
trigram_counter[f"START_START_{tokens[0]}"] += 1
trigram_counter[f"START_{tokens[0]}_{tokens[1]}"] += 1

for i in range(len(tokens) - 2):
    trigram_key = "_".join(tokens[i:i+3])
    trigram_counter[trigram_key] += 1

trigram_counter[f"{tokens[-2]}_{tokens[-1]}_END"] += 1
trigram_counter[f"{tokens[-1]}_END_END"] += 1

dcr_tf_data = {}
with open("dcr_tf.jsonl") as fp:
    for line in fp:
        data = json.loads(line)
        dcr_tf_data[data["id"]] = data

with open("dcr_df.json") as fp:
    df_data = json.load(fp)

df_data["count"] += 1
for trigram, freq in trigram_counter.items():
    if trigram in df_data["df"]:
        df_data["df"][trigram] += 1
    else:
        df_data["df"][trigram] = 1

df_data["idf"] = {}
for k, v in df_data["df"].items():
    df_data["idf"][k] = 1 + math.log(df_data["count"] / v)

story_tf_idf = {}
squared_story_vec_length = 0.0
for k, v in trigram_counter.items():
    story_tf_idf[k] = v * df_data["idf"][k]
    squared_story_vec_length += story_tf_idf[k] ** 2

story_vec_length = math.sqrt(squared_story_vec_length)
log_story_vec_length = math.log(story_vec_length)

with open("dcr_tf.jsonl") as fp:
    max_cos_sim = 0.0
    most_similar_doc = -1

    for line in fp:
        other_data = json.loads(line)
        other_tf = other_data["tf"]
        other_tf_idf = {}
        squared_other_vec_length = 0.0
        for k, v in other_tf.items():
            other_tf_idf[k] = v * df_data["idf"][k]
            squared_other_vec_length += other_tf_idf[k] ** 2

        other_vec_length = math.sqrt(squared_other_vec_length)
        log_other_vec_length = math.log(other_vec_length)

        vec_dot = 0.0
        for trigram, weight in story_tf_idf.items():
            if trigram in other_tf_idf:
                other_weight = other_tf_idf[trigram]
                vec_dot += weight * other_weight

        if vec_dot != 0.0:
            log_cos_sim = math.log(vec_dot) - log_story_vec_length - log_other_vec_length
            cos_sim = math.exp(log_cos_sim)
        else:
            cos_sim = 0.0

        if cos_sim > max_cos_sim:
            max_cos_sim = cos_sim
            most_similar_doc = other_data["id"]

        if max_cos_sim >= 0.28:
            break

    # For now, it just an ID. We will show the URL in the future.
    if max_cos_sim >= 0.28:
        print("Similarity: >= 28.00% (potentially plagiarism!)")
        print("Similar doc ID:", most_similar_doc)
    elif max_cos_sim > 0.02:
        print(f"Similarity: {100 * max_cos_sim:.2f}%")
        print("Most similar doc ID:", most_similar_doc)
    else:
        print(f"Similarity: {100 * max_cos_sim:.2f}%")
        print("No similar documents.")
