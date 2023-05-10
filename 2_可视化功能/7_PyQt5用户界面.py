from ctypes import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer

VCI_USBCAN2 = 4
STATUS_OK = 1

class VCI_INIT_CONFIG(Structure):
    _fields_ = [("AccCode", c_uint),
                ("AccMask", c_uint),
                ("Reserved", c_uint),
                ("Filter", c_ubyte),
                ("Timing0", c_ubyte),
                ("Timing1", c_ubyte),
                ("Mode", c_ubyte)
                ]

class VCI_CAN_OBJ(Structure):
    _fields_ = [("ID", c_uint),
                ("TimeStamp", c_uint),
                ("TimeFlag", c_ubyte),
                ("SendType", c_ubyte),
                ("RemoteFlag", c_ubyte),
                ("ExternFlag", c_ubyte),
                ("DataLen", c_ubyte),
                ("Data", c_ubyte*8),
                ("Reserved", c_ubyte*3)
                ]

CanDLLName = './ControlCAN.dll'
canDLL = windll.LoadLibrary('./ControlCAN.dll')

print(CanDLLName)

ret = canDLL.VCI_OpenDevice(VCI_USBCAN2, 0, 0)
if ret == STATUS_OK:
    print('调用 VCI_OpenDevice成功\r\n')
if ret != STATUS_OK:
    print('调用 VCI_OpenDevice出错\r\n')

# 根据提供的参数初始化 CAN1 通道
vci_initconfig = VCI_INIT_CONFIG(0x80000000, 0xFFFFFFFF, 0, 0, 0x00, 0x1C, 0)
ret = canDLL.VCI_InitCAN(VCI_USBCAN2, 0, 0, byref(vci_initconfig))
if ret == STATUS_OK:
    print('调用 VCI_InitCAN1 成功\r\n')
if ret != STATUS_OK:
    print('调用 VCI_InitCAN1 出错\r\n')

ret = canDLL.VCI_StartCAN(VCI_USBCAN2, 0, 0)
if ret == STATUS_OK:
    print('调用 VCI_StartCAN1 成功\r\n')
if ret != STATUS_OK:
    print('调用 VCI_StartCAN1 出错\r\n')

# ... 保留前面的代码

# 通道1接收数据
# ... 保留前面的代码

# 通道1接收数据
import ctypes

class VCI_CAN_OBJ_ARRAY(Structure):
    _fields_ = [('SIZE', ctypes.c_uint16), ('STRUCT_ARRAY', ctypes.POINTER(VCI_CAN_OBJ))]

    def __init__(self,num_of_structs):
        self.STRUCT_ARRAY = ctypes.cast((VCI_CAN_OBJ * num_of_structs)(),ctypes.POINTER(VCI_CAN_OBJ))
        self.SIZE = num_of_structs
        self.ADDR = self.STRUCT_ARRAY[0]

import time
import json
from ctypes import *
from datetime import datetime

# ... 保留前面的代码

# 输出 JSON 格式的数据
def output_json(index, sys_time, time_flag, channel, direction, frame_id, frame_type, frame_format, data_len, data):
    data_dict = {
        "序号": index,
        "系统时间": sys_time,
        "时间标识": time_flag,
        "CAN通道": channel,
        "传输方向": direction,
        "ID号": frame_id,
        "帧类型": frame_type,
        "帧格式": frame_format,
        "长度": data_len,
        "数据": data
    }
    return json.dumps(data_dict, ensure_ascii=False)

# 创建一个新的函数来更新GUI中的文本
def update_gui_text(json_output):
    text_widget.append(json_output)

# 创建GUI
app = QApplication([])
main_window = QMainWindow()

central_widget = QWidget()
main_window.setCentralWidget(central_widget)

layout = QVBoxLayout(central_widget)

text_widget = QTextEdit()
layout.addWidget(text_widget)

main_window.setWindowTitle("CAN数据显示")
main_window.show()

# 设置一个定时器来更新数据
timer = QTimer()
timer.timeout.connect(lambda: update_gui_text(json_output))
timer.start(100)  # 每100毫秒更新一次

# 更新循环
index = 0
while True:
    rx_vci_can_obj = VCI_CAN_OBJ_ARRAY(2500)
    ret = canDLL.VCI_Receive(VCI_USBCAN2, 0, 0, byref(rx_vci_can_obj.ADDR), 2500, 0)

    if ret > 0:
        index += 1
        sys_time = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        time_flag = hex(rx_vci_can_obj.ADDR.TimeStamp)
        channel = "ch1"
        direction = "接收"
        frame_id = "0x{:08X}".format(rx_vci_can_obj.ADDR.ID)
        frame_type = "标准帧" if not rx_vci_can_obj.ADDR.ExternFlag else "扩展帧"
        frame_format = "数据帧" if not rx_vci_can_obj.ADDR.RemoteFlag else "远程帧"
        data_len = "0x{:X}".format(rx_vci_can_obj.ADDR.DataLen)
        data = " ".join("0x{:02X}".format(x) for x in rx_vci_can_obj.ADDR.Data)

        json_output = output_json(index, sys_time, time_flag, channel, direction, frame_id, frame_type, frame_format, data_len, data)
        update_gui_text(json_output)

    # 在Qt事件循环中处理GUI更新
    app.processEvents()

# 关闭设备
canDLL.VCI_CloseDevice(VCI_USBCAN2, 0)

