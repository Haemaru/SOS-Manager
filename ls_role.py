from utils import num_bin
from utils import bin_num
from utils import is_bit_flagged


class LSRole(object):

    @staticmethod
    def read_by_bin(bin_data):

        offset = 0
        roles_list = list()
        roles_tree = LSRole('root')

        while offset < len(bin_data):
            role_name_len = bin_data[offset]
            offset += 1
            role_name = bin_data[offset:(offset + role_name_len)].decode('utf-8')
            offset += role_name_len

            parent_role_name_len = bin_data[offset]
            offset += 1
            parent_role_name = bin_data[offset:(offset + parent_role_name_len)].decode('utf-8')
            offset += parent_role_name_len

            attr_count = bin_num(bin_data[offset:(offset + 4)], 4)
            offset += (600 - role_name_len - parent_role_name_len - 2)

            role = LSRole(role_name, parent_role_name, attr_count)

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
                    print("Error")

            roles_list.append(role)

        for i in range(len(roles_list)):
            if roles_list[i].parent_role_name == '':
                roles_tree.child_roles.append(roles_list[i])
                roles_list[i].parent_role = roles_tree
            else:
                for j in range(len(roles_list)):
                    if roles_list[i].parent_role_name == roles_list[j].role_name:
                        roles_list[i].parent_role = roles_list[j]
                        roles_list[j].child_roles.append(roles_list[i])

        print(roles_tree.child_roles)

        return roles_tree

    def __init__(self, role_name="", parent_role_name="", attr_count=0):
        self.role_name = role_name
        self.parent_role_name = parent_role_name
        self.attr_count = attr_count

        self.child_roles = list()
        self.parent_role = None

        self.file_roles = list()
        self.network_roles = list()
        self.process_roles = list()

        self.bind_processes = list()
        self.bind_users = list()

    def write(self, f):
        role_name_len = len(self.role_name)
        parent_role_name_len = len(self.parent_role_name)

        f.write(num_bin(role_name_len, 1))
        f.write(self.role_name.encode('utf-8'))

        if self.parent_role_name == "":
            f.write(b'\x00')
        else:
            f.write(num_bin(parent_role_name_len, 1))
            f.write(self.parent_role_name.encode('utf-8'))

        f.write(num_bin(self.attr_count, 4))

        size = role_name_len + parent_role_name_len + 2 + 4

        f.write(bytearray(b'\xff' * (600 - size)))


class LSFileRole(object):

    @staticmethod
    def read_by_bin(bin_data):
        return LSFileRole(bin_num(bin_data[1:9], 8), bin_data[9])

    def __init__(self, i_ino=0, u_acc=0):
        self.i_ino = i_ino
        self.u_acc = u_acc

    def write(self, f):
        f.write(b'\x01')
        f.write(num_bin(self.i_ino, 8))
        f.write(num_bin(self.u_acc, 1))


class LSNetworkRole(object):

    @staticmethod
    def read_by_bin(bin_data):
        return LSNetworkRole(bin_num(bin_data[1:3], 2), bin_data[3])

    def __init__(self, port=0, is_allow_open=True):
        self.port = port
        self.is_allow_open = is_allow_open

    def write(self, f):
        f.write(b'\x02')
        f.write(num_bin(self.port, 2))

        if self.is_allow_open:
            f.write(num_bin(0, 1))
        else:
            f.write(num_bin(1, 1))

        f.write(b'\xff' * 6)


class LSProcessRole(object):

    TYPE_PID = 0
    TYPE_INODE = 1

    @staticmethod
    def read_by_bin(bin_data):
        return LSProcessRole(
            bin_num(bin_data[1:9], 8),
            is_bit_flagged(bin_data[9], 0b100),
            is_bit_flagged(bin_data[9], 0b010),
            is_bit_flagged(bin_data[9], 0b001))

    def __init__(
        self,
        id_value=0,
        id_type=TYPE_PID,
        is_allow_kill=True,
        is_allow_trace=True
    ):
        self.id_value = id_value
        self.id_type = id_type
        self.is_allow_kill = is_allow_kill
        self.is_allow_trace = is_allow_trace

    def write(self, f):
        f.write(b'\x03')

        flag = 0

        if self.id_type == LSProcessRole.TYPE_INODE:
            flag |= 0b100
        if self.is_allow_trace is False:
            flag |= 0b010
        if self.is_allow_kill is False:
            flag |= 0b001

        f.write(num_bin(self.id_value, 8))
        f.write(num_bin(flag, 1))


class LSBindProcess(object):

    TYPE_PID = 0
    TYPE_INODE = 1

    @staticmethod
    def read_by_bin(bin_data):
        return LSBindProcess(
            bin_num(bin_data[1:9], 8),
            is_bit_flagged(bin_data[9], 0b001))

    def __init__(self, id_value=0, id_type=TYPE_PID):
        self.id_value = id_value
        self.id_type = id_type

    def write(self, f):
        f.write(b'\xfe')

        flag = 0

        if self.id_type == LSBindProcess.TYPE_INODE:
            flag |= 0b001

        f.write(num_bin(self.id_value, 8))
        f.write(num_bin(flag, 1))


class LSBindUser(object):

    @staticmethod
    def read_by_bin(bin_data):
        return LSBindUser(bin_num(bin_data[1:5], 4))

    def __init__(self, uid=0):
        self.uid = uid

    def write(self, f):
        f.write(b'\xff')
        f.write(num_bin(self.uid, 4))
        f.write(b'\xff' * 5)


def write_data():

    with open("./data.sos", "wb") as f:
        LSRole("test1", "", 3).write(f)
        LSFileRole(1000001, 7).write(f)
        LSNetworkRole(8080, True).write(f)
        LSProcessRole(2000001, LSProcessRole.TYPE_INODE, True, True).write(f)

        LSRole("test2", "test1", 3).write(f)
        LSFileRole(1000002, 7).write(f)
        LSNetworkRole(8090, True).write(f)
        LSBindProcess(3000001, LSBindProcess.TYPE_PID).write(f)

        LSRole("test3", "test1", 3).write(f)
        LSFileRole(1000002, 7).write(f)
        LSNetworkRole(8090, True).write(f)
        LSBindProcess(3000001, LSBindProcess.TYPE_PID).write(f)

        LSRole("test4", "test3", 3).write(f)
        LSFileRole(1000002, 7).write(f)
        LSNetworkRole(8090, True).write(f)
        LSBindProcess(3000001, LSBindProcess.TYPE_PID).write(f)

        LSRole("test5", "test3", 3).write(f)
        LSFileRole(1000002, 7).write(f)
        LSNetworkRole(8090, True).write(f)
        LSBindProcess(3000001, LSBindProcess.TYPE_PID).write(f)

        LSRole("test6", "test2", 3).write(f)
        LSFileRole(1000002, 7).write(f)
        LSNetworkRole(8090, True).write(f)
        LSBindProcess(3000001, LSBindProcess.TYPE_PID).write(f)


def read_data():

    with open("./data.sos", "rb") as f:
        return LSRole.read_by_bin(bytearray(f.read()))


def tree_traversal(roles_tree_node, depth):

    text = ""
    for i in range(depth):
        text += "  "
    text += "-"
    text += str(roles_tree_node.role_name)
    print(text)

    for i in range(len(roles_tree_node.child_roles)):
        tree_traversal(roles_tree_node.child_roles[i], depth + 1)


def main():

    write_data()

    roles_tree = read_data()

    tree_traversal(roles_tree, 0)


if __name__ == '__main__':
    main()
