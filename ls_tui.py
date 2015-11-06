from ls_role import read_data, write_data
from ls_role import LSRole
from ls_role import LSFileRole, LSNetworkRole, LSProcessRole
from ls_role import LSBindProcess, LSBindUser

import urwid


class LSRolesTreeBox(urwid.ListBox):

    role_names = list()
    focused_role = None

    def make_body(self, role, depth=0, body=list()):
        body.append(LSRolesTreeWidget(role, depth))
        self.role_names.append(role.role_name)

        for key in role.child_roles.keys():
            self.make_body(role.child_roles[key], depth + 1, body)

        return body

    def __init__(self, top_role, attr_types_list):
        urwid.ListBox.__init__(
            self,
            urwid.SimpleFocusListWalker(self.make_body(top_role)))

        self.top_role = top_role
        self.attr_types_list = attr_types_list

        LSRolesTreeBox.focused_role = top_role
        self.update_attr_types_list()

    def keypress(self, size, key):
        key = urwid.ListBox.keypress(self, size, key)

        if key in ('c', 'C'):
            self.create_role()
        elif key in ('d', 'D'):
            self.delete_role()
        else:
            return key

    def change_focus(
        self,
        size,
        position,
        offset_inset=0,
        coming_from=None,
        cursor_coords=None,
        snap_rows=None
    ):
        self.set_attr_map('normal')

        urwid.ListBox.change_focus(
            self,
            size,
            position,
            offset_inset,
            coming_from,
            cursor_coords,
            snap_rows)
        self.update_attr_types_list()

    def create_role(self):
        focused_widget, position = self.get_focus()

        create_count = 0
        while True:
            create_count += 1
            new_role_name = 'new_role' + str(create_count)

            if new_role_name not in LSRolesTreeBox.role_names:
                break

        new_role = LSRole(new_role_name, parent_role=focused_widget.role)
        focused_widget.role.child_roles[new_role_name] = new_role

        new_widget = LSRolesTreeWidget(new_role, focused_widget.depth + 1)
        self.body.insert(position + 1, new_widget)

        self.role_names.append(new_role_name)
        self.set_focus(position + 1)

    def delete_role(self):
        focused_widget, position = self.get_focus()
        focused_role = focused_widget.role

        if position == 0:
            return

        parent_position = position
        while True:
            parent_position -= 1
            parent_widget = self.body[parent_position]

            if focused_role.parent_role == parent_widget.role:
                break

        parent_role = parent_widget.role
        child_roles = focused_role.child_roles

        del parent_role.child_roles[focused_role.role_name]
        for key in child_roles.keys():
            child_roles[key].parent_role = parent_role
            parent_role.child_roles[key] = child_roles[key]

        del self.body[position]
        for i in range(position, len(self.body)):
            if self.body[i].depth <= focused_widget.depth:
                break

            self.body[i].shift_left()

        LSRolesTreeBox.role_names.remove(focused_role.role_name)
        self.set_focus(parent_position)

    def set_attr_map(self, attr):
        position = self.get_focus()[1]
        if position is not None:
            self.body[position].set_attr_map({None: attr})

    def update_attr_types_list(self):
        self.set_attr_map('selected')

        role = self.get_focus()[0].role
        if role is not None:
            LSRolesTreeBox.focused_role = role

        self.attr_types_list.update_list()


class LSRolesTreeWidgetColumns(urwid.Columns):

    def __init__(self, expanded_icon, role_name_edit):
        urwid.Columns.__init__(
            self,
            [('fixed', 1, expanded_icon), role_name_edit],
            dividechars=1)

    def keypress(self, size, key):
        return self.contents[1].keypress(size, key)


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
        self.is_editing = False

    def selectable(self):
        return self.is_editing

    def keypress(self, size, key):
        key = urwid.Edit.keypress(self, size, key)


class LSRolesTreeWidget(urwid.AttrMap):

    unexpanded_icon = urwid.AttrMap(urwid.SelectableIcon('+', 0), 'mark')
    expanded_icon = urwid.AttrMap(urwid.SelectableIcon('-', 0), 'mark')
    none_icon = urwid.AttrMap(urwid.SelectableIcon(' ', 0), 'mark')

    LEFT_SPACE = 3

    NORMAL = 'normal'
    FOCUSED = 'focused'
    SELECTED = 'selected'

    def __init__(self, role, depth):
        self.role = role
        self.depth = depth

        self.expanded_icon = LSRolesTreeWidget.expanded_icon
        self.role_name_edit = LSRolesTreeWidgetEdit('', role.role_name)
        self.role_columns = LSRolesTreeWidgetColumns(
            self.expanded_icon,
            self.role_name_edit)
        self.left_padding = urwid.Padding(
            self.role_columns,
            left=depth * self.LEFT_SPACE)

        urwid.AttrMap.__init__(
            self,
            self.left_padding,
            self.NORMAL,
            self.FOCUSED)

    def shift_left(self):
        self.depth -= 1
        self.left_padding.left = self.depth * self.LEFT_SPACE
        self.left_padding._invalidate()

    def keypress(self, size, key):
        if self.role_name_edit.is_editing is True:
            if key == 'enter':
                parent_role = self.role.parent_role
                old_role_name = self.role.role_name
                new_role_name = self.role_name_edit.get_edit_text()

                if old_role_name != new_role_name:
                    if new_role_name in LSRolesTreeBox.role_names:
                        return None

                    self.role.role_name = new_role_name
                    parent_role.child_roles[new_role_name] = \
                        parent_role.child_roles.pop(old_role_name)

                    LSRolesTreeBox.role_names.remove(old_role_name)
                    LSRolesTreeBox.role_names.append(new_role_name)

                self.set_focus_to_icon()
            else:
                self.role_name_edit.keypress(size, key)
        elif key == 'enter':
            if self.role.role_name != 'default':
                self.set_focus_to_edit()
        else:
            return key

    def set_focus_to_edit(self):
        self.role_name_edit.is_editing = True
        self.role_columns.set_focus_column(1)

    def set_focus_to_icon(self):
        self.role_name_edit.is_editing = False
        self.role_columns.set_focus_column(0)


class LSAttrTypesListBox(urwid.ListBox):

    attr_types = [
        (LSFileRole, 'File Role'),
        (LSNetworkRole, 'Network Role'),
        (LSProcessRole, 'Process Role'),
        (LSBindProcess, 'Bind Process'),
        (LSBindUser, 'Bind Users')]
    focused_attr_type = None
    focused_attrs = None

    def __init__(self, attrs_list):
        urwid.ListBox.__init__(
            self,
            urwid.SimpleFocusListWalker(
                [LSListTextWidget(
                    attr_type[1]) for attr_type in self.attr_types]))

        self.attrs_list = attrs_list
        self.body[0].set_attr_map({None: 'selected'})

    def change_focus(
        self,
        size,
        position,
        offset_inset=0,
        coming_from=None,
        cursor_coords=None,
        snap_rows=None
    ):
        self.set_attr_map('normal')

        urwid.ListBox.change_focus(
            self,
            size,
            position,
            offset_inset,
            coming_from,
            cursor_coords,
            snap_rows)
        self.update_attrs_list()

        self.set_attr_map('selected')

    def update_list(self):
        self.update_attrs_list()

    def update_attrs_list(self):
        role = LSRolesTreeBox.focused_role
        attrs = [
            role.file_roles,
            role.network_roles,
            role.process_roles,
            role.bind_processes,
            role.bind_users
        ]

        position = self.get_focus()[1]
        LSAttrTypesListBox.focused_attr_type = \
            LSAttrTypesListBox.attr_types[position]
        LSAttrTypesListBox.focused_attrs = attrs[position]

        self.attrs_list.update_list()

    def set_attr_map(self, attr):
        position = self.get_focus()[1]
        if position is not None:
            self.body[position].set_attr_map({None: attr})


class LSListTextWidget(urwid.AttrMap):

    NORMAL = 'normal'
    FOCUSED = 'focused'
    SELECTED = 'selected'

    def __init__(self, text):
        urwid.AttrMap.__init__(
            self,
            urwid.Text(' ' + text, align=urwid.LEFT),
            self.NORMAL,
            self.FOCUSED)

    def selectable(self):
        return True

    def keypress(self, size, key):
        return key


class LSAttrsListWidget(LSListTextWidget):

    def __init__(self, attr):
        self.attr = attr

        LSListTextWidget.__init__(
            self, self.attr[0][0] + ' : ' + str(self.attr[0][1]))

    def update_widget(self):
        self.original_widget.set_text(
            ' ' + self.attr[0][0] + ' : ' + str(self.attr[0][1]))
        self.original_widget._invalidate()


class LSAttrsListBox(urwid.ListBox):

    focused_widget = None

    def __init__(self, attr_values_list):
        urwid.ListBox.__init__(self, urwid.SimpleFocusListWalker([]))
        self.attr_values_list = attr_values_list

    def change_focus(
        self,
        size,
        position,
        offset_inset=0,
        coming_from=None,
        cursor_coords=None,
        snap_rows=None
    ):
        self.set_attr_map('normal')

        urwid.ListBox.change_focus(
            self,
            size,
            position,
            offset_inset,
            coming_from,
            cursor_coords,
            snap_rows)
        self.update_attr_values_list()

    def keypress(self, size, key):
        if key in ('c', 'C'):
            self.create_attr()
        elif key in ('d', 'D'):
            self.delete_attr()

        key = urwid.ListBox.keypress(self, size, key)

        return key

    def create_attr(self):
        attrs = LSAttrTypesListBox.focused_attrs

        new_attr = LSAttrTypesListBox.focused_attr_type[0]()
        attrs.append(new_attr)
        self.body.append(LSAttrsListWidget(new_attr))

        self.update_list()
        self.set_focus(len(attrs) - 1)

    def delete_attr(self):
        if len(LSAttrTypesListBox.focused_attrs) != 0:
            del LSAttrTypesListBox.focused_attrs[self.get_focus()[1]]
            self.update_list()

    def update_list(self):
        del self.body[:]

        attrs = LSAttrTypesListBox.focused_attrs

        if len(attrs) == 0:
            self.body.append(
                LSListTextWidget('(need to create attr)'))
        else:
            for attr in attrs:
                self.body.append(LSAttrsListWidget(attr))

        self.update_attr_values_list()

    def set_attr_map(self, attr):
        position = self.get_focus()[1]
        if position is not None:
            self.body[position].set_attr_map({None: attr})

    def update_attr_values_list(self):
        self.set_attr_map('selected')

        position = self.get_focus()[1]

        if position is None or len(LSAttrTypesListBox.focused_attrs) == 0:
            LSAttrsListBox.focused_widget = None
        else:
            LSAttrsListBox.focused_widget = self.body[position]
        self.attr_values_list.update_list()


class LSAttrValuesListBoxIntEdit(urwid.IntEdit):

    def __init__(
        self,
        caption='',
        default=None,
        int_data=None
    ):
        urwid.Edit.__init__(
            self,
            ' ' + caption,
            default)
        self.int_data = int_data
        self.modifiable = False

    def selectable(self):
        return True

    def set_modifiable(self, modifiable):
        self.modifiable = modifiable

    def keypress(self, size, key):
        if self.modifiable is True:
            if key == 'enter':
                self.modifiable = False
                self.int_data[1] = int(self.get_edit_text())
                return key
            else:
                key = urwid.Edit.keypress(self, size, key)
        else:
            if key == 'enter':
                self.modifiable = True

            return key


class LSAttrValuesListBoxBoolEdit(urwid.Edit):

    def __init__(
        self,
        caption='',
        edit_text='',
        bool_data=None,
        bool_text=None
    ):
        urwid.Edit.__init__(
            self,
            ' ' + caption,
            edit_text)
        self.bool_data = bool_data
        self.bool_text = bool_text

    def selectable(self):
        return True

    def keypress(self, size, key):
        if key == 'enter':
            self.bool_data[1] = bool(self.bool_data[1] ^ True)
            self.set_edit_text(self.bool_text[int(self.bool_data[1] ^ True)])

        return key


class LSAttrValuesListBox(urwid.ListBox):

    def __init__(self):
        urwid.ListBox.__init__(self, urwid.SimpleFocusListWalker([]))

    def update_list(self):
        widget = LSAttrsListBox.focused_widget

        del self.body[:]

        if len(LSAttrTypesListBox.focused_attrs) == 0:
            self.body.append(
                LSListTextWidget('(need to create attr)'))
        elif widget is not None:
            for i in range(len(widget.attr)):
                if widget.attr.VALUES[i][1] == int:
                    edit = LSAttrValuesListBoxIntEdit(
                        str(widget.attr[i][0]) + ' : ',
                        str(widget.attr[i][1]),
                        int_data=widget.attr[i])
                else:
                    edit = LSAttrValuesListBoxBoolEdit(
                        str(widget.attr[i][0]) + ' : ',
                        widget.attr.VALUES[i][2][int(widget.attr[i][1] ^ 1)],
                        bool_data=widget.attr[i],
                        bool_text=widget.attr.VALUES[i][2])

                self.body.append(urwid.AttrMap(edit, 'normal', 'focused'))

    def keypress(self, size, key):
        key = urwid.ListBox.keypress(self, size, key)

        if self.get_focus()[1] == 0 and \
                key == 'enter' and \
                LSAttrsListBox.focused_widget is not None:
            LSAttrsListBox.focused_widget.update_widget()

        return key


class LSAttrValuesListWalker(urwid.SimpleFocusListWalker):

    def __init__(self, contents):
        urwid.SimpleFocusListWalker.__init__(self, contents)


class LSListLineBox(urwid.AttrMap):

    NORMAL = 'normal'
    FOCUSED = 'focused'
    SELECTED = 'selected'

    def __init__(self, list_box, title):
        urwid.AttrMap.__init__(
            self,
            urwid.LineBox(urwid.Padding(list_box, left=1, right=1), title),
            self.NORMAL)

    def selectable(self):
        return True


class LSLayout(object):

    layout_header = None
    layout_body = None
    layout_footer = None

    def __init__(self):
        self.palette = [
            ('normal', 'black', 'light gray'),
            ('focused', 'light gray', 'dark blue',),
            ('selected', 'light gray', 'dark gray'),
            ('mark', 'black', 'dark cyan', 'bold'),
        ]

        self.roles_data = read_data()
        self.attr_values = LSAttrValuesListBox()
        self.attrs = LSAttrsListBox(self.attr_values)
        self.attr_types = LSAttrTypesListBox(self.attrs)
        self.roles = LSRolesTreeBox(self.roles_data, self.attr_types)

        LSLayout.layout_body = urwid.Padding(
            urwid.Columns(
                [
                    LSListLineBox(self.roles, 'Roles'),
                    ('fixed', 20, LSListLineBox(self.attr_types, 'Types')),
                    ('fixed', 30, LSListLineBox(self.attrs, 'Attrs')),
                    ('fixed', 30, LSListLineBox(self.attr_values, 'Values')),
                ], 2), left=1, right=2
        )

        LSLayout.layout_header = urwid.Padding(
            urwid.LineBox(urwid.Text(' SOS-Manager')), left=1, right=2)
        LSLayout.layout_footer = urwid.Padding(
            urwid.LineBox(urwid.Text(
                ' Help - Create : c, Delete : d, ' +
                'Rename/Modify : enter, Save : s, Quit : q')
            ), left=1, right=2)

        urwid.MainLoop(urwid.AttrMap(
            urwid.Frame(
                LSLayout.layout_body,
                header=LSLayout.layout_header,
                footer=LSLayout.layout_footer
            ), 'normal'),
            self.palette,
            unhandled_input=self.save_or_exit,).run()

    def save_or_exit(self, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()
        elif key in ('s', 'S'):
            write_data(self.roles_data)


# f = open("log.txt", "w")


# def log(text):
#     f.write(str(text) + '\n')
#     f.flush()


def main():
    LSLayout()


if __name__ == "__main__":
    main()
