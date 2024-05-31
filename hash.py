class OrderedList:
    def __init__(self):
        self.items = []

    def add(self, item):
        if self.items == []:
            self.items.append(item)
        else:
            for i in range(len(self.items)):
                if item < self.items[i]:
                    self.items.insert(i, item)
                    break
            else:
                self.items.append(item)

    def size(self):
        return len(self.items)

    def search(self, item):
        return self._binary_search_recursive(item, 0, len(self.items) - 1)

    def _binary_search_recursive(self, item, left, right):
        if left > right:
            return False
        mid = (left + right) // 2
        if self.items[mid] == item:
            return True
        elif self.items[mid] > item:
            return self._binary_search_recursive(item, left, mid - 1)
        else:
            return self._binary_search_recursive(item, mid + 1, right)


# Example usage:
if __name__ == "__main__":
    ordered_list = OrderedList()
    sequence = [15, 9, 8, 1, 4, 11, 7, 12, 13, 6, 5, 3, 16, 2, 10, 14]
    for element in sequence:
        ordered_list.add(element)

    print("Ordered list:", ordered_list.items)

    to_find = 17
    if ordered_list.search(to_find):
        print(f"{to_find} found in the ordered list.")
    else:
        print(f"{to_find} not found in the ordered list.")
