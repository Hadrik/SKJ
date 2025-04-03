import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement


def create_student(xml_root: Element, student_id: str):
    '''
    Vytvořte studenta dle loginu.
    Ujistěte se, že student neexistuje, jinak: raise Exception('student already exists')
    '''
    if xml_root.find(f"student[@student_id='{student_id}']") is not None:
        raise Exception('student already exists')

    xml_root.append(Element('student', {'student_id': student_id}))


def remove_student(xml_root: Element, student_id: str):
    '''
    Odstraňte studenta dle loginu
    '''
    xml_root.remove(xml_root.find(f"student[@student_id='{student_id}']"))


def set_task_points(xml_root: Element, student_id: str, task_id: str, points: int):
    '''
    Přepište body danému studentovi u jednoho tasku
    '''
    xml_root.find(f"student[@student_id='{student_id}']*[@task_id='{task_id}']").text = str(points)


def create_task(xml_root: Element, student_id: str, task_id: str, points: int):
    '''
    Pro daného studenta vytvořte task s body.
    Ujistěte se, že task (s task_id) u studenta neexistuje, jinak: raise Exception('task already exists')
    '''
    student = xml_root.find(f"student[@student_id='{student_id}']")
    if student.find(f"task[@task_id='{task_id}']") is not None:
        raise Exception('task already exists')

    SubElement(student, 'task', {'task_id': task_id}).text = str(points)


def remove_task(xml_root: Element, task_id: str):
    '''
    Napříč všemi studenty smažte task s daným task_id
    '''
    for student in xml_root.findall('student'):
        for task in student.findall(f"task[@task_id='{task_id}']"):
            student.remove(task)