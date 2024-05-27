from enum import Enum

FIRMWARE_VERSION_LIST = ['萝狮虎', '萝狮虎扩容', '其他']
EEPROM_SIZE = ['8KiB (原厂)', '128KiB (1M)', '256KiB (2M)', '384KiB (3M)', '512KiB (4M)']


class FontType(Enum):
    GB2312_COMPRESSED = '压缩GB2312'
    GB2312_UNCOMPRESSED = '未压缩GB2312'
    LOSEHU_FONT = '萝狮虎字库'


class LanguageType(Enum):
    SIMPLIFIED_CHINESE = '简体中文'
    ENGLISH = 'English'

    @staticmethod
    def find_value(value: str) -> 'LanguageType':
        for item in LanguageType:
            if item.value == value:
                return item
        return LanguageType.SIMPLIFIED_CHINESE

    @staticmethod
    def find_name(name: str) -> 'LanguageType':
        for item in LanguageType:
            if item.name == name:
                return item
        return LanguageType.SIMPLIFIED_CHINESE

    @staticmethod
    def value_list():
        return list(map(lambda i: i.value, LanguageType))


custom_button_functions_zh = [
    '------请选择------',
    '清空EEPROM',
    '自动写入字库',
    '读取校准参数',
    '写入校准参数',
    '读取配置参数',
    '写入配置参数',
    '写入字库配置',
    '写入亚音参数',
    '写入压缩字库',
    '写入全量字库',
    '写入字库 (旧)',
    '写入拼音表（旧）',
    '写入拼音表（新）',
    '备份EEPROM',
    '恢复EEPROM',
    '重启设备',
    '测试',
    '写入补丁'
]

custom_button_functions_en = [
    '---Please select---',
    'Clear EEPROM',
    'Auto write font',
    'Read calibration',
    'Write calibration',
    'Read config',
    'Write config',
    'Write font config',
    'Write tone config',
    'Write comp font',
    'Write full font',
    'Write old font',
    'Write old index',
    'Write new index',
    'Backup EEPROM',
    'Restore EEPROM',
    'Reboot device'
]

