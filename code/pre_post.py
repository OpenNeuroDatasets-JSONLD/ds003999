#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 22 15:13:51 2021

@author: dmitriy_mikhailov
"""

import os
import re
import csv
from shutil import move
from datetime import datetime

script_dir = os.path.realpath(__file__)
dataset_dir = os.path.dirname(os.path.dirname(script_dir))
relative_path = "new_rawdata/fMRI"
data_dir = os.path.join(dataset_dir, relative_path)

print(data_dir)

def actual_move(src_dir, target_dir):
    (root, dirs, files) = next(os.walk(src_dir))
    for obj in dirs + files:
        actual_src = root + '/' + obj 
        move(actual_src, target_dir)
        print("mv: {0} -> {1}".format(actual_src, target_dir))
        
        

#Извлекаем список всех папок
(root_dir, subject_dir_list, trash) = next(os.walk(data_dir))

#Делаем регулярные выражения по которым будем извлекать имена и даты
name_patt = re.compile("[a-z]+")
date_patt = re.compile("[0-9]{2}.[0-9]{2}.[0-9]{4}")

#Делаем словарь {<name> : (<date>, <dir_name>)}
main_dict = {}
for subject_dir in subject_dir_list:
    name_match = name_patt.search(subject_dir)
    date_match = date_patt.search(subject_dir)
    
    if name_match and date_match:
        name = name_match[0]
        date = datetime.strptime(date_match[0], '%d.%m.%Y')
        
        
        if not name in main_dict.keys():
            main_dict[name] = [(date, subject_dir)]
        else:
            main_dict[name].append((date, subject_dir))
    else:
        raise AttributeError("Dir hasn't name in form <pat_name><day>-<mounth>")
    
#Сортируем внутри каждого имени по дате
for name in main_dict:
    main_dict[name].sort(key = lambda tup: tup[0])
    
#Переносим нужные файлы в нужные директории
count = 0
name2id = []
for name in main_dict:
    #создать папки
    dir_name = "sub-{0:0=2d}".format(count)
    
    name2id_inst = dict()
    name2id_inst['name'] = name
    name2id_inst['id'] = dir_name
    name2id_inst['pre_data'] = main_dict[name][0][0].strftime('%m.%d.%Y')
    name2id_inst['post_data'] = main_dict[name][-1][0].strftime('%m.%d.%Y')
    name2id.append(name2id_inst)
           
    os.mkdir(root_dir + '/' + dir_name)
    print("mkdir {}".format(root_dir + '/' + dir_name))
    
    target_path_pre = root_dir + '/' + dir_name + '/pre'
    target_path_post = root_dir + '/' + dir_name + '/post'
    
    os.mkdir(target_path_pre)
    os.mkdir(target_path_post)
    print("mkdir {}".format(target_path_pre))
    print("mkdir {}".format(target_path_post))
    
    
    first_path_pre = root_dir + '/' + main_dict[name][0][1]
    first_path_post = root_dir + '/' + main_dict[name][-1][1]
    
    actual_move(first_path_pre, target_path_pre)
    actual_move(first_path_post, target_path_post)
    count+=1

#записываем соответсвие имен и id в файл
keys = ['name', 'id', 'pre_data', 'post_data']
tsv_filename = os.path.join(data_dir, 'name2id.tsv')
with open(tsv_filename, 'w') as output:
    dict_writer = csv.DictWriter(output, keys, dialect='excel-tab')
    dict_writer.writeheader()
    dict_writer.writerows(name2id)

