import json
import gzip
import os
from os import listdir
from os.path import isfile, join
import re 
import dill


def write_dill(file_name, data):
    with open(file_name, 'wb') as outfile:
        dill.dump(data, outfile)

def read_dill(file_name):
    with open(file_name, 'rb') as data:
        return dill.load(data)

def replace_all(text, dic):
    for i, j in dic.items():
        text = text.replace(i, j)
    return text

def read_json(file_addr):
    with open(file_addr) as json_data:
        d = json.load(json_data)
    return d

def write_json(file_name, data, indent_length=4):
    with open(file_name, 'w') as outfile:
        json.dump(data, outfile, indent=indent_length)

def write_dill_compressed(file_name, data):
    with gzip.GzipFile(file_name, 'w') as fout:
        fout.write(dill.dumps(data))

def read_dill_compressed(file_name):
    with gzip.GzipFile(file_name, 'r') as fin:
        data = dill.load(fin)
    return data

def write_json_compressed(file_name, data):
    with gzip.GzipFile(file_name, 'w') as fout:
        fout.write(json.dumps(data).encode('utf-8'))

def read_json_compressed(file_name):
    with gzip.GzipFile(file_name, 'r') as fin:
        data = json.load(fin)
    return data

def read_json_compressed_messed_up(file_name):
    with gzip.GzipFile(file_name) as fin:
        data = re.sub("(\w+):", r'"\1":', json.loads(fin.read().decode('utf-8')))
        d = { "False": "false", "True": "true"}
        # mySentence = replace_all(mySentence, d)
        # print(mySentence)

        data = json.loads(replace_all(data, d))
#         data =  data)
#     print(data)
#     data = json.loads(data)
#     print (type(data))
# #     print(data)

    return data

def write_list_compressed(file_name, data):
    with gzip.GzipFile(file_name, 'w') as fout:
        for item in data:
            fout.write(item.encode('utf-8') + b'\n')

def read_list_compressed(file_name):
    with gzip.GzipFile(file_name, 'r') as fin:
        content = []
        for line in fin:
            content.append(line.decode('utf-8').strip())
        return content

def write_list(file_addr, list_content):
    with open(file_addr, 'w') as out_file:
        for item in list_content:
            out_file.write(item.encode('utf-8') + '\n') 

def write_list_simple(file_addr, list_content):
    with open(file_addr, 'w') as out_file:
        for item in list_content:
            out_file.write(item + '\n') 

def write_content(file_addr, content):
    with open(file_addr, 'w') as out_file:        
        out_file.write(content) 

def write_content_bytes(file_addr, content):
    with open(file_addr, 'wb') as out_file:        
        out_file.write(content) 

def append_file(file_name, content):
    with open(file_name, "a") as myfile:
        myfile.write(content + '\n')

def read_file(file_addr):
    with open(file_addr) as f:
        content = f.readlines()
    return content

def read_full_file(file_addr):
    with open(file_addr) as f:
        content = f.read()
    return content

def write_full_file_bytes(file_name, content):
    with open(file_name, "wb") as myfile:
        myfile.write(content)

def write_full_file(file_name, content):
    with open(file_name, "w") as myfile:
        myfile.write(content)

def read_file_newline_stripped(file_path):
    with open(file_path) as f:
        content = [word.strip() for word in f]
    return content

def read_gzip(file_addr):
    with gzip.open(file_addr, 'rb') as gf:
        json_file_content = gf.read()
    return json_file_content

def append_list(file_addr, content):
    with open(file_addr, 'a') as myfile:
        for line in content:
            myfile.write(line + '\n')

def isfloat(x):
    try:
        a = float(x)
    except ValueError:
        return False
    else:
        return True

def isint(x):
    try:
        a = float(x)
        b = int(a)
    except ValueError:
        return False
    else:
        return a == b


def get_files_in_a_directory(directory_path):
    file_list = [f for f in listdir(directory_path) if isfile(join(directory_path, f)) and not f.startswith('.')]
    file_list_path = [os.path.join(directory_path, f) for f in file_list]
    return file_list_path


def get_directories_in_a_directory(directory_path):
    file_list = [f for f in listdir(directory_path) if not isfile(join(directory_path, f)) and not f.startswith('.')]
    file_list_path = [os.path.join(directory_path, f) for f in file_list]
    return file_list_path
