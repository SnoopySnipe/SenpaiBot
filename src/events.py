import discord


class EventList:
    def __init__(self):
        self.event_list = []

    def add_event(self, event_name, event_start_time):
        new_event = Event(event_name, event_start_time)
        self.event_list.append(new_event)

        return (len(self.event_list) - 1, new_event)

    def remove_event(self, eventIndex):
        if (eventIndex < len(self.event_list)):
            self.event_list.pop(eventIndex)
            return "Removed event with event number {}".format(eventIndex)
        else:
            return "Invalid event number"

    def list_events(self):
        return str(self)

    def view_attendees(self, eventIndex):
        if (eventIndex < len(self.event_list)):
            return self.event_list[eventIndex].view_attendees()

    def add_attendee(self, eventIndex, name):
        if (eventIndex < len(self.event_list)):
            return self.event_list[eventIndex].add_attendee(name)
        else:
            return "Invalid event number"

    def remove_attendee(self, eventIndex, name):
        if (eventIndex < len(self.event_list)):
            return self.event_list[eventIndex].remove_attendee(name)
        else:
            return "Invalid event number"

    def to_embed_msg_list(self):
        msgs = []
        for i, event in enumerate(self.event_list):
            msg = event.to_embed_msg(i)
            msgs.append(msg)

        return msgs

    def __str__(self) -> str:
        res = ""
        for (i, event) in enumerate(self.event_list):
            res += "#{}. {}  (Date: {})".format(i, event.event_name, event.event_start_time)
            attendees = event.view_attendees()
            res += "\t `{}`\n".format(" | ".join(str(e) for e in attendees))
        return res

class Event:
    def __init__(self, event_name: str, event_start_time: str):
        self.event_name = event_name
        self.event_start_time = event_start_time
        self.attendees = []

    def view_attendees(self):
        return self.attendees

    def add_attendee(self, name):
        if (name in self.attendees):
            return "Already added to event"

        self.attendees.append(name)
        return "Added {} to {}".format(name, self.event_name)

    def remove_attendee(self, name):
        if (name not in self.attendees):
            return "Already removed from event"

        self.attendees.remove(name)
        return "Removed {} from {}".format(name, self.event_name)

    def to_embed_msg(self, index):
        title = "Event #{}: {}".format(index, self.event_name)

        date_msg = "Date: " + self.event_start_time
        going_attendees = 'Going:\n' + '\n'.join(
                '{}. {}'.format(i+1, str(attendee))
                for i, attendee in enumerate(self.attendees))

        final_description = '{}\n\n{}'.format(date_msg, going_attendees)

        embed_msg = discord.Embed(title=title,
                            description=final_description,
                            color=0xff93ac)
        return embed_msg
