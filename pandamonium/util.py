from threading import Lock


# TODO: Actually respect range limits, and reuse released IDs.
class IDGenerator:
    def __init__(self, id_range):
        self.counter = id_range[0] - 1
        self.lock = Lock()

    def get_new(self):
        with self.lock:
            self.counter += 1
            return self.counter


class AssociativeTable:
    class AssociativeColumn:
        def __init__(self, table, name):
            self.table = table
            self.name = name
            self.elements = {}

        def __contains__(self, element):
            return element in self.elements

        def add(self, element):
            if element in self.table._column_of_element:
                raise ValueError(element)
            self.elements[element] = set()
            self.table._column_of_element[element] = self

        def add_assoc(self, element, associated_element):
            self.elements[element].add(associated_element)

        def del_assoc(self, element, associated_element):
            self.elements[element].remove(associated_element)

        def __getitem__(self, element):
            return self.elements[element]

        # FIXME: Remove?
        def get(self, element):
            return self[element]

        def __delitem__(self, element):
            for associated in self[element]:
                pass

        def __repr__(self):
            return "<AssociativeColumn {}: {}>".format(self.name, self.elements)

    def __init__(self, *column_names):
        self._columns = set(column_names)
        self._column = {}
        for column_name in column_names:
            column = self.AssociativeColumn(self, column_name)
            setattr(self, column_name, column)
            self._column[column_name] = column
        self._column_of_element = {}

    def __contains__(self, element):
        return element in self._column_of_element

    def __getitem__(self, element):
        if element not in self._column_of_element:
            raise KeyError
        return self._column_of_element[element][element]

    def get(self, *elements, tables=None, path=None):
        for element in elements:
            if element not in self._column_of_element:
                raise KeyError("Unknown element '{}'".format(element))
        if path is not None:
            if len(path) < 2:
                raise Exception("Path must contain multiple tables")
            for column in path:
                if column not in self._column.values():
                    raise KeyError("Column '{}' not in table".format(column))
            for target_table in path:
                elements = self.get(*elements, tables=(target_table, ))
            return elements
        else:
            all_assocs = set()
            for element in elements:
                assocs = self._column_of_element[element][element]
                all_assocs.update(assocs)
            if tables is None:
                return all_assocs
            else:
                return {assoc for assoc in all_assocs
                        if self._column_of_element[assoc] in tables}

    def __delitem__(self, element):
        if element not in self:
            raise KeyError
        associates = set(self[element])  # FIXME: Why do I need to copy it?
        for associate in associates:
            self._dissoc(element, associate)
        del self._column_of_element[element]

    def _assoc(self, element_a, element_b):
        if element_a not in self._column_of_element:
            raise KeyError(element_a)
        if element_b not in self._column_of_element:
            raise KeyError(element_b)
        self._column_of_element[element_a].add_assoc(element_a, element_b)
        self._column_of_element[element_b].add_assoc(element_b, element_a)

    def _dissoc(self, element_a, element_b):
        if element_a not in self._column_of_element:
            raise KeyError(element_a)
        if element_b not in self._column_of_element:
            raise KeyError(element_b)
        self._column_of_element[element_a].del_assoc(element_a, element_b)
        self._column_of_element[element_b].del_assoc(element_b, element_a)


class BijectiveMap:
    def __init__(self):
        self.forward_map = {}
        self.backward_map = {}

    def __setitem__(self, left_item, right_item):
        self.forward_map[left_item] = right_item
        self.backward_map[right_item] = left_item

    def __getitem__(self, left_item):
        return self.forward_map[left_item]

    def get(self, left_item):
        return self.forward_map[left_item]

    def getreverse(self, right_item):
        return self.backward_map[right_item]

    def __delitem__(self, left_item):
        right_item = self.forward_map[left_item]
        del self.forward_map[left_item]
        del self.backward_map[right_item]
