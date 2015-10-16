from ls_role import read_data
from ls_role import write_data
from ls_role import LSRole

import urwid


class LSTreeWidget(urwid.TreeWidget):
    """ --- TREE --- """

    def get_display_text(self):
        return self.get_node().get_value().role_name

    def selectable(self):
        return True

    def keypress(self, size, key):
        footer.set_text(key)
        log(columns._get_widget_list())
        log(topnode._children)

        new_role = LSRole("new_role")
        roles_tree.child_roles.append(new_role)
        topnode.get_child_keys(True)

        return urwid.TreeWidget.keypress(self, size, key)


class LSTreeNode(urwid.TreeNode):

    def load_widget(self):
        return LSTreeWidget(self)


class LSParentNode(urwid.ParentNode):

    def load_parent(self):
        return self.get_value().parent_role

    def load_widget(self):
        return LSTreeWidget(self)

    def load_child_keys(self):
        return range(len(self.get_value().child_roles))

    def load_child_node(self, key):
        childdata = self.get_value().child_roles[key]
        childdepth = self.get_depth() + 1
        if len(childdata.child_roles) == 0:
            childclass = LSTreeNode
        else:
            childclass = LSParentNode
        return childclass(childdata, parent=self, key=key, depth=childdepth)


class LSTreeListBox(urwid.TreeListBox):

    def keypress(self, size, key):
        return urwid.TreeListBox.keypress(self, size, key)


class LSColumns(urwid.Columns):
    """ --- COLUMNS --- """

    def keypress(self, size, key):
        return urwid.Columns.keypress(self, size, key)


def exit(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()


""" --- LOG --- """
f = open("log.txt", "w")


def log(text):
    f.write(str(text) + '\n')
    f.flush()

write_data()

footer = urwid.Text("this is footer")
listbox2 = urwid.ListBox(urwid.SimpleFocusListWalker([
    urwid.Button("btn1"),
    urwid.Button("btn2")]))
listbox3 = urwid.ListBox(urwid.SimpleFocusListWalker([
    urwid.Button("btn3"),
    urwid.Button("btn4")]))
roles_tree = read_data()

topnode = LSParentNode(roles_tree)
walker = urwid.TreeWalker(topnode)
listbox = LSTreeListBox(walker)
listbox.offset_rows = 1

columns_data = [listbox, listbox2]
columns = LSColumns(columns_data)

top_most = urwid.Frame(columns, footer=footer)


def main():
    urwid.MainLoop(top_most, unhandled_input=exit).run()


if __name__ == "__main__":
    main()
