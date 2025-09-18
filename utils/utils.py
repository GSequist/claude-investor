import tiktoken
import json
import os

#############################################

tokenizer = tiktoken.get_encoding("cl100k_base")

############################################

FAISS_DB = os.path.join(os.getcwd(), "faiss")
WORK_FOLDER = os.path.join(os.getcwd(), "workspace/")
KERNEL_PID_DIR = os.path.join(os.getcwd(), "process_pids")


###########################################


def extract_json_(text):
    """util to extract jsons"""
    results = []
    i = 0
    while i < len(text):
        if text[i] == "{":
            bracket_count = 1
            start = i
            i += 1

            while i < len(text) and bracket_count > 0:
                if text[i] == "{":
                    bracket_count += 1
                elif text[i] == "}":
                    bracket_count -= 1
                i += 1

            if bracket_count == 0:
                json_candidate = text[start:i]
                try:
                    parsed = json.loads(json_candidate)
                    results.append(parsed)
                except:
                    pass
        else:
            i += 1
    return results


####################################################
