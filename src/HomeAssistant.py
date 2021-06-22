from src.Member import Member
from src.Note import Note
import pickle
import os

class HomeAssistant:
    def __init__(self):
        # load data from db
        self.members = self.loadMembers()
        print("Members: ")
        for member in self.members:
            print(f"{member.name}")
        self.notes = self.loadNotes()
        print(len(self.notes))
        print("notes: ")
        for note in self.notes:
            print(f"Note from {note.sender.name} to {note.recipient.name}:\n{note.content}")


    def start(self):
        # start camera:Gabriel

        while True:
            if self.detectPresence():
                member = self.recognizeMember()
                if member == None:
                    self.registerMember()
                else:
                    print(f"Hello, {member.name}")
                    notes = self.getNotesTo(member)
                    if len(notes) == 0:
                        print(f"There are no notes left for you")
                    else:
                        answer = input(f"I have found {len(notes)} notes for you, do you want to here them? ")
                        if answer == "yes":
                            for note in notes:
                                print(f"Note from {note.sender.name}:\n{note.content}")
                                self.removeNote(note)

                    answer = input(f"By the way do you want to leave any note? ")
                    if answer == "yes":
                        to_who = input(f"Who is the recipient of your note? ")
                        recipient = self.searchMemberNamed(to_who)
                        if recipient == None:
                            print(f"Sorry I couldn't find any member named {to_who}")
                        else:
                            content = input(f"What do you want to say to {recipient.name}?")
                            self.addNote(member, recipient, content)

                    if len(self.getNotesFrom(member)) > 0:
                        answer = input(f"Do you want to edit any note?")
                        if answer == "yes":
                            self.noteInteraction("edit", member)
                        answer = input(f"Do you want to remove any note?")
                        if answer == "yes":
                            self.noteInteraction("remove", member)


    def detectPresence(self):
        # Gabriel
        return True

    '''Members'''
    def recognizeMember(self):
        # Gabriel
        name = input(f"What is your name? ")
        return self.searchMemberNamed(name)

    def registerMember(self):

        name = input(f"Registration\nWhat is your name? ")
        # Gabriel: take pictures
        pictures = None
        newMember = Member(name, pictures)
        self.members.append(newMember)
        self.storeMembers()

    def storeMembers(self):
        pickle.dump(self.members, open("../data/members.p", "wb"))

    def loadMembers(self):
        if os.path.getsize("../data/members.p") > 0:
            return pickle.load(open("../data/members.p", "rb"))
        return []

    def searchMemberNamed(self, name):
        for member in self.members:
            if member.name == name:
                return member
        return None


    '''Notes'''
    def storeNotes(self):
        # esempio: {"Antonio": [NoteObj, NoteObj],, "Fabio": [NoteObj, NoteObj]}
        print(len(self.notes))
        pickle.dump(self.notes, open("../data/notes.p", "wb"))

    def loadNotes(self):
        if os.path.getsize("../data/notes.p") > 0:
            return pickle.load(open("../data/notes.p", "rb"))
        return []

    def addNote(self, sender, receipient, content):
        newNote = Note(sender, receipient, content)
        self.notes.append(newNote)
        self.storeNotes()

    def removeNote(self, note):
        self.notes.remove(note)
        self.storeNotes()

    def editNote(self, edit_note):
        answer = input("do you want to change the content")
        if answer == "yes":
            edit_note.content = input("Write the new content")
        answer = input("do you want to change the sender")
        if answer == "yes":
            to_who = input("Tell me the name of the new recipient")
            recipient = self.searchMemberNamed(to_who)
            edit_note.recipient = recipient
        self.storeNotes()

    def getNotesTo(self, recipient):
        notes = []
        print([f"{n.sender.name}-{n.recipient.name}:{n.content}" for n in self.notes])
        for note in self.notes:
            if note.recipient == recipient:
                notes.append(note)
        return notes

    def getNotesFrom(self, sender):
        notes = []
        print([f"{n.sender.name}-{n.recipient.name}:{n.content}" for n in self.notes])
        for note in self.notes:
            if note.sender == sender:
                notes.append(sender)
        return notes

    def getNotesFromTo(self, sender, recipient):
        notes = []
        print([f"{n.sender.name}-{n.recipient.name}:{n.content}" for n in self.notes])
        for note in self.notes:
            if note.sender == sender and note.recipient == recipient:
                notes.append(note)
        return notes



    def getMostProbableNote(self, notes_to_who, words):
        max_note = notes_to_who[0]
        max = len([word for word in words if word in max_note.content])
        for note in notes_to_who:
            if len([word for word in words if word in note.content]) > max:
                max_note = note
                max = len([word for word in words if word in note.content])
        return max_note

    def noteInteraction(self, type, member):
        assert type == "edit" or type == "delete"
        to_who = input(f"Which member is the recipient ?")
        # check to_who is a member
        if self.searchMemberNamed(to_who) == None:
            print(f"Sorry I couldn't find any member with such name")
        else:
            notes_to_who = self.getNotesFromTo(member, to_who)
            print([f"{n.sender.name}-{n.recipient.name}:{n.content}" for n in notes_to_who])
            print(f"I have found {len(notes_to_who)} from you to {to_who}")
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
                words = input(f"You need to be more specific. Try typing some words in the note")
                most_prob_note = self.getMostProbableNote(notes_to_who, words.split())
                answer = input(f"Do you want to edit this note: {most_prob_note.content}")
                if answer == "yes":
                    if type == "edit":
                        self.editNote(most_prob_note)
                    else:
                        self.removeNote(most_prob_note)