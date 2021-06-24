from src.Member import Member
from src.Note import Note
import pickle
import os
import pyttsx3

class HomeAssistant:
    def __init__(self):
        # load data from db
        self.members = []
        self.notes = []
        self.loadMembers()
        self.voice = pyttsx3.init()

    def start(self):
        # start camera:Gabriel

        while True:
            if self.detectPresence():
                member = self.recognizeMember()
                if member == None:
                    self.registerMember()
                else:
                    self.say(f"Hello, {member.name}")
                    notes = self.getNotesTo(member)
                    if len(notes) == 0:
                        self.say(f"There are no notes left for you")
                    else:
                        self.say(f"I have found {len(notes)} notes for you, do you want to hear them? ")
                        answer = input(f"Write here")
                        if answer == "yes":
                            for note in notes:
                                self.say(f"Note from {note.sender.name}:\n{note.content}")
                                self.removeNote(note)
                    self.say(f"By the way do you want to leave any note? ")
                    answer = input(f"Write here ")
                    if answer == "yes":
                        self.say(f"Who is the recipient of your note? ")
                        to_who = input(f"Write here ")
                        recipient = self.searchMemberNamed(to_who)
                        if recipient == None:
                            self.say(f"Sorry I couldn't find any member named {to_who}")
                        else:
                            self.say(f"What do you want to say to {recipient.name}?")
                            content = input(f"Write here ")
                            self.addNote(member, recipient, content)

                    if len(self.getNotesFrom(member)) > 0:
                        self.say(f"Do you want to edit any note?")
                        answer = input(f"Write here ")
                        if answer == "yes":
                            self.noteInteraction("edit", member)
                        self.say(f"Do you want to remove any note?")
                        answer = input(f"Write here ")
                        if answer == "yes":
                            self.noteInteraction("remove", member)


    def detectPresence(self):
        # Gabriel
        return True

    '''Members'''
    def recognizeMember(self):
        # Gabriel
        self.say(f"Authentication\nWhat is your name? ")
        name = input("Write here ")
        return self.searchMemberNamed(name)

    def registerMember(self):
        self.say(f"Registration\nWhat is your name? ")
        name = input("Write here ")
        # Gabriel: take pictures
        pictures = None
        newMember = Member(name, pictures)
        self.members.append(newMember)
        self.storeMembers()

    def storeMembers(self):
        members_dict = {}
        for member in self.members:
            members_dict[member.name] = member.pictures
        pickle.dump(members_dict, open("../data/members.p", "wb"))
        #pickle.dump(self.members, open("../data/members.p", "wb"))

    def loadMembers(self):
        self.members = []
        if os.path.getsize("../data/members.p") > 0:
            #self.members = pickle.load(open("../data/members.p", "rb"))
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
        #pickle.dump(self.notes, open("../data/notes.p", "wb"))

    def loadNotes(self):
        self.notes = []
        if os.path.getsize("../data/notes.p") > 0:
            #self.notes = pickle.load(open("../data/notes.p", "rb"))
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
        self.say("Do you want to change the content? ")
        answer = input("Write here ")
        if answer == "yes":
            self.say("Write the new content ")
            edit_note.content = input("Write here ")
        self.say("Do you want to change the recipient ")
        answer = input("Write here ")
        if answer == "yes":
            self.say("Tell me the name of the new recipient ")
            to_who = input("Write here ")
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

    def noteInteraction(self, type, member):
        assert type == "edit" or type == "remove"
        self.say(f"Which member is the recipient? ")
        to_who = input("Write here ")
        # check to_who is a member
        recipient = self.searchMemberNamed(to_who)
        if recipient == None:
            self.say(f"Sorry I couldn't find any member with such name")
        else:
            notes_to_who = self.getNotesFromTo(member, recipient)
            self.say(f"I have found {len(notes_to_who)} from you to {recipient.name}")
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
                self.say(f"You need to be more specific. Try typing some words in the note\n")
                words = input("Write here ")
                most_prob_note = self.getMostProbableNote(notes_to_who, words.split())
                self.say(f"Do you want to edit this note? \"{most_prob_note.content}\"")
                answer = input("Write here ")
                if answer == "yes":
                    if type == "edit":
                        self.editNote(most_prob_note)
                    else:
                        self.removeNote(most_prob_note)


    def say(self, text):
        print(text)
        self.voice.say(text)
        self.voice.runAndWait()