from ls_role import read_data, write_data, LSRole

import urwid


class LSRolesTreeWidgetPadding(urwid.Padding):

    def __init__(
        self,
        w,
        align=urwid.LEFT,
        width=urwid.RELATIVE_100,
        min_width=None,
        left=0,
        right=0
    ):
        urwid.Padding.__init__(
            self,
            w,
            align,
            width,
            min_width,
            left,
            right)
        self._focus = w[0]

    @property
    def focus(self):
        return self._focus


class LSRolesTreeWidgetColumns(urwid.Columns):

    def keypress(self, size, key):
        return self.contents[1][0].keypress(size, key)


class LSRolesTreeWidgetEdit(urwid.Edit):

    def __init__(
        self,
        caption=u"",
        edit_text=u"",
        multiline=False,
        align=urwid.LEFT,
        wrap=urwid.SPACE,
        allow_tab=False,
        edit_pos=None,
        layout=None,
        mask=None
    ):
        urwid.Edit.__init__(
            self,
            caption,
            edit_text,
            multiline,
            align,
            wrap,
            allow_tab,
            edit_pos,
            layout,
            mask)
        self.modifiable = False

    def selectable(self):
        return self.modifiable

    def set_modifiable(self, modifiable):
        self.modifiable = modifiable

    def keypress(self, size, key):
        key = urwid.Edit.keypress(self, size, key)


class LSRolesTreeWidget(urwid.TreeWidget):

    def __init__(self, node):
        urwid.TreeWidget.__init__(self, node)
        self.inner_columns = self._wrapped_widget.original_widget
        self._focus = self._wrapped_widget

        if len(self._node.get_value().child_roles) == 0:
            self.is_leaf = True

        self.is_modifying = False

    @property
    def focus(self):
        return self._focus

    def get_indented_widget(self):
        widget = self.get_inner_widget()
        if not self.is_leaf:
            widget = LSRolesTreeWidgetColumns([(
                'fixed',
                1,
                [self.unexpanded_icon, self.expanded_icon][self.expanded]),
                widget],
                dividechars=1)

        indent_cols = self.get_indent_cols()
        return LSRolesTreeWidgetPadding(
            widget,
            width=('relative', 100),
            left=indent_cols)

    def get_display_text(self):
        return self.get_node().get_value().role_name

    def load_inner_widget(self):
        self.inner_edit = LSRolesTreeWidgetEdit('', self.get_display_text())
        return self.inner_edit

    def selectable(self):
        return True

    def keypress(self, size, key):
        if self.is_modifying is True:
            if key == 'enter':
                self.set_focus_to_icon()
            else:
                self.inner_edit.keypress(size, key)
        elif key == 'enter':
            self.set_focus_to_edit()
        elif key == 'tab':
            if self.expanded is True:
                self.expanded = False
                self.update_expanded_icon()
            else:
                self.expanded = True
                self.update_expanded_icon()
        else:
            return key

    def set_focus_to_edit(self):
        self.is_modifying = True
        self.inner_edit.set_modifiable(True)
        self.inner_columns.set_focus_column(1)
        # self.inner_edit.move_cursor_to_coords((20, ), 15, 0)

    def set_focus_to_icon(self):
        self.is_modifying = False
        self.inner_edit.set_modifiable(False)
        self.inner_columns.set_focus_column(0)


class LSRolesTreeNode(urwid.ParentNode):

    def get_parent(self):
        return urwid.ParentNode.get_parent(self)

    def load_parent(self):
        log('=================load parent call===================')

    def load_widget(self):
        return LSRolesTreeWidget(self)

    def load_child_keys(self):
        return self.get_value().child_roles.keys()

    def get_child_node(self, key, reload=True):
        if key not in self._children or reload is True:
            self._children[key] = self.load_child_node(key)
        return self._children[key]

    def get_child_index(self, key):
        try:
            return self.get_child_keys(True).index(key)
        except ValueError:
            return None

    def load_child_node(self, key):
        if key is None:
            log('error!')
            return None
        else:
            return LSRolesTreeNode(
                value=self.get_value().child_roles[key],
                parent=self,
                key=key,
                depth=self.get_depth() + 1
            )


class LSRolesTreeListBox(urwid.TreeListBox):

    def __init__(self, body, attr_types_list):
        urwid.TreeListBox.__init__(self, body)
        self.create_count = 1
        self.attr_types_list = attr_types_list
        self.set_role()

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
        self.set_role()

    def keypress(self, size, key):
        key = self.__super.keypress(size, key)

        if key == 'c':
            self.create_role(size)
        elif key == 'd':
            self.delete_role(size)
        else:
            return key

    def unhandled_input(self, size, input):
        return input

    def create_role(self, size):
        focused_node = self.get_focus()[1]
        focused_role = focused_node.get_value()

        new_role_name = 'new_role' + str(self.create_count)
        self.create_count += 1
        new_role = LSRole(new_role_name)
        new_node = LSRolesTreeNode(
            value=new_role,
            parent=focused_node,
            key=new_role_name,
            depth=focused_node.get_depth() + 1
        )

        focused_role.child_roles[new_role_name] = new_role
        focused_node._children[new_role_name] = new_node
        focused_node.get_child_keys(True)

        self.change_focus(size, new_node)

    def delete_role(self, size):
        focused_node = self.get_focus()[1]
        focused_role = focused_node.get_value()
        parent_node = focused_node.get_parent()

        if parent_node is not None:
            parent_role = parent_node.get_value()

            del parent_role.child_roles[focused_role.role_name]
            del parent_node._children[focused_role.role_name]

            for child in focused_node._children.items():
                parent_role.child_roles[child[0]] = child[1].get_value()
                parent_node._children[child[0]] = child[1]
            parent_node.get_child_keys(True)

            self.change_focus(size, parent_node)

    def set_role(self):
        self.attr_types_list.set_role(self.get_focus()[1].get_value())


class LSRolesTreeWalker(urwid.TreeWalker):

    def __init__(self, start_from):
        urwid.TreeWalker.__init__(self, start_from)


class LSAttrTypesListBox(urwid.ListBox):

    def __init__(self, body, attrs_list):
        urwid.ListBox.__init__(self, body)
        self.attrs_list = attrs_list

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
        self.set_attr_type()

    def set_role(self, role):
        self.role = role
        self.set_attr_type()

    def set_attr_type(self):
        focus = self.get_focus()[1]
        attr_types = [
            self.role.file_roles,
            self.role.network_roles,
            self.role.process_roles,
            self.role.bind_processes,
            self.role.bind_users
        ]
        attr_type = attr_types[focus]

        self.attrs_list.set_attr_type(attr_type)


class LSAttrTypesListWalker(urwid.SimpleFocusListWalker):

    def __init__(self, contents):
        urwid.SimpleFocusListWalker.__init__(self, contents)


class LSAttrsListBox(urwid.ListBox):

    def __init__(self, body, values_list):
        urwid.ListBox.__init__(self, body)
        self.values_list = values_list

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
        self.set_attr()

    def keypress(self, size, key):
        if key == 'c':
            log(self.attr_type.__class__)

        return urwid.ListBox.keypress(self, size, key)

    def set_attr_type(self, attr_type=None):
        if attr_type is not None:
            self.attr_type = attr_type

        del self.body[:]

        for attr in attr_type:
            self.body.append(urwid.Edit(attr[0][0] + ' : ' + str(attr[0][1])))

        self.set_attr()

    def set_attr(self):
        focus = self.get_focus()[1]

        if focus is not None:
            attr = self.attr_type[focus]
        else:
            attr = None

        self.values_list.set_attr(attr)


class LSAttrsListWalker(urwid.SimpleFocusListWalker):

    def __init__(self, contents):
        urwid.SimpleFocusListWalker.__init__(self, contents)


class LSAttrValuesListBox(urwid.ListBox):

    def __init__(self, body):
        urwid.ListBox.__init__(self, body)

    def set_attr(self, attr):
        self.attr = attr

        del self.body[:]

        if attr is not None:
            for value in attr:
                self.body.append(urwid.Edit(
                    str(value[0]) + ' : ',
                    str(value[1])))


class LSAttrValuesListWalker(urwid.SimpleFocusListWalker):

    def __init__(self, contents):
        urwid.SimpleFocusListWalker.__init__(self, contents)


class LSColumns(urwid.Columns):

    def keypress(self, size, key):
        key = urwid.Columns.keypress(self, size, key)

        return key


def exit(key):
    if key in ('q', 'Q'):
        log('-----------------exit------------------')
        raise urwid.ExitMainLoop()


f = open("log.txt", "w")


def log(text):
    f.write(str(text) + '\n')
    f.flush()


write_data()
roles_data = read_data()

attr_values_list_walker = LSAttrValuesListWalker([])
attr_values_list_box = LSAttrValuesListBox(attr_values_list_walker)

attrs_list_walker = LSAttrsListWalker([])
attrs_list_box = LSAttrsListBox(attrs_list_walker, attr_values_list_box)

attr_types_list_walker = LSAttrTypesListWalker([
    urwid.Button("File Roles"),
    urwid.Button("Network Roles"),
    urwid.Button("Process Roles"),
    urwid.Button("Bind Processes"),
    urwid.Button("Bind Users")])
attr_types_list_box = LSAttrTypesListBox(
    attr_types_list_walker,
    attrs_list_box)

roles_root_node = LSRolesTreeNode(roles_data)
log('origin ' + str(id(roles_root_node)))
log(type(roles_root_node))

roles_tree_walker = LSRolesTreeWalker(roles_root_node)
roles_tree_box = LSRolesTreeListBox(
    roles_tree_walker,
    attr_types_list_box)

columns_data = [
    roles_tree_box,
    attr_types_list_box,
    attrs_list_box,
    attr_values_list_box]
columns = LSColumns(columns_data)

root_widget = roles_root_node.get_widget()


header = urwid.Edit("test")
footer = urwid.Text("this is footer")
top_most = urwid.Frame(columns, header=header, footer=footer)


def node_traversal(node, depth):
    text = ""
    for i in range(depth):
        text += "  "
    text += "-"
    text += str(node.get_value().role_name + ' - ' + \
        str([node._children[n].get_value().role_name for n in node._children]))
    log(text)

    for key in node.get_value().child_roles.keys():
        node_traversal(node._children[key], depth + 1)


def tree_update(node):
    log(node.get_value().role_name)
    for key in node.get_child_keys(True):
        node._children.clear()
        node.get_child_node(key, True)
        tree_update(node._children[key])


def tree_traversal(roles_tree_node, depth):

    text = ""
    for i in range(depth):
        text += "  "
    text += "-"
    text += str(roles_tree_node.role_name)
    log(text)

    for key in roles_tree_node.child_roles.keys():
        tree_traversal(roles_tree_node.child_roles[key], depth + 1)


def main():
    urwid.MainLoop(top_most, unhandled_input=exit).run()


if __name__ == "__main__":
    main()
