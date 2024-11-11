#!/usr/bin/env python3
import os
import sys
import subprocess

def batch_execute(command, file_pairs):
    for source, config in file_pairs:
        try:
            full_command = command.format(source=source, config=config)
            print(f"Executing: {full_command}")
            result = subprocess.run(full_command, shell=True, check=True, capture_output=True, text=True)
            print("Output:", result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error executing command with files {source} and {config}: {e.stderr}")

command = "python3.12 -m src.main -f {source} -c {config}"

file_pairs = [
    ("verilogcode/andor_1bit.v"       , "config/andor_1bit.json      "),
    ("verilogcode/condition_case.v"   , "config/condition_case.json"),
    ("verilogcode/condition_if.v"     , "config/condition_if.json"),
    ("verilogcode/and.v"              , "config/and.json"),
    ("verilogcode/fulladder.v"        , "config/fulladder.json"),
    ("verilogcode/generate.v"         , "config/generate.json"),
    ("verilogcode/mux4to1.v"          , "config/mux4to1.json"),
    ("verilogcode/shift.v"            , "config/shift.json"),
]

if __name__ == '__main__':
    batch_execute(command, file_pairs)
