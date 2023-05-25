# encoding: utf-8
# !/usr/bin/env python

"""
# @Author: Andrey M.
# @Contact: <muraigtor@gmail.com>
# @Site:
# @Version: 1.0
# @License: Apache Licence
# @File: app.py
# @Time: 10.03.2023 10:46
# @Software: IntelliJ IDEA

Скрипт Для перемещения ресурсов в стейте из модулей в простые ресурсы с выделением стейтов в отдельные файлы

"""


import glob
from inspect import currentframe
from python_terraform import *
from pathlib import Path
import shutil
from jinja2 import Environment, FileSystemLoader


def get_linenumber():
    cf = currentframe()
    return cf.f_back.f_lineno


"""
 Создаем переменные для работы скрипта: имя файла стейта, рабочую директорию,
 файл для внеснеия изменений после пермещения модулей
"""
""" tfstate - это файл со стейтом """
tfstate = '30-03-2023_09:25:15_mystate.json'
directory: str = '/тут_адрес_до_папки_где_находится_текуший_проект:_папки_python_src_и_sources_с_шаблонами_jinja2'

""" Указываем папку для выгрузки созданныхз стейт-файлов модулей """
directory_tg = '/тут_адрес_до_папки_куда_будем_складывать_созданные_папки_и_файлы/tg/dtline'
source_path = f"{directory}/sources"
path_to_source_files = '/тут_адрес_до_папки_откуда_забирать_файлы_с_описанием_ресурсов_ТФ'
# main_file = f"{directory}/main.tf"

""" Вспомогательные директории """
_tfstate = f"{directory}/{tfstate}"
_tfdir = f"{directory}/tfst"
tfst_tfstate = f"{directory}/tfst/{tfstate}"

""" Добавляем файл с кредами до датацентра такого плана:
# file credentials.auto.tfvars
vcd_user     = "USER"
vcd_password = "PASSWORD"
vcd_org      = "ORGANISATION"
vcd_vdc      = "NAME_VDC"
vcd_url      = "https://URL_TO_DATACENTR.ru/api"
"""
credit_var = str(Path.cwd()) + "/" + "credentials.auto.tfvars"
# -#return_code, stdout, stderr = t.validate_cmd(*arguments, **options)

"""
  Создаем экземпляр класса Terrafrom для выполнения команд state list, state mv
"""
t = Terraform(working_dir=directory, var_file=credit_var)

"""
 Создаем список модулей, которые получаем с датацентра командой terraform state list
 Создаем список ресурсов, которые получаем с датацентра командой terraform state list
"""
list_module = []
list_resource = []
hash_resource = {}

"""
 Создаем списки и массивы для передачи параметров выполнения команд в класс Terraform
"""
arguments = []
options = {}

"""
Описание алгоритма действия скрипта:
# 1. Получаем список модулей из корневого файла main.tf
# 2. Получаем описание ресурсов для каждого модуля module "xxxxxxx" {}
# 3. Создаем наименования модулей, если необходимо(applications/qa -> app/qa_app, applications/qa->app/qa_auth...)
# 4. Создаем файл для описания модуля, в который входят все ресурсы этого модуля ./app/xxxxxxx/main.tf
# 5. Перемещаем описание ресурсов в папку с модулем
# 6. Находим стейт этих ресурсов в общем стейте и перемещаем с созданием отдельных стейтов для каждого ресурса:
# tfstate=23-03-2023_10:00:18_mystate.json; terragrunt state list -state=$tfstate  2>/dev/null \
# | xargs -n1 -I{} terragrunt state mv -state=tfst/$tfstate -state-out=tfst/{}.tfstate {} {}
"""


def move_state_list_to_map(_stdout, _tfst_tfstate):
    """
    Функция для создания файлов - объектов перемещения модулей.
    В результате ее действия создаются множество файлов, в которых содержаться стейты модулей.

    На вход подается вывод команды terragform state list(_stdout) и переменная _tfst_tfstate,
    которая является путем до файла стейта, находящегося в папке tfst.
    Данная папка(tfst) находится в папке с файлами проекта ТФ

    :param _tfst_tfstate: string
    :param _stdout: list
    :return: list_module: list
    """

    """ Проверка существования файлов от предыдущей операции terragrunt state mv """
    my_tfstate = [f for f in glob.glob(f"{_tfdir}/*.tfstate")]
    # print(f"Str:{get_linenumber()}| my_tfstate: |{my_tfstate}|") ; sys.exit()
    """ Если файлы уже существуют, значит их создали ранее. Возвращаем ответ об этом и выходим из функции """
    if my_tfstate:
        """ Возвращаем ответ о существовании файлов """
        return ("В папке есть файлы от предыдущей операции terraform state mv").split(' ')

    """ Если проверка закончилась успешно, запускаем операцию о перемещении ресурсов """
    for count, item in enumerate(list(_stdout)):
        print(f"Str:{get_linenumber()}:{count}: {item}")
        """ Пропускаем пустую итерацию, без модулей """
        if item == '':
            continue
        # print(f"Str:{get_linenumber()}:terragrunt state mv -state={_tfst_tfstate}"
        #       f" -state-out=tfst/{item}.tfstate {item} {item}")
        """ Составляем строку аргументов для операции перемещения ресурсов. Строка состоит из:
         1. пути до файла, в который заноситься информация о перемещении: -state={_tfst_tfstate}
         2. пути, куда помещать файлы со стейтом ресрусов: -state-out=tfst/{item}.tfstate.
        В данной строке у нас указывается перемещать каждый ресурс в самого себя, с выделением в отдельный файл-стейт:
         -state={_tfst_tfstate} -state-out=tfst/{item}.tfstate item, item """
        p = Path(_tfst_tfstate)
        shutil.copy(_tfstate, _tfst_tfstate)
        if not p.is_file():
            print(f"Str:{get_linenumber()}: count: {count} ::_tfst_tfstate |{_tfst_tfstate}")  # sys.exit()
            __arguments = ["pull", f"-state={_tfst_tfstate}", f"-state-out=tfst/{item}.tfstate", item, item]
            return "Стейт-файлы отсутсвуют!\n" \
                   " Создайте стейт-файлы текущей конфигурации, либо укажите их местоположение!\n" \
                   "\nЗапустите функцию создание стейт-файлов!\n".split(' ')
        else:
            print(f"Str:{get_linenumber()}: count: {count} ::p.is_file() |{p.is_file()}")
        # sys.exit()

        """ Получаем вывод операции перемещения ресурсов из корня в отдельные стейты. Данная информация не используется,
        в результате нее создаются необходимые нам файлы командой terraform state mv """
        __arguments = ["mv", f"-state={_tfst_tfstate}", f"-state-out=tfst/{item}.tfstate", item, item]
        module_list = item.split(".", maxsplit=-1)
        __resource = '.'.join(module_list[2:])
        print(f"Str:{get_linenumber()}::: __arguments |{__arguments}")
        __arguments = ["mv", f"-state={_tfst_tfstate}", f"-state-out=tfst/{item}.tfstate", item, __resource]
        print(f"Str:{get_linenumber()}::: __arguments |{__arguments}")  # ; sys.exit()
        __return_code, __stdout, __stderr = t.state_cmd(*__arguments)
        """ Для информации о том, какие ресурсы обрабатывались, создаем список с ними,
        который возвращаем из этой функции """
        list_module.append(item)

    return list_module


def extracting_list_modules(_stdout, _tfst_tfstate=None):
    """
    Функция для получения списков:
    модуей
    ресурсов
    хеша

    Где ключ - модуль, а значение - список ресуров
    На вход подается вывод команды terragrunt state list(_stdout) и переменная _tfst_tfstate,
    которая является путем до файла стейта(в данной функции не используется)

    :param _stdout:
    :param _tfst_tfstate:
    :return:
    """
    _list_module = []
    __list_module = {}
    _list_resource = []
    _module = ''
    # if _module == 'module.vapps':
    #     print(f"  Str:{get_linenumber()}| _module: |{_module}|")
    #     print(f"   Str:{get_linenumber()}| _resource: |{_resource}|")
    #     print(f"   Str:{get_linenumber()}| _list_resource: |{_list_resource}|")
    #     # sys.exit()
    # else:
    #     print(f" Str:{get_linenumber()}| _module: |{_module}|")
    """ Находим в выводе команды ресурсы и помещаем их в массив """
    for count, elem in enumerate(list(_stdout)):
        """ Пропускаем пустую итерацию, без модулей """
        if elem == '':
            continue
        # if count >= 25:
        #     break
        # IFS='.' read -ra arr <<< "$st"
        """ Создаем список из наименования ресурса ,разделенный по точкам """
        module_list = elem.split(".", maxsplit=-1)
        _resource = '.'.join(module_list)
        _module = '.'.join(module_list[:2])
        # print(f"Str:{get_linenumber()}| elem: |{elem}|") #; sys.exit()
        # if _module == "module.astra_app":
        #     print(f"Str:{get_linenumber()}:{count}: |{module_list}|")
        #     print(f"Str:{get_linenumber()}:{count}: |{_resource}|"); sys.exit()
        """ Если список НЕ пустой: """
        """ добавляем с список ресурсов ресурс _resource, если список модулей и ресурсов пустые """
        if len(_module) and len(_list_resource) == 0:
            _list_module.append(_module)
            _list_resource.append(_resource)
            # print(f" Str:{get_linenumber()}| _list_module: |{_list_module}|")
            # print(f" Str:{get_linenumber()}| _list_resource: |{_list_resource}|")
            """ Так как добавили ресурс, необходимо этот ресрс добавить в массив ресурсов, где ключ это имя модуля """
            hash_resource[_module] = _list_resource
        elif _list_module[-1] == _module:
            """ Иначе Если его предыдущий модуль равен модулю текущего ресурса:
            добавляем с список ресурсов ресурс _resource и в список модулей добавляем текущий модуль """
            # print(f" Str:{get_linenumber()}| _list_module[-1]: |{_list_module[-1]}|")
            # print(f" Str:{get_linenumber()}| _module: |{_module}|")
            _list_module.append(_module)
            _list_resource.append(_resource)
            # print(f" Str:{get_linenumber()}| _list_resource: |{_list_resource}|")
            """ Так как добавили ресурс, необходимо этот ресрс добавить в массив ресурсов, где ключ это имя модуля """
            hash_resource[_module] = _list_resource
        else:
            """ Иначе начинаются новые модули и ресурсы,
            значит создаем новый список ресурсов и в него добавляем этот ресурс
            так же создаем новый список модулей и в него добавляем этот модуль"""
            _list_resource = []
            _list_resource.append(_resource)
            _list_module = []
            _list_module.append(_module)
            # print(f" Str:{get_linenumber()}| _list_module: |{_list_module}|")
            # print(f" Str:{get_linenumber()}| _list_resource: |{_list_resource}|")
            """ Так как добавили ресурс, необходимо этот ресрс добавить в массив ресурсов, где ключ это имя модуля """
            hash_resource[_module] = _list_resource

    # print(f" Str:{get_linenumber()}| hash_resource: |{json.dumps(hash_resource, indent=2, ensure_ascii=True)}|")
    # print(f"Str:{get_linenumber()}:{count}: |{hash_resource['module.vapps']}|")
    # sys.exit()
    return _list_module, list_resource, hash_resource


def create_related_files(module_path, _source_path):
    """
    Функция для создания сопутствующих модулю файлов.
    Данные файлы копируются из папки и в них изменяются переменные в соответствии с именем модуля
    На вход подается путь до директории с файлами которые необходимо скопировтаь
    и путь до директорий, куда их необходимо скопировать

    :param _source_path:
    :param module_path:
    :return:
    """

    global module_dir
    """Пропускаем файлы, в пути которых есть упоминание disks, так как это файлы, связанные с модулем описания дисков
    """
    # if "disk" in module_path:
    #     print(f"Str:{get_linenumber()}:: Путь до папки: |{module_path}|")  # ; sys.exit()
    #     return "Ok!"
    # else:
    print(f"Str:{get_linenumber()}:: Путь до папки: |{module_path}|")
    # sys.exit()
    """ Находим имена файлов из папки с шаблонами """
    # sources_file: list[str] = glob.glob(f"{_source_path}/*.hcl")
    # print(f"Str:{get_linenumber()}:: {_source_path}") ; # sys.exit()
    sources_file = list(Path(_source_path).rglob('*.*'))
    if len(sources_file) == 0:
        print(f"Str:{get_linenumber()}:: Шаблонов в папке {Path(_source_path)} для копирования файлов нету!"
              .split())
        return f"Шаблонов в папке {Path(_source_path)} для копирования файлов нету!".split()
    else:
        print(f"Str:{get_linenumber()}:: Шаблоны в папке {Path(_source_path)} для копирования файлов!")
    #     print(f"Str:{get_linenumber()}:: {sources_file}") ; # sys.exit()
    #     # print(f"Str:{get_linenumber()}:: {sources_file[0].split('/')[-1]}") ; # sys.exit()
    """ Получаем имена папок для подстановки в шаблон файла """
    _path = module_path.split("/")
    # print(f"\nStr:{get_linenumber()}:: Путь до папки: |{_path[-1]}|\n") ;sys.exit()
    """ Создаем переменные для подстановки в шаблон """
    render_data = {
        "filename": _path[-1],
        "module_path": module_path.split('/')[-2]
    }
    """ Для каждого файла запускаем процедуру рендеринга """
    for count, data in enumerate(sources_file):
        # print(f" Str:{get_linenumber()}:: str(data): |{str(data)}|")
        # print(f" Str:{get_linenumber()}:: _source_path: |{_source_path}|")
        """ Если в пути нет папки _envcommon и файл сущетвуют, то файл рендерим и записываем в папку модуля """
        if not "_envcommon" in str(data) and Path(data).exists():
            env = Environment(loader=FileSystemLoader(searchpath=_source_path))
            template = env.get_template(str(data).split('/')[-1])
            _output = template.render(**render_data)  # this is where to put args to the template renderer
            # print(f"  Str:{get_linenumber()}:: output: |{_output}|")
            """ Записываем созданный шаблон в файл """
            with open(f"{module_path}/{str(data).split('/')[-1]}", 'w') as the_file:
                the_file.write(f"{''.join(_output)}")
            # print(f"\n  Str:{get_linenumber()}:: Создать файл: |{module_path}/{str(data).split('/')[-1]}|")
            # print(f"  Str:{get_linenumber()}:: module_path: |{module_path.split('/')[-2]}|\n")
        elif "_envcommon" in str(data) and Path(data).exists():
            """ Если имя файла содержит папку _envcommon, то рендерим и записываем его в другое место """
            """ Из абсолютного имени файла шаблона получаем путь до этого файла """
            _data = str(data).split('/')
            print(f"  Str:{get_linenumber()} Путь до папки с шаблонами: |{'/'.join(_data)}|")
            del _data[-1]
            print(f"  Str:{get_linenumber()} Путь до папки с шаблонами: |{'/'.join(_data)}|")
            """ Получаем шаблон и рендерим его """
            env = Environment(loader=FileSystemLoader(searchpath='/'.join(_data)))
            template = env.get_template(str(data).split('/')[-1])
            _output = template.render(**render_data)  # this is where to put args to the template renderer
            """ Создаем отсуствующие папки, папка _envcommon находится выше на два уровня и является общей для всех """
            print(f"  Str:{get_linenumber()}:: module_path: |{module_path}|")
            if not 'vapps' in module_path and not 'networks' in module_path and not 'edges' in module_path:
                module_dir = str(module_path).split('/')[-2]
                p = Path(f"{module_path}/../../_envcommon/{module_dir}/")
                _envcommon = '../../_envcommon'
                print(f"  Str:{get_linenumber()} Папка для шаблона: |{module_dir}|")
                # sys.exit()()
            else:
                module_dir = str(module_path).split('/')[-1]
                p = Path(f"{module_path}/../_envcommon/{module_dir}/")
                _envcommon = '../_envcommon'
                print(f"  Str:{get_linenumber()} Папка для шаблона: |{module_dir}|")
                # sys.exit()()

            p.mkdir(parents=True, exist_ok=True)
            """ Записываем отрендеренный шаблон в файл """
            with open(f"{module_path}/{_envcommon}/{module_dir}/{_path[-1]}.hcl", 'w') as the_file:
                the_file.write(f"{''.join(_output)}")
            # print(f"\n  Str:{get_linenumber()} Создать файл: |{module_path}/_envcommon/{str(data).split('/')[-1]}|")
            # print(f"  Str:{get_linenumber()} _path[-1]: |{_path[-1]}.hcl|")
            # print(f"  Str:{get_linenumber()} \"_envcommon\" in str(data): |{str(data).split('/').pop(-1)}|")
            # print(f"  Str:{get_linenumber()} \"_envcommon\" in str(data): |{str(data)}|\n")
        else:
            """ Иначе мы получаем ссылку, клонируем ее в папку, в дальнейшем она будет вести на существующий файл """
            src = Path(f"../{str(data).split('/')[-1]}")
            dst = Path(f"{module_path}/{str(data).split('/')[-1]}")
            # print(f"Str:{get_linenumber()}:src: |{src}|")
            # print(f"Str:{get_linenumber()}:dst: |{dst}|")
            # print(f"Str:{get_linenumber()}:Try:: Путь до module: |{module_path}|")
            # print(f"Str:{get_linenumber()}:Путь до симлинка: |{str(data).split('/')[-1]}|")
            try:
                # syml = os.symlink(src, dst) # or
                Path(dst).symlink_to(src)
            except Exception as e:
                print(f"Str:{get_linenumber()}:Exept::|{e}|")
            # print(f"\n  Str:{get_linenumber()} ELSE:: str(data).split('/')[-1]: |{str(data).split('/')[-1]}|")
            # print(f"  Str:{get_linenumber()} ELSE:: Path(data).exists(): |{str(data)}|\n")
            # sys.exit()
        # if "_envcommon" in str(data):
        #     sys.exit()

    print(f"  Str:{get_linenumber()} Папка для источника файлов: |{module_dir}|{module_path}")
    # sys.exit()()
    if 'vapps' in module_path:
        src_dir = str(module_path).split('/')[-1]
        module_dir = str(module_path).split('/')[-1]
        # terragrunt/src/networking/networks
        src_path = f'{path_to_source_files}/app/{module_dir}'
        print(f"  Str:{get_linenumber()} ELSE:: Папка для источника файлов: |src_path|{src_path}")
        # sys.exit()()
        print(f"  Str:{get_linenumber()} ELSE:: Папка для источника файлов: |src_dir|{src_dir}")
        # sys.exit()

    if not 'networks' in module_path and not 'vapps' in module_path and not 'edges' in module_path:
        src_dir = str(module_path).split('/')[-1]
        src_path = f'{path_to_source_files}/app/{module_dir}/{src_dir}'
        print(f"  Str:{get_linenumber()} IF:: Папка для источника файлов: |src_path|{src_path}")
        # sys.exit()()
        print(f"  Str:{get_linenumber()} IF:: Папка для источника файлов: |src_dir|{src_dir}")
        # sys.exit()()
    else:
        src_dir = str(module_path).split('/')[-1]
        module_dir = str(module_path).split('/')[-1]
        # terragrunt/src/networking/networks
        src_path = f'{path_to_source_files}/networking/{module_dir}'
        print(f"  Str:{get_linenumber()} ELSE:: Папка для источника файлов: |src_path|{src_path}")
        # sys.exit()()
        print(f"  Str:{get_linenumber()} ELSE:: Папка для источника файлов: |src_dir|{src_dir}")
        # sys.exit()()

    print(f"  Str:{get_linenumber()} Файлы в папке источника: |{list(Path(src_path).rglob('*.*'))}|")
    # sys.exit()()
    """ Копируем файлы из источника проекта ТФ """
    for data in Path(src_path).rglob('*.*'):
        print(f"  Str:{get_linenumber()}:: Путь до файла data: |{data}|")
        src = Path(data)
        print(f"\n  Str:{get_linenumber()}:IF:: Путь до src: |{src}|")
        """ Если встречаем файл output.tf - то копируем его с новым именем output_override.tf,
        добавляя в него sensitive = true """
        if "output.tf" in str(src):
            print(f"   Str:{get_linenumber()}:IF:: Путь до output.tf: |{src}|")
            # dst = Path(f"{module_path}/{str(data).split('/')[-1]}")
            dst = Path(f"{module_path}/output_override.tf")
            with open(f"{src}", "r") as read_file:
                """ Добавляем в содерджимое файла sensitive = true """
                filedata = read_file.read()
                filedata = filedata.replace('}', '  sensitive = true\n}')
                print(f"\n    Str:{get_linenumber()}:Try:: Содержимое файла: |"
                      f"{json.dumps(filedata, indent=2, ensure_ascii=True)}|\n")
            with open(f"{dst}", "w") as write_file:
                write_file.write(filedata)
            # print(f"  Str:{get_linenumber()}:Try:: Путь до dst: |{dst}|\n")
            # try:
            #     dst.write_text(src.read_text()) #for text files
            # except Exception as e:
            #     print(f"Str:{get_linenumber()}:Exept::|{e}|")


def get_keys_from_hash_module(__hash_module, __directory, __module=None):
    """
     Функция для создания стейт-файлов терраформа.
     На вход функции подается массив значений, где ключ - наименование модуля, а значения его - наименования ресурсов,
     входящих в данный модуль.
     В результате действия данной функции создаются папки с именами модулей и стейт-файлы с именами ресурсов.
     Из функции возвращается список файл-стейтов модулей.

     Для того что бы создать файл стейта для модуля необходимо:
     1. получить содержимое файл стейта ресурса - data = json.load(read_file)
     2. создать болванку файла, кдплив из него ненужное - data['resources'] = []
     3. из файлов стейта ресурсов получить описание ресурса - data_resource = data['resources'][0]
     4. в болванку файл стейта в ключ data['resources'] добавить описание ресурса - data_resource
     5. в итоге записать получившийся файл стейт в директорию с описанием ресурсов модуля
     7. последный этап - добавить стейт в backend модуля
     6. данную операцию необходимо произвести с каждым модулем из массива _dict_state, получая его имя по ключу
     а ресурсы в него входящие - будут являтся значением этого ключа

    :param __module:
    :param __directory:
    :param __hash_module:
    :return:
    """

    """ Создаем список для хранения стейт-файлов модулей """
    _list_state = []
    """ Получаем кортеж(ключ, значение) из массива(dict(__hash_module)) """
    for _count, item in enumerate(__hash_module.items()):
        """ Пропускаем пустую итерацию, без модулей """
        if item == '':
            continue
        # Str:226 item[1] |['module.astra_app.data.vcd_vapp.vapp_name_qa', 'module.astra_app.vcd_vapp_vm.p01ecprepapp']|
        """ Добавляем фильтр по модулям """
        if __module in item[1][0]:
            print(f"\nStr:{get_linenumber()} item[1] |{item[1]}|")
        else:
            continue

        # """ Ограничиваем работу скрипта """
        # if _count >= 1:
        #     break
        # item — это кортеж (ключ, значение)
        # print(f"Str:{get_linenumber()}::{_count} |{type(item)}")
        # print(f"Str:{get_linenumber()}::{_count} |{list(map(str, item))}")
        """ Создаем массив для удобного представления и получения значений имени модуля и списком имён ресурсов """
        _dict_state = {item[0]: item[1]}
        # print(f"Str:{get_linenumber()}: json.dumps(_dict_state)|"
        #       f"{json.dumps(_dict_state, indent=2, ensure_ascii=True)}|")

        """ Создаем вспомогательный массив __dict_state для формирования болванки стейт-файла """
        __dict_state = {}
        """ Получаем из списка значений каждое значение, которое является списком ресурсов данного модуля """
        for __count, _item in enumerate(item[1]):
            # print(f"\n  Str:{get_linenumber()}::{__count} |{_item}")

            """ Имя файла с абсолютным путем - это имя ресурса и часть файла, полученная с помощью функции glob,
            где _tfdir - папка с файлами, а item - это кортеж, в котором первый элемент это имя модуля.
            В итоге получаем список файлов модуля с абсолютным путем """
            # __tfstate_resource = glob.glob(f"{_tfdir}/{_item}*.tfstate")
            __tfstate_resource = f"{_tfdir}/{_item}.tfstate"
            # print(f"  Str:{get_linenumber()}::{_count} |{__tfstate_resource}\n") ; #         sys.exit()

            """ Создаем болванку стейт-файла, для этого открываем по очереди все файлы модуля """
            with open(f"{__tfstate_resource}", "r") as read_file:
                """ Добавляем в список стейтов имя ресурса """
                data = json.load(read_file)
                """ и извлекаем из него содержимое ключа resources и помещаем его в значение ключа модуля из массива
                __dict_state """
                data_resource = data['resources'][0]
                """ все остальное будет болванкой для создания стейта со списко ресурсов модуля, в котором находится
                данный ресурс """
                data['resources'] = []
                """ Если первый проход, то применяем болванку как массив модуля __dict_state и добавляем в ключ
                __dict_state['resources'] описание ресурса  """
                if __count == 0:
                    __dict_state = data
                    __dict_state['resources'].append(data_resource)
                else:
                    """ Иначе добавляем в ключ __dict_state['resources'] описание ресурса  """
                    __dict_state['resources'].append(data_resource)

        """ Из первого имени ресурса(item[1][0]) получаем """
        module_list = item[1][0].split(".", maxsplit=-1)
        """ вторую часть имени, которая является относительно корня проекта путем до хранения файлов модуля
        эта папка состоит из одной либо несколько папок, разделителем является знак подчеркивания """
        # module_directory = module_list[1].split("_")
        module_directory = '/'.join(module_list[1].split("_"))
        """ Абсолютный путь до файла состоит из имени директории(directory), папки для хранения всех модулей(/app) и
        папки для хранения файлов модулей и относительным путем конкретного модуля('/'.join(module_directory)) """
        # abs_path = f"{__directory}/app/{'/'.join(module_directory)}"
        abs_path = f"{__directory}/env/{module_directory}"
        d = Path(abs_path)
        if d.is_dir():
            print(f"  Str:{get_linenumber()} abs_path |{abs_path}|")
            print(f"  Str:{get_linenumber()} module_directory |{module_directory}|")
        else:
            print(f"  Str:{get_linenumber()} abs_path |{abs_path}|")
            print(f"  Str:{get_linenumber()} module_directory |{module_directory}|")

        """ Создаем папку с именем модуля для записи стейт-файлов в папке с проектом ТФ """
        module_path = f"{_tfdir}/{module_directory}"

        """ Изменяем папку для создаваемых стейт-файлов на папку ,расположенную в проекте ТГ """
        """ ВНИМАНИЕ!!!!! ВНИМАНИЕ!!!!! ВНИМАНИЕ!!!!! ВНИМАНИЕ!!!!! ВНИМАНИЕ!!!!! """
        """ ЗАМЕНА ПУТИ МЕНЯЕТ ПУТЬ ДО СОЗДАВАЕМЫХ ФАЙЛОВ ВНЕ ДИРЕКТОРИИ ПРОЕКТА
         ИСПОЛЬЗУЕТСЯ ДЛЯ СОЗДАНИЯ ФАЙЛОВ ПРЯМО В СУЩЕСТВУЮЩИЙ ПРОЕКТ TERRAGRUNT'а """
        # module_path = abs_path
        print(f"  Str:{get_linenumber()} module_path |{module_path}|\n")

        p = Path(module_path)
        p.mkdir(parents=True, exist_ok=True)
        file_path = f"{module_path}/{item[0]}.tfstate"
        if p.is_dir():
            """ Записываем стейт-файл из массива __dict_state """
            with open(file_path, "w") as write_file:
                json.dump(__dict_state, write_file, indent=2, ensure_ascii=True)
        else:
            print(f"  Str:{get_linenumber()}:: Директория {p} не создана!!!")

        # print(f"\n Str:{get_linenumber()}::{_count}||_dict_state "
        #       f"|{json.dumps(__dict_state, indent=2, ensure_ascii=True)}\n###########################\n")
        _list_state.append(__dict_state)
        create_related_files(module_path, source_path)

    # print(f"  Str:{get_linenumber()}: json.dumps(_dict_state)\n|"
    #       f"{json.dumps(dict_state, indent=2, ensure_ascii=True)}|")

    # with open(f"{_tfdir}/data_file.json", "w") as write_file:
    #     json.dump(_list_state, write_file, indent=2, ensure_ascii=True)

    return _list_state


def extract_resources_and_add_to_state_file(__tfdir, _tfstate, _directory_tg, __module=None):
    """
    Функция для создания стейт файлов модулей.
    На вход функции подается путь до папки с файлом где будут создаваться стейт-файлы ресурсов
    и путь до общего стейт-файла.
    Из функции возвращается список стейт-файлов, оформелнных как массивы с описанием модулей.

    В функции осуществляется проверка существоания стейт-файлов ресурсов и при наличии их создаются стейт-файлы
    описания модулей.
    В ней описаны ресурсы модулей, которые создаются из списка модулей и словаря ресурсов __hash_module,
    получаемого из этой же функции путем запуска функции extracting_list_modules.
    в этом случае находим файл с именем module.astra_auth.data.vcd_vapp.tfstate, из которого извлекаем описание ресурса.

    :param __module:
    :param _directory_tg:
    :param __tfdir:
    :param _tfstate:
    :return:
    """
    my_tfstate = [f for f in glob.glob(f"{__tfdir}/*.tfstate")]
    # print(f"Str:{get_linenumber()}| type(my_tfstate): |{type(my_tfstate)}|") ; sys.exit()
    if my_tfstate:
        """ Возвращаем ответ о существовании файлов """
        """ Сортируем список и убираем путь до файла, оставляя только имена файлов """

        """ Для формирования массива ресурсов находим их с помощью функции extracting_list_modules().
        В функции так же создаются стейт-файлы модулей """
        __arguments = ["list", "-state=" + _tfstate]
        return_code, stdout, stderr = t.state_cmd(*__arguments)
        _stdout = ",".join(stdout)
        _stdout = stdout.split('\n')
        __list_module, __list_resource, __hash_module = extracting_list_modules(_stdout)
        # print(f"\n Str:{get_linenumber()}:\n", json.dumps(__hash_module, indent=2, ensure_ascii=True)); sys.exit()

        hash_state = get_keys_from_hash_module(__hash_module, _directory_tg, __module)
    else:
        print(f"Str:{get_linenumber()}| my_tfstate: |{my_tfstate}|")
        return "В папке нет файлов от предыдущей операции terraform state mv".split(' ')
    return hash_state


"""
# . Созданный файл стейта($tfstate), в котором перечисляем все ресурсы одного модуля и отправляем его в backend,
# для чего переходим в папку этого модуля и выполняем команду: terragrunt push $tfstate
#
#
#
#
"""
"""
 Получаем вывод команды terrafrom state list, с помощью созданного экземпляра класса Terrafrom в переменную stdout,
 так же получаем выводы кода операции(return_code) и ошибок(stderr)
"""
"""
arguments = ["list", "-state=" + _tfstate]
return_code, stdout, stderr = t.state_cmd(*arguments)
_stdout = ",".join(stdout)
_stdout = stdout.split('\n')
__list_module, __list_resource, __hash_module = extracting_list_modules(_stdout)
# print(f"Str:{get_linenumber()}:\n"+"\n".join(list_resource))
print(f"Str:{get_linenumber()}: {len(__list_module)}")
print(f"\n Str:{get_linenumber()}:\n", '\n'.join([str(x) for x in __list_module]))
print(f"\n Str:{get_linenumber()}:\n", '\n'.join([str(x) for x in __list_resource]))
print(f"\n Str:{get_linenumber()}:\n", json.dumps(__hash_module, indent=2, ensure_ascii=True))
"""


def run():
    """
    Данная функция формирует запрос на создание и внесение изменений в текущий скрипт

    :return:
    """
    # pass
    """ Получаем вывод команды terrafrom state list, с помощью созданного экземпляра класса Terrafrom
     в переменную stdout, так же получаем выводы кода операции(return_code) и ошибок(stderr) """
    _arguments = ["list", "-state=" + _tfstate]
    return_code, stdout, stderr = t.state_cmd(*_arguments)
    # ##_stdout = ",".join(stdout)

    _stdout = stdout.split('\n')
    _list_module = move_state_list_to_map(_stdout, tfst_tfstate)
    print('\n'.join(_list_module))

    """ Указываем имя модуля, который будем обрабатывать """
    __module = 'qa_'
    __module = 'release'
    __module = 'infra'
    __module = 'devenv'
    __module = 'internal'
    __module = 'dmz'
    __module = 'rmis'
    __module = 'sqlbases'
    __module = 'template'
    __module = 'redos'
    __module = 'nsud'
    __module = 'k8s'
    __module = 'jump'
    __module = 'astra'
    __module = 'demo'
    __module = 'redos'
    __module = 'networks'
    __module = 'vapps'
    __module = 'edge'
    """ Для работы скрипта используется последнее значение,
     предыдущие значения не удалялись для понимания что уже сделано а что еще нет """

    """ Формируем файл стейт модуля из отдельных файлов ресурсов """
    state = extract_resources_and_add_to_state_file(_tfdir, _tfstate, directory_tg, __module)
    print(f"Str:{get_linenumber()}| state: |#state#| Ok!")


"""
Команды выполняются в папке с модулем
terragrunt state push module.qa_*.tfstate &&\
terragrunt state push module.release_*.tfstate &&\
terragrunt state push module.infra_*.tfstate &&\

terragrunt state  pull > `date +%d-%m-%Y_%H:%M:%S`_mystate.json &&\
terragrunt state push module.infra_*.tfstate &&\
terragrunt apply -refresh-only --auto-approve --terragrunt-log-level debug --terragrunt-debug &&\
terragrunt plan --terragrunt-log-level debug --terragrunt-debug
"""


if __name__ == '__main__':
    run()
