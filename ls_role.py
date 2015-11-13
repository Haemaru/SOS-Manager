from os.path import isfile
from utils import num_bin
from utils import bin_num
from utils import is_bit_flagged


class LSRole(object):

    @staticmethod
    def read_by_bin(bin_data):

        offset = 20
        roles_list = list()

        while offset < len(bin_data):
            role_name_len = bin_data[offset]
            offset += 1
            role_name = bin_data[
                offset:(offset + role_name_len)
            ].decode('ascii')

            offset += role_name_len

            parent_role_name_len = bin_data[offset]
            offset += 1
            parent_role_name = bin_data[
                offset:(offset + parent_role_name_len)
            ].decode('ascii')

            offset += parent_role_name_len

            attr_count = bin_num(bin_data[offset:(offset + 4)], 4)
            offset += (600 - role_name_len - parent_role_name_len - 2)

            role = LSRole(role_name, parent_role_name=parent_role_name)

            for i in range(attr_count):
                attr_data = bin_data[offset:(offset + 10)]
                offset += 10

                if attr_data[0] == 0x01:
                    role.file_roles.append(
                        LSFileRole.read_by_bin(attr_data))
                elif attr_data[0] == 0x02:
                    role.network_roles.append(
                        LSNetworkRole.read_by_bin(attr_data))
                elif attr_data[0] == 0x03:
                    role.process_roles.append(
                        LSProcessRole.read_by_bin(attr_data))
                elif attr_data[0] == 0xfe:
                    role.bind_processes.append(
                        LSBindProcess.read_by_bin(attr_data))
                elif attr_data[0] == 0xff:
                    role.bind_users.append(
                        LSBindUser.read_by_bin(attr_data))
                else:
                    pass

            roles_list.append(role)

        if len(roles_list) > 0:
            top_role = roles_list[0]
        else:
            top_role = LSRole('default')

        for child in roles_list:
            for parent in roles_list:
                if child.parent_role_name == parent.role_name:
                    child.parent_role = parent
                    parent.child_roles[child.role_name] = child
                    break

        return top_role

    def __init__(self, role_name='', parent_role=None, parent_role_name=''):
        self.role_name = role_name
        self.parent_role_name = parent_role_name

        self.child_roles = dict()
        self.parent_role = parent_role

        self.file_roles = list()
        self.network_roles = list()
        self.process_roles = list()

        self.bind_processes = list()
        self.bind_users = list()

    def write(self, f):
        role_name_len = len(self.role_name)

        f.write(num_bin(role_name_len, 1))
        f.write(self.role_name.encode('ascii'))

        if self.parent_role is None:
            parent_role_name_len = 0
            f.write(b'\x00')
        else:
            parent_role_name_len = len(self.parent_role.role_name)
            f.write(num_bin(parent_role_name_len, 1))
            f.write(self.parent_role.role_name.encode('ascii'))

        attr_count = len(self.file_roles) + \
            len(self.network_roles) + \
            len(self.process_roles) + \
            len(self.bind_processes) + \
            len(self.bind_users)
        f.write(num_bin(attr_count, 4))

        size = role_name_len + parent_role_name_len + 2 + 4

        f.write(bytearray(b'\xff' * (600 - size)))


class LSFileRole(list):

    VALUES = (
        ('INODE Number', int, 8),
        ('Read', bool, ('DENY', 'ALLOW')),
        ('Write', bool, ('DENY', 'ALLOW')),
        ('Execute', bool, ('DENY', 'ALLOW')))

    @staticmethod
    def read_by_bin(bin_data):
        return LSFileRole(
            bin_num(bin_data[1:9], 8),
            is_bit_flagged(bin_data[9], 0b100) ^ 1,
            is_bit_flagged(bin_data[9], 0b010) ^ 1,
            is_bit_flagged(bin_data[9], 0b001) ^ 1)

    def __init__(
        self,
        i_ino=0,
        u_acc_read=True,
        u_acc_write=True,
        u_acc_execute=True
    ):
        self.append(['INODE Number', i_ino])
        self.append(['u_acc_read', u_acc_read])
        self.append(['u_acc_write', u_acc_write])
        self.append(['u_acc_execute', u_acc_write])

    def write(self, f):
        f.write(b'\x01')

        u_acc = 0

        if self[1][1] is True:
            u_acc |= 0b100
        if self[2][1] is True:
            u_acc |= 0b010
        if self[3][1] is True:
            u_acc |= 0b001

        f.write(num_bin(self[0][1], 8))
        f.write(num_bin(u_acc, 1))


class LSNetworkRole(list):

    VALUES = (
        ('Port', int, 2),
        ('Open', bool, ('DENY', 'ALLOW')))

    @staticmethod
    def read_by_bin(bin_data):
        return LSNetworkRole(
            bin_num(bin_data[1:3], 2),
            is_bit_flagged(bin_data[3], 0b001))

    def __init__(self, port=0, is_allow_open=True):
        self.append(['Port', port])
        self.append(['is_allow_open', is_allow_open])

    def write(self, f):
        f.write(b'\x02')
        f.write(num_bin(self[0][1], 2))

        if self[1][1] is True:
            f.write(num_bin(0, 1))
        else:
            f.write(num_bin(1, 1))

        f.write(b'\xff' * 6)


class LSProcessRole(list):

    VALUES = (
        ('ID', int, 8),
        ('ID Type', bool, ('INODE', 'UID')),
        ('Kill', bool, ('DENY', 'ALLOW')),
        ('Trace', bool, ('DENY', 'ALLOW')),
        ('Setuid', bool, ('DENY', 'ALLOW')))

    TYPE_PID = 1
    TYPE_INODE = 0

    @staticmethod
    def read_by_bin(bin_data):
        return LSProcessRole(
            bin_num(bin_data[1:9], 8),
            is_bit_flagged(bin_data[9], 0b1000),
            is_bit_flagged(bin_data[9], 0b0100),
            is_bit_flagged(bin_data[9], 0b0010),
            is_bit_flagged(bin_data[9], 0b0001))

    def __init__(
        self,
        id_value=0,
        id_type=TYPE_PID,
        is_allow_kill=True,
        is_allow_trace=True,
        is_allow_setuid=True
    ):
        self.append(['ID', id_value])
        self.append(['id_type', id_type])
        self.append(['is_allow_kill', is_allow_kill])
        self.append(['is_allow_trace', is_allow_trace])
        self.append(['is_allow_setuid', is_allow_setuid])

    def write(self, f):
        f.write(b'\x03')

        flag = 0

        if self[1][1] == LSProcessRole.TYPE_INODE:
            flag |= 0b1000
        if self[2][1] is False:
            flag |= 0b0100
        if self[3][1] is False:
            flag |= 0b0010
        if self[4][1] is False:
            flag |= 0b0001

        f.write(num_bin(self[0][1], 8))
        f.write(num_bin(flag, 1))


class LSBindProcess(list):

    VALUES = (
        ('ID', int, 8),
        ('ID Type', bool, ('INODE', 'UID')))

    TYPE_PID = 1
    TYPE_INODE = 0

    @staticmethod
    def read_by_bin(bin_data):
        return LSBindProcess(
            bin_num(bin_data[1:9], 8),
            is_bit_flagged(bin_data[9], 0b001))

    def __init__(self, id_value=0, id_type=TYPE_PID):
        self.append(['ID', id_value])
        self.append(['id_type', id_type])

    def write(self, f):
        f.write(b'\xfe')

        flag = 0

        if self[1][1] == LSBindProcess.TYPE_INODE:
            flag |= 0b001

        f.write(num_bin(self[0][1], 8))
        f.write(num_bin(flag, 1))


class LSBindUser(list):

    VALUES = [
        ('UID', int, 4)]

    @staticmethod
    def read_by_bin(bin_data):
        return LSBindUser(bin_num(bin_data[1:5], 4))

    def __init__(self, uid=0):
        self.append(['UID', uid])

    def write(self, f):
        f.write(b'\xff')
        f.write(num_bin(self[0][1], 4))
        f.write(b'\xff' * 5)


def write_data(top_role):

    with open("/etc/data.sos", "wb") as f:
        write_role(top_role, f)


def write_role(role, f):

    role.write(f)

    for attr in role.file_roles:
        attr.write(f)
    for attr in role.network_roles:
        attr.write(f)
    for attr in role.process_roles:
        attr.write(f)
    for attr in role.bind_processes:
        attr.write(f)
    for attr in role.bind_users:
        attr.write(f)

    for key in role.child_roles.keys():
        write_role(role.child_roles[key], f)


def read_data():
    if not isfile("/etc/data.sos"):
        return LSRole.read_by_bin(bytearray())

    with open("/etc/data.sos", "rb") as f:
        return LSRole.read_by_bin(bytearray(f.read()))
