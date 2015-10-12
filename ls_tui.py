from ls_role import read_data
from ls_role import write_data

import urwid


class LSRolesTreeWidget(urwid.TreeWidget):

    def get_display_text(self):
        return self.get_node().get_value().role_name

    def selectable(self):
        return True


class LSRolesNode(urwid.TreeNode):

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
            childclass = LSRolesNode
        else:
            childclass = LSRolesParentNode
        return childclass(childdata, parent=self, key=key, depth=childdepth)


def main():

    write_data()

    roles_tree = read_data()

    topnode = LSRolesParentNode(roles_tree)
    listbox = urwid.TreeListBox(urwid.TreeWalker(topnode))
    listbox.offset_rows = 1

    urwid.MainLoop(urwid.Frame(listbox)).run()


if __name__ == "__main__":
    main()
