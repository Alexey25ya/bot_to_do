import csv
import string
from typing import List


global tasks
global searched_tasks
tasks = []
searched_tasks = []
filter_tasks = [] 


def search_task(searchstring: str, tasks:List):
    '''
    Поиск в списке
    '''
    for task in tasks:
        for value in task.values():
            if searchstring in value:
                   searched_tasks.append(task)
    return searched_tasks        

def view_tasks(tasks: List) -> string:
    '''
    Запись в строку для Telegram
    '''
    strings =[]
    for task in tasks:
        for key, value in task.items():
            strings.append('{}: {}'.format(key, value))
        strings.append(' ')        
    result ='\n'.join(strings)        
    return result


def read_csv():
    '''
    Чтение из файла csv
    '''
    with open('todo1.csv','r', encoding='utf-8') as f:
        tasks = [{key: value  for key, value in task.items()}
                for task in csv.DictReader(f, skipinitialspace=True)]
    return tasks
 
#print(read_csv())

def write_csv(tasks: List) -> None:
    '''
    Запись в csv фаил. 
    '''
    fieldnames = tasks[0].keys()
    with open('todo1.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames,lineterminator='\n')
        writer.writeheader()
        writer.writerows(tasks)

def delete_task(contact):
    """
    Удаляет контакт
    """
    f = open('todo1.csv', 'r',encoding = 'utf-8')
    lines = f.readlines()
    f.close()
    f = open('todo1.csv', 'w',encoding = 'utf-8',newline='')
    for line in lines: 
        if contact in line:              
            search_line=f'Задача <{line}> удалена'
        if contact not in line: 
            search_line=f'Задача <{contact}> не найдена'
            f.write(line)
    f.close()
    return search_line


