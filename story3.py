import json
import requests

with open("config.json") as f:
    config = json.load(f)

def publish_story(story_path):
    with open(story_path) as fp:
        story = json.load(fp)
    
    # Prepare the Story3 batch
    sentences = []
    sentence_prefix_sum_length = [0]
    isi = story["isi"]
    i = 0
    while i < len(isi):
        current_sentence = ""
        in_quote = False
        end_sentence = False
        while i < len(isi) and not (end_sentence and (not in_quote) and isi[i] == " "):
            current_sentence += isi[i]
            if isi[i] == "\"":
                in_quote = not in_quote

            if end_sentence:
                end_sentence = isi[i] not in "abcdefghijklmnopqrstuvwxyz"
            else:
                end_sentence = isi[i] in ".?!"

            i += 1
        # i == len(isi) or end_sentence or (not in_quote) or isi[i] == " "
        
        sentences.append(current_sentence)
        sentence_prefix_sum_length.append(sentence_prefix_sum_length[-1] + len(current_sentence))

        while i < len(isi) and not (isi[i] in "abcdefghijklmnopqrstuvwxyz\""):
            i += 1
        # i == len(isi) or isi[i] in "abcdefghijklmnopqrstuvwxyz\""
        
    limit = 300
    i_start = 0
    i_end = 1
    batches = []

    while i_end < len(sentences):
        while (i_end < len(sentences)) and (sentence_prefix_sum_length[i_end] - sentence_prefix_sum_length[i_start] + (i_start - i_end) < limit):
            i_end += 1
        # i_end == len(sentences) or reach limit

        if i_end < len(sentences):
            batches.append(" ".join(sentences[i_start:i_end]))
            i_start = i_end
            i_end += 1

        if limit == 300:
            # To make a twist longer.
            limit = 600
    
    # i_end == len(sentences)
    
    batches.append(" ".join(sentences[i_start:i_end]))

    print(f"Total batch: {len(batches)}")
    
    print("Posting batch 1 ....")

    res = post_to_story3_with_log(
        endpoint="/api/v2/stories",
        data={
            "title": story["judul"],
            "body": batches[0]
        }
    )


    if res.status_code != 201:
        raise ValueError(f"Unexpected response status code: {res.status_code}. Check log.txt.")
    
    story3_data = json.loads(res.text)
    if "hashId" not in story3_data:
        raise ValueError(f"Expecting hashId key, got unexpected JSON:\n{story3_data}")
    hash_parent_id = story3_data["hashId"]
    
    print("Publishing batch 1 ....")

    res = post_to_story3_with_log(
        endpoint=f"/api/v2/twists/{hash_parent_id}/publish"
    )

    if res.status_code != 201:
        raise ValueError(f"Unexpected response status code: {res.status_code}. Check log.txt.")

    batch_idx = 1
    while batch_idx < len(batches):
        # Create twist title
        isi = batches[batch_idx]
        isi_idx = 0
        end_idx = min(len(isi), 80)
        in_quote = False
        end_sentence = False
        while isi_idx < end_idx and not (end_sentence and (not in_quote) and isi[isi_idx] == " "):
            if isi[isi_idx] == "\"":
                in_quote = not in_quote

            if end_sentence:
                end_sentence = isi[isi_idx] in "abcdefghijklmnopqrstuvwxyz"
            else:
                end_sentence = isi[isi_idx] in ".?!"

            isi_idx += 1
        # i == end_i or (end_sentence and (not in_quote) and isi[i] == " ")
        
        if (isi_idx < end_idx) or end_idx < 80 or (end_sentence and (not in_quote)):
            judul = isi[:isi_idx]
        else:
            judul = isi[:isi_idx - 3] + "..."

        print(f"Posting batch {batch_idx + 1} ....")

        res = post_to_story3_with_log(
            endpoint="/api/v2/twists",
            data={
                "hashParentId": hash_parent_id,
                "isExtraTwist": False, # I am not sure what the API asks here, but I assume it's False because it's a first twist.
                "title": judul,
                "body": isi
            }
        )

        if res.status_code != 201:
            raise ValueError(f"Unexpected response status code: {res.status_code}. Check log.txt.")
        
        story3_data = json.loads(res.text)
        if "hashId" not in story3_data:
            raise ValueError(f"Expecting hashId key, got unexpected JSON:\n{story3_data}")
        hash_parent_id = story3_data["hashId"]

        print(f"Publishing batch {batch_idx + 1} ....")

        res = post_to_story3_with_log(
            endpoint=f"/api/v2/twists/{hash_parent_id}/publish"
        )

        if res.status_code != 201:
            raise ValueError(f"Unexpected response status code: {res.status_code}. Check log.txt.")
        
        batch_idx += 1

    # batch_idx == len(batches)

STORY3_DOMAIN = "https://story3.com"
def post_to_story3_with_log(*, endpoint: str, data: dict | None = None):
    actual_endpoint = STORY3_DOMAIN + endpoint
    with open("log.txt", mode="a") as fp:
        print(f">>> POST\endpoint={actual_endpoint}\tdata={data}", file=fp)
    if data is not None:
        json_data = json.dumps(data)
        res = requests.post(actual_endpoint, data=json_data, headers={
            "x-auth-token": config["api_key"],
            "Content-Type": "application/json"
        })
    else:
        res = requests.post(actual_endpoint, headers={
            "x-auth-token": config["api_key"]
        })
    with open("log.txt", mode="a") as fp:
        print(res.text, file=fp)
    return res

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        raise ValueError("Specify task as a first argument.")
    
    if sys.argv[1] == "publish":
        if len(sys.argv) < 3:
            raise ValueError("Specify story path as a second argument.")
        
        story_path = sys.argv[2]
        res = publish_story(story_path=story_path)
        print("Analyzed!")
    else:
        raise NotImplementedError
