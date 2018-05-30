def generate_annotation_text(annotation_json):
    result = []
    for word in annotation_json:
        if word["type"] == "normal":
            result.append(word["text"])
        elif word["type"] == "like":
            result.append(word["text"] + "SPLIT" + "None")
        else:
            result.append(word["text"] + "SPLIT" + word["sense_id"])
    return " ".join(result)