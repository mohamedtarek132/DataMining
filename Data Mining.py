import pandas as pd
import math
import copy
import pyfiglet

# from anytree import Node, RenderTree


class Node:
    item: str
    count: int
    adjacent: dict

    def __init__(self, item, count, adjacent):
        self.item = item
        self.count = count
        self.adjacent = adjacent


def show_tree(root: Node, level):
    print(" " * (level * 5), "└──", root.item, ":", root.count)
    for node in root.adjacent.values():
        show_tree(node, level + 1)


def show_tree1(root: Node, branch: str, is_last: bool):
    print(f"{branch}└── {root.item}:{root.count}")

    counter = 0
    number_of_spaces = 4

    if len(branch) > (number_of_spaces - 1):
        branch = branch[:-(number_of_spaces - 1)]
    else:
        branch = ""

    if not is_last:
        branch = branch + " " * (number_of_spaces - 1) + "|"
    else:
        branch = branch + " " * number_of_spaces

    length = len(root.adjacent)
    branch = branch + " " * number_of_spaces

    for node in root.adjacent.values():
        if counter == (length - 1):
            is_current_element_last = True
        else:
            is_current_element_last = False

        counter += 1
        show_tree1(node, branch, is_current_element_last)


def get_frequent(supports: dict, data: list, supp_cnt, frequent: list):
    # calculate supports
    for lst in data:
        for item in lst:
            if item in supports.keys():
                supports[item] += 1
            else:
                supports[item] = 1

    for item in supports.copy():
        if supports[item] < supp_cnt:
            del supports[item]
            for lst in data:
                if item in lst:
                    lst.remove(item)
        else:
            frequent.append(item)


def build_tree(root, data, frequent):
    previous = Node(None, 0, dict())

    for lst in data:
        previous = root
        for item in lst:
            if item in frequent:
                if item in previous.adjacent.keys():
                    previous.adjacent[item].count += 1
                else:
                    previous.adjacent[item] = Node(item, 1, dict())
                previous = previous.adjacent[item]


def sort_data(data, frequent, supports) -> list:
    for lst in range(0, len(data)):
        data[lst] = sorted(data[lst], key=lambda x: supports[x], reverse=True)
    frequent = sorted(frequent, key=lambda x: supports[x])
    return frequent


def DFS(item: str, stack: list, visited: list, predecessors: dict, track: list) -> list:
    if len(stack) == 0:
        return track
    current_node = stack.pop()

    if current_node not in visited:
        visited.append(current_node)
    else:
        return track

    for key in current_node.adjacent:

        if key == item:
            x = []
            name = current_node.item

            while name in predecessors.keys():
                x.append(name)
                name = predecessors[name]

            track.append(tuple([x, current_node.adjacent[key].count]))

            continue

        predecessors[key] = current_node.item
        stack.append(current_node.adjacent[key])

    return DFS(item, stack, visited, predecessors, track)


def get_conditional_pattern_base(conditional_pattern_base, root, frequent):
    for item in frequent:
        root_copy = Node(None, 0, copy.deepcopy(root.adjacent))
        stack = [root_copy]
        conditional_pattern_base[item] = DFS(item, stack, [], {}, [])


def get_frequent_CPB(supports: dict, data: list, supp_cnt, frequent: list):
    # list(tuple(list(), int))
    # calculate supports
    for tple in data:
        lst = tple[0]
        count = tple[1]
        for item in lst:
            if item in supports.keys():
                supports[item] += count
            else:
                supports[item] = count

    for lst in supports.copy():
        if supports[lst] < supp_cnt:
            del supports[lst]
            for tple in data:
                if lst in tple:
                    tple.remove(lst)
        else:
            frequent.append(lst)


def get_support(item: list, data: list):
    support = 0
    # print(data)
    for tple in data:
        lst = tple[0]
        count = tple[1]
        # print("oops", lst)
        # print(item)
        if type(lst) is list:
            if set(item).issubset(lst):
                support += count
        elif type(lst) is str:
            # print("yay")
            if len(item) == 1 and item[0] == lst:
                support += count
                break
    return support

def get_support2(item: list, data: list):
    support = 0
    # print(data)
    for tple in data:
        lst = tple[0]
        count = tple[1]
        # print("oops", lst)
        # print(item)
        if type(lst) is list:
            if item == lst:
                support += count
                break
        elif type(lst) is str:
            # print("yay")
            if len(item) == 1 and item[0] == lst:
                support += count
                break
    return support


def get_frequent_item_sets(base_item, item: list, conditional_tree: dict, frequent_item_sets: list, data):
    for key in conditional_tree.keys():
        if key in item:
            continue
        new_item = [key, *item]
        new_item = sorted(new_item)

        temp = [key, *item]
        if base_item in temp:
            temp.remove(base_item)
        support = get_support(temp, data)
        # support = 0
        for i in frequent_item_sets:
            if i[0] == new_item:
                break
        else:
            frequent_item_sets.append(tuple([new_item, support]))
            get_frequent_item_sets(base_item, new_item, conditional_tree, frequent_item_sets, data)


def generate_association_rule(item, item_set, association_rules, temp):
    for key in item_set:
        if key in item:
            continue
        new_item = [key, *item]
        new_item = sorted(new_item)
        # support = 0
        difference = set(item_set).difference(set(new_item))

        if tuple([new_item, difference]) not in association_rules:
            if len(difference) > 0:
                print(*new_item, "->", *difference)
                association_rules.append(tuple([new_item, difference]))
                temp.append(tuple([new_item, difference]))
            generate_association_rule(new_item, item_set, association_rules, temp)


def generate_association_rules(frequent_item_sets, association_rules):
    item_association_rules = list()
    for item in frequent_item_sets:
        # print(item)
        if type(item[0]) is list:
            temp = list()
            generate_association_rule([], item[0], association_rules, temp)
            item_association_rules += temp
    return item_association_rules


def generate_strong_rules(item_association_rules, frequent_item_set, confidence):
    strong_rules = list()
    for item in item_association_rules:
        all_items = item[0] + list(item[1])
        all_items = sorted(all_items)

        # print(all_items)
        # print("i am here", conditional_pattern_base)
        intersection = get_support2(all_items, frequent_item_set)
        x = item[0]
        x = sorted(item[0])

        x = get_support2(x, frequent_item_set)

        if x > 0 and (intersection/x) >= confidence:
            strong_rules.append(item)
    return strong_rules


def generate_lift(item_association_rules, frequent_item_set, total_count):
    lift = list()
    for item in item_association_rules:
        all_items = item[0] + list(item[1])
        all_items = sorted(all_items)
        intersection = get_support2(all_items, frequent_item_set)

        x = sorted(item[0])
        x = get_support2(x, frequent_item_set)

        y = sorted(item[1])
        y = get_support2(y, frequent_item_set)
        if x * y > 0:
            temp = ((intersection * total_count)/(x * y))
        else:
            temp = 0
        relation = "dependent"
        correlation = "positive"
        if temp < 1:
            correlation = "negative"
        elif temp == 1:
            correlation = "no relation"
            relation = "independent"
        lift.append(tuple([item, temp, relation, correlation]))
    return lift


def fp_growth(data, supp, conf):
    supports = dict()
    frequent = list()
    frequent_item_sets = list()

    supp_cnt = math.ceil(supp * len(data))

    get_frequent(supports, data, supp_cnt, frequent)

    frequent = sort_data(data, frequent, supports)

    frequent_item_sets += (supports.items())
    # print(frequent_item_sets)
    # print("The following is data:\n", data)
    # print("The following is frequent:\n", frequent)
    # print("The following is supports:\n", supports)

    root = Node(None, 0, dict())
    build_tree(root, data, frequent)
    # show_Tree(root, 0)
    print("\nFP Growth Tree\n")
    show_tree1(root, "", True)

    conditional_pattern_base = dict()
    get_conditional_pattern_base(conditional_pattern_base, root, frequent)
    association_rules = list()
    strong_rules = list()
    for item in conditional_pattern_base.keys():
        conditional_pattern_base_support = dict()
        conditional_pattern_base_frequent = list()

        get_frequent_CPB(conditional_pattern_base_support, conditional_pattern_base[item], supp_cnt, conditional_pattern_base_frequent)

        frequent_item_set = list(supports.items())

        get_frequent_item_sets(item, item, conditional_pattern_base_support, frequent_item_set, conditional_pattern_base[item])

        frequent_item_sets += [i for i in frequent_item_set if i not in list(supports.items())]


    print("\nAssociation Rules\n")
    generate_association_rules(frequent_item_sets, association_rules)
    # print(*association_rules, sep="\n")
    # item_strong_rules =
    strong_rules = generate_strong_rules(association_rules, frequent_item_sets, conf)
    print("\nStrong Rules\n")
    for rule in strong_rules:
        print(*rule[0], "->", *rule[1])
#    print(*strong_rules, sep="\n")

    lift = generate_lift(association_rules, frequent_item_sets, len(data))

    print("\nLift\n")
    print(*lift, sep="\n")

    print("\nFrequent Item sets\n")
    print(*frequent_item_sets, sep="\n")


def main():
    df = pd.read_excel('Horizontal_Format.xlsx')

    items = list(df.loc[:, "items"])
    data = list()

    for element in items:
        data.append(element.split(','))

    for lst in range(0, len(data)):
        data[lst] = list(set(data[lst]))
    ascii_art = pyfiglet.figlet_format("FP-Growth")
    print(ascii_art)
    support = float(input("support: "))
    confidence = float(input("confidence: "))
    fp_growth(data, support, confidence)


if __name__ == "__main__":
    main()
