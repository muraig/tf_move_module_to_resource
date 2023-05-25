#!/usr/bin/env python

# encoding: utf-8
'''
# @Author: Andrey M.
# @Contact: <muraigtor@gmail.com>
# @Site:
# @Version: 1.0
# @License: Apache Licence
# @File: __main__.py
# @Time: 10.03.2023 10:44
# @Software: IntelliJ IDEA
Начните с этой строки, чтобы написать описания и пояснения к этому файлу.
'''


VERSION_MAJOR = 1
VERSION_MINOR = 0
VERSION_REVISION = 0


def app():
    print("dtline_tf_to_tg")
    print("Version %d.%d.%d                       " % (VERSION_MAJOR, VERSION_MINOR, VERSION_REVISION))

    # TODO: Application code here


try:
    print("Command line application Андрей Мурашев <>")
except KeyboardInterrupt:
    print("Project generation cancelled by user.")

app()
