from ctypes import *

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

# 初始化 CAN2 通道
vci_initconfig = VCI_INIT_CONFIG(0x80000008, 0xFFFFFFFF, 0, 0, 0x03, 0x1C, 0)
ret = canDLL.VCI_InitCAN(VCI_USBCAN2, 0, 1, byref(vci_initconfig))
if ret == STATUS_OK:
    print('调用 VCI_InitCAN2 成功\r\n')
if ret != STATUS_OK:
    print('调用 VCI_InitCAN2 出错\r\n')

ret = canDLL.VCI_StartCAN(VCI_USBCAN2, 0, 1)
if ret == STATUS_OK:
    print('调用 VCI_StartCAN2 成功\r\n')
if ret != STATUS_OK:
    print('调用 VCI_StartCAN2 出错\r\n')


# ... 保留前面的代码

# 初始化 CAN1 通道
ret = canDLL.VCI_InitCAN(VCI_USBCAN2, 0, 0, byref(vci_initconfig))
if ret == STATUS_OK:
    print('调用 VCI_InitCAN1成功\r\n')
if ret != STATUS_OK:
    print('调用 VCI_InitCAN1出错\r\n')

ret = canDLL.VCI_StartCAN(VCI_USBCAN2, 0, 0)
if ret == STATUS_OK:
    print('调用 VCI_StartCAN1成功\r\n')
if ret != STATUS_OK:
    print('调用 VCI_StartCAN1出错\r\n')

# 通道1发送数据 [1, 2, 3, 4, 5, 6, 7, 8]
ubyte_array = c_ubyte * 8
a = ubyte_array(1, 2, 3, 4, 5, 6, 7, 8)  # 更改为 [1, 2, 3, 4, 5, 6, 7, 8]
ubyte_3array = c_ubyte * 3
b = ubyte_3array(0, 0, 0)
vci_can_obj = VCI_CAN_OBJ(0x1, 0, 0, 1, 0, 0, 8, a, b)

ret = canDLL.VCI_Transmit(VCI_USBCAN2, 0, 0, byref(vci_can_obj), 1)
if ret == STATUS_OK:
    print('CAN1通道发送成功\r\n')
if ret != STATUS_OK:
    print('CAN1通道发送失败\r\n')

# ... 保留后面的代码


# 通道2接收数据
import ctypes
class VCI_CAN_OBJ_ARRAY(Structure):
    _fields_ = [('SIZE', ctypes.c_uint16), ('STRUCT_ARRAY', ctypes.POINTER(VCI_CAN_OBJ))]

    def __init__(self,num_of_structs):
        self.STRUCT_ARRAY = ctypes.cast((VCI_CAN_OBJ * num_of_structs)(),ctypes.POINTER(VCI_CAN_OBJ))
        self.SIZE = num_of_structs
        self.ADDR = self.STRUCT_ARRAY[0]

rx_vci_can_obj = VCI_CAN_OBJ_ARRAY(2500)

ret = canDLL.VCI_Receive(VCI_USBCAN2, 0, 1, byref(rx_vci_can_obj.ADDR), 2500, 0)
while ret <= 0:
    ret = canDLL.VCI_Receive(VCI_USBCAN2, 0, 1, byref(rx_vci_can_obj.ADDR), 2500, 0)
if ret > 0:
    print('CAN2通道接收成功\r\n')
    print('ID：')
    print(rx_vci_can_obj.ADDR.ID)
    print('DataLen：')
    print(rx_vci_can_obj.ADDR.DataLen)
    print('Data：')
    print(list(rx_vci_can_obj.ADDR.Data))

# 关闭设备
canDLL.VCI_CloseDevice(VCI_USBCAN2, 0)

