from ctypes import *
from colorama import Fore, Style

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

# 通道1接收数据
import ctypes

class VCI_CAN_OBJ_ARRAY(Structure):
    _fields_ = [('SIZE', ctypes.c_uint16), ('STRUCT_ARRAY', ctypes.POINTER(VCI_CAN_OBJ))]

    def __init__(self,num_of_structs):
        self.STRUCT_ARRAY = ctypes.cast((VCI_CAN_OBJ * num_of_structs)(),ctypes.POINTER(VCI_CAN_OBJ))
        self.SIZE = num_of_structs
        self.ADDR = self.STRUCT_ARRAY[0]

import json
from ctypes import *
from datetime import datetime

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

# 用于解析和输出数据的函数
def parse_and_output_data(data):
    byte_list = [int(x, 16) for x in data.split()]

    # PTC 开关状态
    ptc_switch_status = (byte_list[0] >> 0) & 0b1
    output_color = Fore.RED if ptc_switch_status == 0 else Fore.GREEN
    print(output_color + f"PTC 开关状态: {'PTC关闭' if ptc_switch_status == 0 else 'PTC开启'}" + Style.RESET_ALL,
          end=' ')

    # PTC 故障
    ptc_fault = (byte_list[0] >> 4) & 0b1
    output_color = Fore.GREEN if ptc_fault == 0 else Fore.RED
    print(output_color + f"PTC 故障: {'无故障' if ptc_fault == 0 else '有故障'}" + Style.RESET_ALL, end=' ')

    # PTC 严重故障
    ptc_severe_fault = (byte_list[0] >> 7) & 0b1
    output_color = Fore.GREEN if ptc_severe_fault == 0 else Fore.RED
    print(output_color + f"PTC 严重故障: {'无故障' if ptc_severe_fault == 0 else '有故障'}" + Style.RESET_ALL, end=' ')

    # PTC 出口温度
    ptc_exit_temp = byte_list[1] - 40
    print(f"PTC 出口温度: {ptc_exit_temp}℃", end=' ')

    # PTC IGBT温度
    ptc_igbt_temp = byte_list[2] - 40
    print(f"PTC IGBT温度: {ptc_igbt_temp}℃", end=' ')

    # PTC 高压值
    ptc_high_voltage = byte_list[3] * 4
    print(f"PTC 高压值: {ptc_high_voltage:.2f}V", end=' ')

    # PTC 功率值
    ptc_power_value = byte_list[4] * 50
    print(f"PTC 功率值: {ptc_power_value:.2f}W", end=' ')

    # PTC 高压异常
    ptc_high_voltage_abnormal = (byte_list[5] >> 0) & 0b1
    output_color = Fore.GREEN if ptc_high_voltage_abnormal == 0 else Fore.RED
    print(output_color + f"PTC 高压异常: {'无异常' if ptc_high_voltage_abnormal == 0 else '有异常'}" + Style.RESET_ALL, end=' ')

    # PTC 高压接反
    ptc_high_voltage_reversed = (byte_list[5] >> 1) & 0b1
    output_color = Fore.GREEN if ptc_high_voltage_reversed == 0 else Fore.RED
    print(output_color + f"PTC 高压接反: {'没接反' if ptc_high_voltage_reversed == 0 else '接反了'}" + Style.RESET_ALL, end=' ')

    # PTC IGBT驱动电压异常
    ptc_igbt_drive_voltage_abnormal = (byte_list[5] >> 2) & 0b1
    output_color = Fore.GREEN if ptc_igbt_drive_voltage_abnormal == 0 else Fore.RED
    print(output_color + f"PTC IGBT驱动电压异常: {'无异常' if ptc_igbt_drive_voltage_abnormal == 0 else '有异常'}" + Style.RESET_ALL, end=' ')

    # PTC 超温
    ptc_over_temperature = (byte_list[5] >> 3) & 0b1
    output_color = Fore.GREEN if ptc_over_temperature == 0 else Fore.RED
    print(output_color + f"PTC 超温: {'没超温' if ptc_over_temperature == 0 else '超温了'}" + Style.RESET_ALL, end=' ')

    # PTC IGBT超温
    ptc_igbt_over_temperature = (byte_list[5] >> 4) & 0b1
    output_color = Fore.GREEN if ptc_igbt_over_temperature == 0 else Fore.RED
    print(output_color + f"PTC IGBT超温: {'没超温' if ptc_igbt_over_temperature == 0 else '超温了'}" + Style.RESET_ALL, end=' ')

    # PTC 过流
    ptc_over_current = (byte_list[5] >> 5) & 0b1
    output_color = Fore.GREEN if ptc_over_current == 0 else Fore.RED
    print(output_color + f"PTC 过流: {'没过流' if ptc_over_current == 0 else '过流了'}" + Style.RESET_ALL, end=' ')

    # PTC 防冻液流量低
    ptc_antifreeze_low_flow = (byte_list[5] >> 6) & 0b1
    output_color = Fore.GREEN if ptc_antifreeze_low_flow == 0 else Fore.RED
    print(output_color + f"PTC 防冻液流量低: {'流量正常' if ptc_antifreeze_low_flow == 0 else '防冻液流量低'}" + Style.RESET_ALL, end=' ')

    # PTC CAN通讯超时
    ptc_can_comm_timeout= (byte_list[5] >> 7) & 0b1
    output_color = Fore.GREEN if ptc_can_comm_timeout == 0 else Fore.RED
    print(output_color + f"PTC CAN通讯超时: {'通讯正常' if ptc_can_comm_timeout == 0 else 'CAN通讯超时'}" + Style.RESET_ALL, end=' ')

    # PTC 发热芯短路
    ptc_heating_core_short_circuit = (byte_list[6] >> 0) & 0b1
    output_color = Fore.GREEN if ptc_heating_core_short_circuit == 0 else Fore.RED
    print(output_color + f"PTC 发热芯短路: {'没短路' if ptc_heating_core_short_circuit == 0 else '短路了'}" + Style.RESET_ALL, end=' ')

    # PTC IGBT击穿
    ptc_igbt_breakdown = (byte_list[6] >> 1) & 0b1
    output_color = Fore.GREEN if ptc_igbt_breakdown == 0 else Fore.RED
    print(output_color + f"PTC IGBT击穿: {'没击穿' if ptc_igbt_breakdown == 0 else '击穿了'}" + Style.RESET_ALL, end=' ')

    # PTC IGBT或发热芯开路
    ptc_igbt_or_heating_core_open_circuit = (byte_list[6] >> 2) & 0b1
    output_color = Fore.GREEN if ptc_igbt_or_heating_core_open_circuit == 0 else Fore.RED
    print(output_color + f"PTC IGBT或发热芯开路: {'没开路' if ptc_igbt_or_heating_core_open_circuit == 0 else '开路了'}" + Style.RESET_ALL, end=' ')

    # PTC 温度传感器开路
    ptc_temp_sensor_open_circuit = (byte_list[6] >> 3) & 0b1
    output_color = Fore.GREEN if ptc_temp_sensor_open_circuit == 0 else Fore.RED
    print(output_color + f"PTC 温度传感器开路: {'没开路' if ptc_temp_sensor_open_circuit == 0 else '开路了'}" + Style.RESET_ALL, end=' ')

    # PTC 温度传感器短路
    ptc_temp_sensor_short_circuit = (byte_list[6] >> 4) & 0b1
    output_color = Fore.GREEN if ptc_temp_sensor_short_circuit == 0 else Fore.RED
    print(output_color + f"PTC 温度传感器短路: {'没短路' if ptc_temp_sensor_short_circuit == 0 else '短路了'}" + Style.RESET_ALL, end=' ')

    # PTC IGBT温度传感器开路
    ptc_igbt_temp_sensor_open_circuit = (byte_list[6] >> 5) & 0b1
    output_color = Fore.GREEN if ptc_igbt_temp_sensor_open_circuit == 0 else Fore.RED
    print(output_color + f"PTC IGBT温度传感器开路: {'没开路' if ptc_igbt_temp_sensor_open_circuit == 0 else '开路了'}" + Style.RESET_ALL, end=' ')

    # PTC IGBT温度传感器短路
    ptc_igbt_temp_sensor_short_circuit = (byte_list[6] >> 6) & 0b1
    output_color = Fore.GREEN if ptc_igbt_temp_sensor_short_circuit == 0 else Fore.RED
    print(output_color + f"PTC IGBT温度传感器短路: {'没短路' if ptc_igbt_temp_sensor_short_circuit == 0 else '短路了'}" + Style.RESET_ALL)

def parse_data_and_output_json(index, sys_time, time_flag, channel, direction, frame_id, frame_type, frame_format, data_len, data):
    json_str = output_json(index, sys_time, time_flag, channel, direction, frame_id, frame_type, frame_format, data_len, data)
    print(json_str)
    parse_and_output_data(data)

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

        json_output = parse_data_and_output_json(index, sys_time, time_flag, channel, direction, frame_id, frame_type, frame_format, data_len, data)
        print(json_output)

# 关闭设备
canDLL.VCI_CloseDevice(VCI_USBCAN2, 0)

