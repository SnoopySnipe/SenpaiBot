class Event_List:
    def __init__(self):
        self.event_list = []
    def add_event(self, event_name, event_start_time):
        self.event_list.append(Event(event_name, event_start_time))
        return "Added event: " + event_name + " with date: " + event_start_time 
    def list_events(self):
        res = ""
        for i in range(len(self.event_list)):
            res += "#" + str(i) + ". " + self.event_list[i].event_name + "  (Date: " + self.event_list[i].event_start_time + ")" + "\n"
            attendees = self.view_attendees(i)
            res += "\t `" + " | ".join(str(e) for e in attendees) + " `\n"
        return res
    def view_attendees(self, eventIndex):
        if(eventIndex < len(self.event_list)):
            return self.event_list[eventIndex].view_attendees()
    def add_attendee(self, eventIndex, name):
        if(eventIndex < len(self.event_list)):
            return self.event_list[eventIndex].add_attendee(name)
    def remove_attendee(self, eventIndex, name):
        if(eventIndex < len(self.event_list)):
            return self.event_list[eventIndex].remove_attendee(name)
class Event:
    def __init__(self, event_name, event_start_time):
        self.event_name = event_name
        self.event_start_time = event_start_time
        self.attendees = []
    def view_attendees(self):
        return self.attendees
    def add_attendee(self, name):
        if(name not in self.attendees):
            self.attendees.append(name)
            return "Added to " + self.event_name
        else:
            return "Already added to event"
    def remove_attendee(self, name):
        if(name in self.attendees):
            self.attendees.remove(name)
            return "Removed from " + self.event_name
        else:
            return "Already removed from event"
