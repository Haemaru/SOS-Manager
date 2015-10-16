from ls_role import read_data, write_data, LSRole

import urwid

"""
columns._set_widget_list([])
topnode.get_child_keys(True)
"""


class LSRolesTreeWidget(urwid.TreeWidget):

    def get_display_text(self):
        return self.get_node().get_value().role_name

    def selectable(self):
        return True

    def keypress(self, size, key):
        if key is not 'right':
            key = urwid.TreeWidget.keypress(self, size, key)

        return key


class LSRolesTreeNode(urwid.TreeNode):

    def load_widget(self):
        return LSRolesTreeWidget(self)


class LSRolesParentNode(urwid.ParentNode):

    def load_parent(self):
        return self.get_value().parent_role

    def load_widget(self):
        return LSRolesTreeWidget(self)

    def load_child_keys(self):
        return range(len(self.get_value().child_roles))

    def load_child_node(self, key):
        childdata = self.get_value().child_roles[key]
        childdepth = self.get_depth() + 1
        if len(childdata.child_roles) == 0:
            childclass = LSRolesTreeNode
        else:
            childclass = LSRolesParentNode
        return childclass(childdata, parent=self, key=key, depth=childdepth)


class LSRolesTreeListBox(urwid.TreeListBox):

    def __init__(self, body, attr_types):
        urwid.TreeListBox.__init__(self, body)
        self.attr_types = attr_types
        self.update_attr_types()

    def change_focus(
        self,
        size,
        position,
        offset_inset=0,
        coming_from=None,
        cursor_coords=None,
        snap_rows=None
    ):
        urwid.ListBox.change_focus(
            self,
            size,
            position,
            offset_inset,
            coming_from,
            cursor_coords,
            snap_rows)
        self.update_attr_types()

    def keypress(self, size, key):
        return urwid.TreeListBox.keypress(self, size, key)

    def update_attr_types(self):
        self.attr_types.set_role(self.get_focus()[1].get_value())
        self.attr_types.update_attrs()


class LSRolesTreeWalker(urwid.TreeWalker):

    def __init__(self, start_from):
        urwid.TreeWalker.__init__(self, start_from)


class LSAttrTypesListBox(urwid.ListBox):

    def __init__(self, body, attrs):
        urwid.ListBox.__init__(self, body)
        self.attrs = attrs

    def change_focus(
        self,
        size,
        position,
        offset_inset=0,
        coming_from=None,
        cursor_coords=None,
        snap_rows=None
    ):
        urwid.ListBox.change_focus(
            self,
            size,
            position,
            offset_inset,
            coming_from,
            cursor_coords,
            snap_rows)
        self.update_attrs()

    def set_role(self, role):
        self.role = role

    def update_attrs(self):
        focus = self.get_focus()[1]
        role_types = [
            self.role.file_roles,
            self.role.network_roles,
            self.role.process_roles,
            self.role.bind_processes,
            self.role.bind_users
        ]
        role = role_types[focus]

        del self.attrs.body[:]
        for i in range(len(role)):
            self.attrs.body.append(urwid.Button("role " + str(i)))


class LSAttrTypesListWalker(urwid.SimpleFocusListWalker):

    def __init__(self, contents):
        urwid.SimpleFocusListWalker.__init__(self, contents)


class LSAttrsListBox(urwid.ListBox):

    def change_focus(
        self,
        size,
        position,
        offset_inset=0,
        coming_from=None,
        cursor_coords=None,
        snap_rows=None
    ):
        urwid.ListBox.change_focus(
            self,
            size,
            position,
            offset_inset,
            coming_from,
            cursor_coords,
            snap_rows)
        log("LSAttrListBox.change_focus")


class LSAttrsListWalker(urwid.SimpleFocusListWalker):

    def __init__(self, contents):
        urwid.SimpleFocusListWalker.__init__(self, contents)


class LSColumns(urwid.Columns):

    def keypress(self, size, key):
        key = urwid.Columns.keypress(self, size, key)

        return key


def exit(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()


f = open("log.txt", "w")


def log(text):
    f.write(str(text) + '\n')
    f.flush()

write_data()
roles_data = read_data()

attrs_list_walker = LSAttrsListWalker([])
attrs_list_box = LSAttrsListBox(attrs_list_walker)

attr_types_list_walker = LSAttrTypesListWalker([
    urwid.Button("File Roles"),
    urwid.Button("Network Roles"),
    urwid.Button("Process Roles"),
    urwid.Button("Bind Processes"),
    urwid.Button("Bind Users")])
attr_types_list_box = LSAttrTypesListBox(
    attr_types_list_walker,
    attrs_list_box)

roles_root_node = LSRolesParentNode(roles_data)
roles_tree_walker = LSRolesTreeWalker(roles_root_node)
roles_tree_box = LSRolesTreeListBox(
    roles_tree_walker,
    attr_types_list_box)

columns_data = [roles_tree_box, attr_types_list_box, attrs_list_box]
columns = LSColumns(columns_data)

header = urwid.Text("this is header")
footer = urwid.Text("this is footer")
top_most = urwid.Frame(columns, header=header, footer=footer)

"""
top_most = urwid.ListBox(urwid.SimpleFocusListWalker([]))
top_most.body.append(urwid.Button("test"))
"""


def main():
    urwid.MainLoop(top_most, unhandled_input=exit).run()


if __name__ == "__main__":
    main()
