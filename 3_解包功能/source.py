import sys
from ctypes import *
from colorama import init, Fore
init(autoreset=True)

if sys.platform.startswith("win"):
    canDLL = windll.LoadLibrary("./ControlCAN.dll")

class VCI_INIT_CONFIG(Structure):
    _fields_ = [("AccCode", c_uint),
                ("AccMask", c_uint),
                ("Reserved", c_uint),
                ("Filter", c_ubyte),
                ("Timing0", c_ubyte),
                ("Timing1", c_ubyte),
                ("Mode", c_ubyte)]

class VCI_CAN_OBJ(Structure):
    _fields_ = [("ID", c_uint),
                ("TimeStamp", c_uint),
                ("TimeFlag", c_byte),
                ("SendType", c_byte),
                ("RemoteFlag", c_byte),
                ("ExternFlag", c_byte),
                ("DataLen", c_byte),
                ("Data", c_byte * 8),
                ("Reserved", c_byte * 3)]

VCI_CAN_OBJ_ARRAY = VCI_CAN_OBJ * 2500

VCI_USBCAN2 = 4

import time
seq_number = 0
def print_output(direction, channel, can_obj):
    global seq_number
    sys_time = time.strftime("%H:%M:%S", time.localtime())
    ms = int(time.time() % 1 * 1000)
    sys_time += f".{ms:03d}"
    timestamp = f"0x{int(time.time()):08X}"
    if can_obj.ExternFlag == 0:
        frame_type = "标准帧"
    else:
        frame_type = "扩展帧"
    if can_obj.RemoteFlag == 0:
        frame_format = "数据帧"
    else:
        frame_format = "远程帧"
    print(f"{seq_number:05} {sys_time} {timestamp} {channel} {direction} 0x{can_obj.ID:08X} {frame_type} {frame_format} 0x{can_obj.DataLen:02X} {' '.join([f'0x{byte:02X}' for byte in can_obj.Data[:can_obj.DataLen]])}")
    parse_data([byte for byte in can_obj.Data[:can_obj.DataLen]])
    seq_number += 1
def parse_data(data_bytes):
    ptc_switch_status = (data_bytes[0] >> 0) & 0x01
    ptc_fault = (data_bytes[0] >> 4) & 0x01
    ptc_severe_fault = (data_bytes[0] >> 7) & 0x01

    ptc_exit_temperature = data_bytes[1] - 40
    ptc_igbt_temperature = data_bytes[2] - 40

    ptc_high_voltage = data_bytes[3] * 4
    ptc_power = data_bytes[4] * 50

    ptc_high_voltage_exception = (data_bytes[5] >> 0) & 0x01
    ptc_high_voltage_reverse = (data_bytes[5] >> 1) & 0x01
    ptc_igbt_drive_voltage_exception = (data_bytes[5] >> 2) & 0x01
    ptc_over_temperature = (data_bytes[5] >> 3) & 0x01
    ptc_igbt_over_temperature = (data_bytes[5] >> 4) & 0x01
    ptc_over_current = (data_bytes[5] >> 5) & 0x01
    ptc_low_antifreeze_flow = (data_bytes[5] >> 6) & 0x01
    ptc_can_timeout = (data_bytes[5] >> 7) & 0x01

    ptc_heating_core_short_circuit = (data_bytes[6] >> 0) & 0x01
    ptc_igbt_puncture = (data_bytes[6] >> 4) & 0x01

    ptc_igbt_or_heating_core_open_circuit = (data_bytes[7] >> 0) & 0x01
    ptc_temperature_sensor_open_circuit = (data_bytes[7] >> 4) & 0x01
    ptc_temperature_sensor_short_circuit = (data_bytes[7] >> 5) & 0x01
    ptc_igbt_temperature_sensor_open_circuit = (data_bytes[7] >> 6) & 0x01
    ptc_igbt_temperature_sensor_short_circuit = (data_bytes[7] >> 7) & 0x01

    print(f"{Fore.RED if ptc_switch_status == 0 else Fore.GREEN}PTC 高压异常PTC 开关状态: {'开启' if ptc_switch_status else '关闭'}")
    print(f"{Fore.RED if ptc_switch_status == 0 else Fore.GREEN}PTC 高压异常PTC 故障: {'有故障' if ptc_fault else '无故障'}")
    print(f"{Fore.RED if ptc_switch_status == 0 else Fore.GREEN}PTC 高压异常PTC 严重故障: {'有故障' if ptc_severe_fault else '无故障'}")
    print(f"{Fore.LIGHTBLUE_EX}PTC 出口温度: {ptc_exit_temperature}℃")
    print(f"{Fore.LIGHTBLUE_EX}PTC IGBT温度: {ptc_igbt_temperature}℃")
    print(f"{Fore.LIGHTBLUE_EX}PTC 高压值: {ptc_high_voltage}V")
    print(f"{Fore.LIGHTBLUE_EX}PTC 功率值: {ptc_power}W")

    print(f"{Fore.RED if ptc_switch_status == 0 else Fore.GREEN}PTC 高压异常: {'有异常' if ptc_high_voltage_exception else '无异常'}")
    print(f"{Fore.RED if ptc_switch_status == 0 else Fore.GREEN}PTC 高压异常PTC 高压接反: {'接反了' if ptc_high_voltage_reverse else '没接反'}")
    print(f"{Fore.RED if ptc_switch_status == 0 else Fore.GREEN}PTC 高压异常PTC IGBT驱动电压异常: {'有异常' if ptc_igbt_drive_voltage_exception else '无异常'}")
    print(f"{Fore.RED if ptc_switch_status == 0 else Fore.GREEN}PTC 高压异常PTC 超温: {'超温了' if ptc_over_temperature else '没超温'}")
    print(f"{Fore.RED if ptc_switch_status == 0 else Fore.GREEN}PTC 高压异常PTC IGBT超温: {'超温了' if ptc_igbt_over_temperature else '没超温'}")
    print(f"{Fore.RED if ptc_switch_status == 0 else Fore.GREEN}PTC 高压异常PTC 过流: {'过流了' if ptc_over_current else '没过流'}")
    print(f"{Fore.RED if ptc_switch_status == 0 else Fore.GREEN}PTC 高压异常PTC 防冻液流量低: {'防冻液流量低' if ptc_low_antifreeze_flow else '流量正常'}")
    print(f"{Fore.RED if ptc_switch_status == 0 else Fore.GREEN}PTC 高压异常PTC CAN超时: {'超时了' if ptc_can_timeout else '没超时'}")
    print(f"{Fore.RED if ptc_switch_status == 0 else Fore.GREEN}PTC 高压异常PTC 加热芯短路: {'短路了' if ptc_heating_core_short_circuit else '没短路'}")
    print(f"{Fore.RED if ptc_switch_status == 0 else Fore.GREEN}PTC 高压异常PTC IGBT击穿: {'击穿了' if ptc_igbt_puncture else '没击穿'}")
    print(f"{Fore.RED if ptc_switch_status == 0 else Fore.GREEN}PTC 高压异常PTC IGBT或加热芯断路: {'断路了' if ptc_igbt_or_heating_core_open_circuit else '没断路'}")
    print(f"{Fore.RED if ptc_switch_status == 0 else Fore.GREEN}PTC 高压异常PTC 温度传感器断路: {'断路了' if ptc_temperature_sensor_open_circuit else '没断路'}")
    print(f"{Fore.RED if ptc_switch_status == 0 else Fore.GREEN}PTC 高压异常PTC 温度传感器短路: {'短路了' if ptc_temperature_sensor_short_circuit else '没短路'}")
    print(f"{Fore.RED if ptc_switch_status == 0 else Fore.GREEN}PTC 高压异常PTC IGBT温度传感器断路: {'断路了' if ptc_igbt_temperature_sensor_open_circuit else '没断路'}")
    print(f"{Fore.RED if ptc_switch_status == 0 else Fore.GREEN}PTC 高压异常PTC IGBT温度传感器短路: {'短路了' if ptc_igbt_temperature_sensor_short_circuit else '没短路'}")

ret = canDLL.VCI_OpenDevice(VCI_USBCAN2, 0, 0)
if ret != 1:
    raise Exception("Failed to open device")

vci_config = VCI_INIT_CONFIG()
vci_config.AccCode = 0x00000000
vci_config.AccMask = 0xFFFFFFFF
vci_config.Filter = 1
vci_config.Timing0 = 0x00
vci_config.Timing1 = 0x1C
vci_config.Mode = 0

ret = canDLL.VCI_InitCAN(VCI_USBCAN2, 0, 0, byref(vci_config))
if ret != 1:
    canDLL.VCI_CloseDevice(VCI_USBCAN2, 0)
    raise Exception("Failed to initialize CAN on channel 1")

ret = canDLL.VCI_StartCAN(VCI_USBCAN2, 0, 0)
if ret != 1:
    canDLL.VCI_CloseDevice(VCI_USBCAN2, 0)
    raise Exception("Failed to start CAN on channel 1")

rx_vci_can_obj_array = VCI_CAN_OBJ_ARRAY()

while True:
    try:
        read_count = canDLL.VCI_Receive(VCI_USBCAN2, 0, 0, byref(rx_vci_can_obj_array), 2500, 100)

        if read_count > 0:
            for i in range(read_count):
                print_output("接收", "ch1", rx_vci_can_obj_array[i])

        time.sleep(0.1)

    except KeyboardInterrupt:
        ret = canDLL.VCI_CloseDevice(VCI_USBCAN2, 0)
        if ret != 1:
            print(Fore.RED + "Failed to close device")
        else:
            print(Fore.GREEN + "Device closed successfully")
        break
