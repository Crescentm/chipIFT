#!/usr/bin/env python3
import re
import os
import sys
import json

template = {
    "top_module": "",
    "conditions": [
        {
            "name": "test",
            "expected_output_signals": {},
            "sat_options": {
                "set": {},
                "show": []
            }
        }
    ]
}

pattern_effect = re.compile(r"(?<=signal\(s\)\.\.\.\n)([\s\S]*?)(?=Activation)")
pattern_condition = re.compile(r"(?<=signals\.\.\.\n)([\s\S]*?)(?=\*\*\*\*\*)")

def match_pro(folder_name: str):
    logfile = os.path.join("./",folder_name,"log.txt")
    # print(logfile)
    with open(logfile, "r", encoding='utf-8') as fr:
        filecontent = fr.read()
        res1 = pattern_effect.findall(filecontent)
        res2 = pattern_condition.findall(filecontent)
        effect_list = res1[0].replace("\n"," ").strip().split(" ")
        condition_list = res2[0].replace("\n"," ").strip().split(" ")
        return [effect_list, condition_list]

def gen_json(signal_list: list, top_name: str):
    sinks = signal_list[0]
    sources = signal_list[1]
    # top
    template["top_module"] = top_name
    # show
    template["conditions"][0]["sat_options"]["show"].extend(sources + sinks)
    #expected
    for source in sources:
        template["conditions"][0]["sat_options"]["set"][source] = "1"
    for sink in sinks:
        template["conditions"][0]["expected_output_signals"][sink] = "0"
    return template

if __name__ == "__main__":
    if (len(sys.argv) != 3):
        print("Wrong usage!\n")
    result =  match_pro(str(sys.argv[1]))
    # print(result) 
    json_dict = gen_json(result, sys.argv[2])
    with open(sys.argv[1] +  "/config.json", "w") as f:
        json.dump(json_dict, f)
