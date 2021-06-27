from src.Member import Member
from src.Note import Note
from src.CommunicationHandler import CommunicationHandler
import pickle
import os

class HomeAssistant:
    def __init__(self, blind=False, deaf=False, dumb=False):
        # load data from db
        self.members = []
        self.notes = []
        self.loadMembers()
        self.communicator = CommunicationHandler(blind, deaf, dumb)

    def start(self):
        # start camera:Gabriel
        while True:
            if self.detectPresence():
                member = self.recognizeMember()
                if member == None:
                    self.nonMemberInteraction()
                else:
                    self.memberInteraction(member)

    '''Interactions'''
    def nonMemberInteraction(self):
        self.communicator.say("Seems your not part of this Clan, do you want to register?")
        answer = self.communicator.listen()
        if "yes" in answer.split():
            self.registerMember()

    def memberInteraction(self, member):
        while True:
            self.communicator.say(f"Hello, {member.name[0].capitalize() + member.name[1:]}")
            if not self.isMemberStillHere(member): break
            notes = self.getNotesTo(member)
            if len(notes) == 0:
                self.communicator.say(f"There are no notes left for you")
            else:
                self.communicator.say(f"I have found {len(notes)} notes for you, do you want to hear them? ")
                answer = self.communicator.listen()
                if "yes" in answer.split(): self.tellNotes(notes)
            self.communicator.say(f"What can I do for you, {member.name[0].capitalize() + member.name[1:]}?")
            answer = self.communicator.listen()
            action = self.getMostProbableAction(answer)
            self.communicator.say(f"So, do you want to {action} a note?")
            answer = self.communicator.listen()
            if "yes" in answer:
                if action == "leave":
                    self.leaveNoteInteraction(member)
                else:
                    self.noteInteraction(action, member)

    def leaveNoteInteraction(self, member):
        self.communicator.say(f"Who is the recipient of your note? ")
        to_who = self.communicator.listen()
        recipient = self.searchMemberNamed(to_who)
        if recipient == None:
            self.communicator.say(f"Sorry I couldn't find any member named {to_who}")
        else:
            self.communicator.say(f"What do you want to say to {recipient.name}?")
            content = self.communicator.listen()
            self.addNote(member, recipient, content)

    def noteInteraction(self, type, member):
        assert type == "edit" or type == "remove"
        self.communicator.say(f"Which member is the recipient? ")
        to_who = self.communicator.listen()
        # check to_who is a member
        recipient = self.searchMemberNamed(to_who)
        if recipient == None:
            self.communicator.say(f"Sorry I couldn't find any member with such name")
        else:
            notes_to_who = self.getNotesFromTo(member, recipient)
            self.communicator.say(f"I have found {len(notes_to_who)} from you to {recipient.name}")
            if len(notes_to_who) == 0:
                print("ERROR: there are no notes!! ")
                return
            if len(notes_to_who) == 1:
                # there is just one note
                if type == "edit":
                    self.editNote(notes_to_who[0])
                else:
                    self.removeNote(notes_to_who[0])
            else:
                self.communicator.say(f"You need to be more specific. Try typing some words in the note\n")
                words = self.communicator.listen()
                most_prob_note = self.getMostProbableNote(notes_to_who, words.split())
                self.communicator.say(f"Do you want to edit this note? \"{most_prob_note.content}\"")
                answer = self.communicator.listen()
                if answer == "yes":
                    if type == "edit":
                        self.editNote(most_prob_note)
                    else:
                        self.removeNote(most_prob_note)
    def tellNotes(self, notes):
        for note in notes:
            self.communicator.say(f"Note from {note.sender.name}:\n{note.content}")
            self.removeNote(note)

    def detectPresence(self):
        # Gabriel
        return True

    def isMemberStillHere(self, member):
        return self.detectPresence() #and (self.recognizeMember() == member)

    '''Members'''

    def recognizeMember(self):
        # Gabriel
        self.communicator.say(f"Authentication\nWhat is your name? ")
        name = self.communicator.listen()
        return self.searchMemberNamed(name)

    def registerMember(self):
        self.communicator.say(f"Registration\nWhat is your name? ")
        name = self.communicator.listen()
        # Gabriel: take pictures
        pictures = None
        newMember = Member(name.lower(), pictures)
        self.members.append(newMember)
        self.storeMembers()
        self.communicator.say("Registration completed")

    def storeMembers(self):
        members_dict = {}
        for member in self.members:
            members_dict[member.name] = member.pictures
        pickle.dump(members_dict, open("../data/members.p", "wb"))

    def loadMembers(self):
        self.members = []
        if os.path.getsize("../data/members.p") > 0:
            members_dict = pickle.load(open("../data/members.p", "rb"))
            for name in members_dict:
                self.members += [Member(name, members_dict[name])]
        self.loadNotes()

    def searchMemberNamed(self, name):
        for member in self.members:
            if member.name == name:
                return member
        return None

    '''Notes'''
    def storeNotes(self):
        # esempio: {"Antonio": [NoteObj, NoteObj],, "Fabio": [NoteObj, NoteObj]}
        notes_dict = {}
        for note in self.notes:
            if note.sender.name in notes_dict.keys():
                notes_dict[note.recipient.name] += [{'sender': note.sender.name, 'content': note.content}]
            else:
                notes_dict[note.recipient.name] = [{'sender': note.sender.name, 'content': note.content}]

        pickle.dump(notes_dict, open("../data/notes.p", "wb"))

    def loadNotes(self):
        self.notes = []
        if os.path.getsize("../data/notes.p") > 0:
            notes_dict = pickle.load(open("../data/notes.p", "rb"))
            for member in self.members:
                if member.name in notes_dict.keys():
                    notes_to_member = notes_dict[member.name]
                    for note in notes_to_member:
                        self.notes += [Note(self.searchMemberNamed(note['sender']), member, note['content'])]

    def addNote(self, sender, receipient, content):
        newNote = Note(sender, receipient, content)
        self.notes.append(newNote)
        self.storeNotes()

    def removeNote(self, note):
        self.notes.remove(note)
        self.storeNotes()

    def editNote(self, edit_note):
        self.communicator.say("Do you want to change the content? ")
        answer = self.communicator.listen()
        if answer == "yes":
            self.communicator.say("Write the new content ")
            edit_note.content = self.communicator.listen()
        self.communicator.say("Do you want to change the recipient ")
        answer = self.communicator.listen()
        if answer == "yes":
            self.communicator.say("Tell me the name of the new recipient ")
            to_who = self.communicator.listen()
            recipient = self.searchMemberNamed(to_who)
            edit_note.recipient = recipient
        self.storeNotes()

    def getNotesTo(self, recipient):
        notes = []
        for note in self.notes:
            if note.recipient == recipient:
                notes.append(note)
        return notes

    def getNotesFrom(self, sender):
        notes = []
        for note in self.notes:
            if note.sender == sender:
                notes.append(sender)
        return notes

    def getNotesFromTo(self, sender, recipient):
        notes = []
        for note in self.notes:
            if note.sender == sender and note.recipient == recipient:
                notes += [note]
        return notes

    def getMostProbableNote(self, notes_to_who, words):
        max_note = notes_to_who[0]
        max = len([word for word in words if word in max_note.content])
        for note in notes_to_who:
            if len([word for word in words if word in note.content]) > max:
                max_note = note
                max = len([word for word in words if word in note.content])
        return max_note

    def getMostProbableAction(self, text):
        words = text.split()
        prob = {"edit": len([w for w in words if w in ["edit", "modity", "change"]])/len(words),
                "remove": len([w for w in words if w in ["delete", "remove", "forget"]])/len(words),
                "leave": len([w for w in words if w in ["new", "leave", "say", "tell"]])/len(words)}
        return max(prob, key=lambda key: prob[key])