import time
import os


class Partlist:
    def __init__(self, partlist: dict = None):
        if partlist is not None:
            self.partlist = partlist
        else:
            self.partlist = {}

    def add_part(self, p_id: str, amount: int = 1):
        if p_id in self.partlist:
            self.partlist[p_id] += amount
        else:
            self.partlist[p_id] = amount

    def add_part_by_line(self, line: str):
        parameters = line.strip("\n").split(" ")
        colour = parameters[1]
        name = " ".join(parameters[14:])
        self.add_part(f"{colour}:{name}")

    def get_total_part_count(self) -> int:
        count = 0
        for part in self.partlist:
            count += self.partlist[part]
        return count

    def generate_ldraw_model(self, filename, col_distance=165, row_distance=165, height_distance=35):
        header = [
            f"0 FILE {filename}\n",
            "0 Untitled Model\n",
            f"0 Name:  {filename}\n",
            "0 Author: \n",
            "0 CustomBrick\n",
            "0 FlexibleBrickControlPointUnitLength -1\n",
            f"0 NumOfBricks:  {self.get_total_part_count()}\n"
        ]
        content = []
        rows = {}
        columns = {}
        part_ids = list(self.partlist.keys())

        def part_id_to_partnumber(part_id: str):
            name = part_id.split(":")[1].split(".dat")[0]
            digits = []
            post_chars = False
            for char in name:
                if not char.isdigit() and post_chars:
                    break
                if char.isdigit():
                    post_chars = True
                    digits.append(char)
            if len(digits) > 0:
                return int("".join(digits))
            else:
                return -1

        col_count = 0
        part_ids.sort(key=part_id_to_partnumber)
        for part_id in part_ids:
            partname = part_id.split(":")[1]
            if partname not in columns:
                columns[partname] = col_count
                col_count += 1

        def colour_id_to_number(part_colour: str):
            colour_id = part_colour.split(":")[0]
            if colour_id.isdigit():
                return int(colour_id)
            else:
                return -1

        row_count = 0
        part_ids.sort(key=colour_id_to_number)
        for part_id in part_ids:
            colour = part_id.split(":")[0]
            if colour not in rows:
                rows[colour] = row_count
                row_count += 1

        for part in self.partlist:
            colour, partname = part.split(":")
            column = columns[partname]
            row = rows[colour]
            for i in range(self.partlist[part]):
                new_line = f"1 {colour} {column * col_distance} {-i * height_distance} {row * row_distance} 1 0 0 0 1 0 0 0 1 {partname}\n"
                content.append(new_line)

        return header + content + ["0 NOFILE\n"]

    def save_as_ldraw_file(self, filepath, col_distance=165, row_distance=165, height_distance=35):
        filename = os.path.basename(filepath)
        lines = self.generate_ldraw_model(filename, col_distance, row_distance, height_distance)
        with open(filepath, "w", encoding="utf-8") as file:
            file.writelines(lines)

    def __str__(self):
        return str(self.partlist)

    def __repr__(self):
        return f"Parlist -> Unique:{len(self.partlist)}, Total: {self.get_total_part_count()}"

    def __add__(self, other):
        if not isinstance(other, Partlist):
            raise ValueError
        sum_list = Partlist(other.partlist.copy())
        for part in self.partlist:
            sum_list.add_part(part, self.partlist[part])
        return sum_list

    def __mul__(self, other):
        prod_list = Partlist(self.partlist.copy())
        if not isinstance(other, int):
            raise ValueError
        for part in prod_list.partlist:
            prod_list.partlist[part] *= other
        return prod_list


class LDrawFile:
    def __init__(self, content: list):
        self.header = []
        self.filename = content[0].strip("\n")[7:]
        self.modelname = content[1].strip("\n")[2:]
        self.parts = Partlist()
        self.submodels = {}
        self.content = []
        header_complete = False
        for line in content:
            if line.startswith("1"):
                header_complete = True
            if line.startswith("0 NumOfBricks"):
                pass
            elif not header_complete:
                self.header.append(line)
            elif line.startswith("1"):
                self.content.append(line)
                if line.endswith(".dat\n"):
                    self.parts.add_part_by_line(line)
                else:
                    submodel_id = " ".join(line.strip("\n").split(" ")[14:])
                    if submodel_id in self.submodels:
                        self.submodels[submodel_id][1] += 1
                    else:
                        self.submodels[submodel_id] = [None, 1]

    def link_submodel(self, submodel):
        sub_id = submodel.filename.lower()
        self.submodels[sub_id][0] = submodel

    def get_total_partlist(self) -> Partlist:
        total_list = Partlist(self.parts.partlist.copy())
        for sub_id in self.submodels:
            total_list += self.submodels[sub_id][0].get_total_partlist() * self.submodels[sub_id][1]
        return total_list

    def get_ldraw_lines(self):
        return self.header + self.content + ["0 NOFILE\n"]

    def __eq__(self, other):
        if not isinstance(other, LDrawFile):
            raise ValueError
        self.content.sort()
        other.content.sort()
        if self.filename != other.filename:
            return False
        if len(self.content) != len(other.content):
            return False
        for index, line in enumerate(self.content):
            if line != other.content[index]:
                return False
        return True


class LdrawFileTree:
    def __init__(self, filepath: str):
        self.filetree = {}
        with open(filepath, "r", encoding="utf-8") as file:
            submodel_content = []
            for line in file:
                submodel_content.append(line)
                if line.startswith("0 NOFILE"):
                    if len(submodel_content) > 0:
                        submodel = LDrawFile(submodel_content)
                        self.filetree[submodel.filename.lower()] = submodel
                        submodel_content = []
        for fileid in self.filetree:
            file: LDrawFile = self.filetree[fileid]
            for submodel in file.submodels:
                file.link_submodel(self.filetree[submodel])


def get_difference_model(model_a: LdrawFileTree, model_b: LdrawFileTree):
    difference_model = {}
    common_model = {}
    for file_id in model_a.filetree:
        diff_file = LDrawFile(model_a.filetree[file_id].header)
        comm_file = LDrawFile(model_a.filetree[file_id].header)
        if file_id in model_b.filetree:
            file_a = model_a.filetree[file_id]
            file_b = model_b.filetree[file_id]
            for line in file_a.content:
                if line in file_b.content:
                    if not line.endswith(".dat\n"):
                        sub_id = " ".join(line.strip("\n").split(" ")[14:])
                        if model_a.filetree[sub_id] != model_b.filetree[sub_id]:
                            diff_file.content.append(line)
                    comm_file.content.append(line)
                else:
                    if line.endswith(".dat\n"):
                        diff_file.content.append(line)
                    else:
                        sub_id = " ".join(line.strip("\n").split(" ")[14:])
                        if sub_id not in model_b.filetree or model_a.filetree[sub_id] == model_b.filetree[sub_id]:
                            diff_file.content.append(line)
                        else:
                            new_sub_header = model_a.filetree[sub_id].header.copy()
                            time_id = hex(time.time_ns())[2:]
                            new_sub_id = f"{model_a.filetree[sub_id].filename.lower()}_{time_id}"
                            #Case ID already used in model
                            while new_sub_id in model_a.filetree:
                                time_id = hex(time.time_ns())[2:]
                                new_sub_id = f"{model_a.filetree[sub_id].filename.lower()}_{time_id}"

                            new_sub_header[0] = new_sub_header[0].replace("\n", f"_{time_id}\n")
                            new_sub_header[1] = new_sub_header[1].replace("\n", f"_{time_id}\n")
                            new_sub_header[2] = new_sub_header[2].replace("\n", f"_{time_id}\n")
                            new_sub = LDrawFile(new_sub_header+model_a.filetree[sub_id].content)
                            difference_model[new_sub_id] = new_sub
                            new_line = line.replace("\n", f"_{time_id}\n")
                            diff_file.content.append(new_line)
            common_model[file_id] = comm_file
            if len(diff_file.content) > 0:
                difference_model[file_id] = diff_file
            else:
                diff_file.content = file_a.content
                difference_model[file_id] = diff_file
        else:
            diff_file.content = model_a.filetree[file_id].content
            difference_model[file_id] = diff_file
    return difference_model, common_model


def save_model(model: dict, filepath):
    with open(filepath, "w", encoding="utf-8") as file:
        for ld_file in model.values():
            file.writelines(ld_file.get_ldraw_lines())


def get_part_difference(partlist_a: Partlist, partlist_b: Partlist):
    diff_list = Partlist()
    comm_list = Partlist()

    for part in partlist_a.partlist:
        if part in partlist_b.partlist:
            if partlist_a.partlist[part] <= partlist_b.partlist[part]:
                comm_list.partlist[part] = partlist_a.partlist[part]
            elif partlist_a.partlist[part] > partlist_b.partlist[part]:
                comm_list.partlist[part] = partlist_b.partlist[part]
                diff = partlist_a.partlist[part] - partlist_b.partlist[part]
                diff_list.partlist[part] = diff
        else:
            diff_list.partlist[part] = partlist_a.partlist[part]
    return diff_list, comm_list


if __name__ == "__main__":
    testfile_a = "Path\\To\\Your\\Testfile_A.ldr"
    testfile_b = "Path\\To\\Your\\Testfile_B.ldr"

    file_tree_a = LdrawFileTree(testfile_a)
    file_tree_b = LdrawFileTree(testfile_b)
    part_diff, part_comm = get_part_difference(
        list(file_tree_a.filetree.values())[0].get_total_partlist(),
        list(file_tree_b.filetree.values())[0].get_total_partlist())

    for line in part_comm.generate_ldraw_model("diff_partlist", 85, 25, 25):
        print(line.strip("\n"))

    file_diff, file_comm = get_difference_model(file_tree_b, file_tree_a)

    for sub in file_diff.values():
        sub.content.sort()
        for lline in sub.get_ldraw_lines():
            print(lline.strip("\n"))

    total_a = list(file_tree_a.filetree.values())[0].get_total_partlist()
    print(total_a)
