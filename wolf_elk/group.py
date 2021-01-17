from collections import defaultdict
import uuid


class Groups():

    def __init__(self):
        self.groups = defaultdict(Group)
    
    def add(self, group):
        self.groups[group.group_id] = group

    def get(self, group_id):
        return self.groups.pop(group_id)

    def remove(self, group):
        self.groups.pop(group.group_id)


class Group():
    def __init__(self, max_members):
        self.group_id = uuid.uuid4()
        self.members = []
        self.max_members = max_members

    def id(self):
        return self.group_id

    def add(self, member):
        member.group_id = self.group_id
        member.grouped = True
        self.members.append(member)

    def disband(self):
        for member in self.members:
            member.grouped = False
            member.group_id = None

    def remove(self, member):
        self.members.remove(member)
    
    def __len__(self):
        return len(self.members)

