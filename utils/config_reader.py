# -*- coding:utf-8 -*-

from configparser import ConfigParser
import os


class ConfigReader:

    conf = ConfigParser()
    conf_path = os.path.dirname(os.path.split(os.path.realpath(__file__))[0])
    conf.read(conf_path + '/conf.ini', encoding="utf-8-sig")

    @classmethod
    def read_conf(cls):
        cls.conf.read(cls.conf_path + '/conf.ini', encoding="utf-8-sig")

    @classmethod
    def get_member_room_number(cls, name):
        return cls.conf.get('juju_room', name)

    @classmethod
    def get_qq_number(cls, name):
        return cls.conf.get('qq_conf', name)

    @classmethod
    def get_group_number(cls):
        return cls.conf.get('qq_conf', 'group_number')

    @classmethod
    def get_test_group_number(cls):
        return cls.conf.get('qq_conf', 'test_group_number')

    @classmethod
    def get_all_member_room_id_list(cls):
        member_room_id_list = []
        for item in cls.conf.items('juju_room'):
            member_room_id_list.append(item)
        return member_room_id_list

    @classmethod
    def get_living_member_id_list(cls):
        living_member_id_list = []
        for item in cls.conf.items('live'):
            living_member_id_list.append(item[1])
        return living_member_id_list

    @classmethod
    def get_property(cls, root, name):
        return cls.conf.get(root, name)


if __name__ == '__main__':
    ConfigReader.read_conf()
    se_list = ConfigReader.conf.sections()
    print(se_list)
    print(ConfigReader.get_qq_number('member_room_msg_groups'))
