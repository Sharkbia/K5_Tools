import dataclasses
import serial_utils
import serial.tools.list_ports
from logger import log
import tkinter as tk
from tkinter import messagebox, ttk
import resources.font
# if sys.version_info < (3, 10):
#     import importlib_resources
# else:
#     import importlib.resources as importlib_resources


@dataclasses.dataclass
class SerialPortCheckResult:
    status: bool
    message: str
    extra_eeprom: bool


def get_all_serial_port():
    ports = serial.tools.list_ports.comports()
    ports = [port.device for port in ports]
    log('可用串口: ' + str(ports))
    return ports


def serial_port_combo_postcommand(combo: ttk.Combobox):
    combo['values'] = get_all_serial_port()


def check_serial_port(serial_port: serial.Serial) -> SerialPortCheckResult:
    try:
        version = serial_utils.sayhello(serial_port)
        extra_eeprom = version.endswith('K')
        msg = '串口连接成功！\n版本号: ' + version + '\nEEPROM大小: ' + ('已扩容 128KiB+' if extra_eeprom else '8KiB')
        log(msg)
        return SerialPortCheckResult(True, msg, extra_eeprom)
    except Exception as e:
        msg = '串口连接失败！<-' + str(e)
        log(msg)
        return SerialPortCheckResult(False, msg, False)


def serial_port_combo_callback(event, serial_port: str, status_label: tk.Label):
    status_label['text'] = '当前操作: 检查串口连接'
    with serial.Serial(serial_port, 38400, timeout=2) as serial_port:
        serial_check = check_serial_port(serial_port)
        if serial_check.status:
            messagebox.showinfo('提示', serial_check.message)
        else:
            messagebox.showerror('错误', serial_check.message)
    status_label['text'] = '当前操作: 无'


def clean_eeprom(serial_port: str, window: tk.Tk, progress: ttk.Progressbar, status_label: tk.Label):
    log('开始清空EEPROM流程')
    log('选择的串口: ' + serial_port)
    status_label['text'] = '当前操作: 清空EEPROM'
    if len(serial_port) == 0:
        log('没有选择串口！')
        messagebox.showerror('错误', '没有选择串口！')
        return

    if not messagebox.askokcancel('警告', '该操作会清空EEPROM内所有数据(包括设置、信道、校准等)\n确定要清空EEPROM吗？'):
        return

    with serial.Serial(serial_port, 38400, timeout=2) as serial_port:
        serial_check = check_serial_port(serial_port)
        if not serial_check.status:
            messagebox.showerror('错误', serial_check.message)
            return

        if not serial_check.extra_eeprom:
            log('非萝狮虎(losehu) 扩容固件，部分扇区可能无法被清除')
            messagebox.showinfo('未扩容固件', '未使用 萝狮虎(losehu) 扩容固件, 部分扇区可能无法被清除')
            for i in range(0, 64):
                serial_utils.write_eeprom(serial_port, i * 128, b'\xff' * 128)
                percent_float = (i + 1) / 64 * 100
                percent = int(percent_float)
                progress['value'] = percent
                log(f'进度: {percent_float:.1f}%, offset={hex(i * 128)}')
                window.update()
        else:
            total_steps = 512 * 2
            current_step = 0
            for offset in range(0, 2):
                for n in range(0, 512):
                    current_step += 1
                    serial_utils.write_extra_eeprom(serial_port, offset, n * 128, b'\xff' * 128)
                    percent_float = (current_step / total_steps) * 100
                    percent = int(percent_float)
                    progress['value'] = percent
                    log(f'进度: {percent_float:.1f}%, offset={hex(offset)}, extra={hex(n * 128)}')
                    window.update()
        progress['value'] = 0
        window.update()
        serial_utils.reset_radio(serial_port)
    log('清空EEPROM成功！')
    status_label['text'] = '当前操作: 无'
    messagebox.showinfo('提示', '清空EEPROM成功！')


def write_font(serial_port: str, window: tk.Tk, progress: ttk.Progressbar, status_label: tk.Label,
               new_font: bool = True):
    log('开始写入字库流程')
    font_version = '新' if new_font else '旧'
    log(f'字库版本: {font_version}')
    log('选择的串口: ' + serial_port)
    status_label['text'] = f'当前操作: 写入字库 ({font_version})'
    if len(serial_port) == 0:
        log('没有选择串口！')
        messagebox.showerror('错误', '没有选择串口！')
        return

    with serial.Serial(serial_port, 38400, timeout=2) as serial_port:
        serial_check = check_serial_port(serial_port)
        if not serial_check.status:
            messagebox.showerror('错误', serial_check.message)
            return

        if not serial_check.extra_eeprom:
            log('非萝狮虎(losehu) 扩容固件，无法写入字库！')
            messagebox.showerror('未扩容固件', '未使用 萝狮虎(losehu) 扩容固件，无法写入字库！')
            return
        else:
            # resource_dir = str(importlib_resources.files('resources'))
            # if resource_dir.startswith('MultiplexedPath'):
            #     resource_dir = resource_dir[17:-2]
            # font_file = str(os.path.join(resource_dir, 'font_old.bin'))
            # with open(font_file, 'rb') as f:
            #     data = f.read()
            # if len(data) != 0x1C320:
            #     log('字库文件大小错误！')
            #     messagebox.showerror('错误', '字库文件大小错误！')
            #     return
            # 直接使用字库数据 不再从文件读取
            if new_font:
                font_data = resources.font.new_data
            else:
                font_data = resources.font.old_data
            font_len = len(font_data)
            total_page = font_len // 128
            addr = 0x2000
            current_step = 0
            offset = 0
            while addr < 0x2000 + font_len:
                write_data = bytes(font_data[:128])
                font_data = font_data[128:]
                if addr - offset * 0x10000 >= 0x10000:
                    offset += 1
                serial_utils.write_extra_eeprom(serial_port, offset, addr - offset * 0x10000, write_data)
                addr += 128
                current_step += 1
                percent_float = (current_step / total_page) * 100
                percent = int(percent_float)
                progress['value'] = percent
                log(f'进度: {percent_float:.1f}%, addr={hex(addr)}')
                window.update()
        progress['value'] = 0
        window.update()
        serial_utils.reset_radio(serial_port)
    log('写入字库成功！')
    status_label['text'] = '当前操作: 无'
    messagebox.showinfo('提示', '写入字库成功！')
