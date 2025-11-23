# -*- coding:utf-8 -*-
import configparser
import base64
from Crypto.Cipher import AES
from Crypto import Random


class MCfg:
    """配置管理类"""
    cp = configparser.ConfigParser()
    server_host = ""
    server_port = 0
    loglevel = 10
    __key = b'quantization_123'

    def __encode(self, value):
        """AES加密"""
        iv = Random.new().read(AES.block_size)
        mycipher = AES.new(self.__key, AES.MODE_CFB, iv)
        ciptext = iv + mycipher.encrypt(value.encode())
        b64_cip_text = base64.b64encode(ciptext)
        return b64_cip_text.decode()

    def __decrypt(self, value):
        """AES解密"""
        tovalue = base64.b64decode(value)
        mydecrypt = AES.new(self.__key, AES.MODE_CFB, tovalue[:16])
        decrytext = mydecrypt.decrypt(tovalue[16:])
        return decrytext.decode()

    def get_item(self, section, item):
        """获取配置项"""
        if section not in self.cp.sections():
            raise Exception(f'配置文件缺少section: {section}')
        if item not in self.cp[section]:
            raise Exception(f'配置文件缺少item: {item} in section: {section}')
        return self.cp[section][item]

    def __init__(self, file):
        import os

        # 配置文件选择逻辑：
        # 只有在设置了 USE_LOCAL_CONFIG=true 环境变量时，才使用本地配置
        # 其他所有情况都使用默认配置文件
        use_local = os.environ.get('USE_LOCAL_CONFIG', '').lower()
        local_file = file + '.local'

        if use_local == 'true' and os.path.exists(local_file):
            config_file = local_file
            print(f'使用本地配置文件 (USE_LOCAL_CONFIG=true): {config_file}')
        else:
            config_file = file
            print(f'使用默认配置文件: {config_file}')

        self.cp.read(config_file, encoding='utf-8')

        # 读取基础配置
        try:
            self.server_host = self.get_item('Service', 'Host')
            self.server_port = int(self.get_item('Service', 'Port'))
            self.loglevel = int(self.get_item('Service', 'LogLevel'))
        except Exception as e:
            print(f'配置文件读取错误: {e}')
            raise
