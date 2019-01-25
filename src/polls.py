import discord

class Option:
    def __init__(self, name):
        self.name = name
        self.votes = 0
        self.people = []

    def vote(self, name):
        if name in self.people:
            self.people.remove(name)
            self.votes -= 1
        else:
            self.people.append(name)
            self.votes += 1

class Poll:
    def __init__(self, description, options=None):
        self.description = description
        if options:
            for option in options:
                self.options.append(Option(option))
        else:
            self.options = [Option("Yes"), Option("No")]

    def add_option(self, name):
        self.options.append(Option(name))

    def remove_option(self, index):
        if index < len(self.options):
            del self.options[index]
            return "Removed option {}".format(index)
        else:
            return "Option does not exist"

    def vote(self, index, name):
        self.options[index].vote(name)

    def view(self, index):
        title = "Poll #{}: {}".format(index, self.description)
        description = ""
        for i in range(len(self.options)):
            option = self.options[i]
            description = description + "Option #{} - **{} votes**: {}\n".format(i, option.votes, option.name)
            for people in option.people:
                description = description + "\t" + people + "\n"
            else:
                description = description + "\n"

        return discord.Embed(title=title, description=description, color=0xffd700)

class Poll_List:
    def __init__(self):
        self.poll_list = []

    def add_poll(self, description, options=None):
        new_poll = Poll(description, options)
        self.poll_list.append(new_poll)
        return new_poll.view(len(self.poll_list) - 1)

    def remove_poll(self, index):
        if index < len(self.poll_list):
            del self.poll_list[index]
            return "Removed poll {}".format(index)
        else:
            return "Poll does not exist"
