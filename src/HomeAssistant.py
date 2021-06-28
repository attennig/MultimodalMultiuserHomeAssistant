from Member import Member
from Note import Note
from CommunicationHandler import CommunicationHandler
import cv2
import face_recognition
import pickle
import os


class HomeAssistant:
    def __init__(self, blind=False, deaf=False, dumb=False):
        # load data from db
        self.members = []
        self.notes = []
        self.load_members()
        self.communicator = CommunicationHandler(blind, deaf, dumb)

    def start(self):
        # start onboard webcam
        video_capture = cv2.VideoCapture(0)
        while True:
            # capture next frame and detect eventual face/s
            _, frame = video_capture.read()
            if self.detect_presence(frame):
                member = self.recognize_member(frame)
                if member is None:
                    self.non_member_interaction(frame)
                else:
                    self.save_frame(frame, member)
                    self.member_interaction(frame, member)

    '''Interactions'''

    def non_member_interaction(self, frame):
        self.communicator.say("Seems you are not part of this Clan, do you want to register?")
        answer = self.communicator.listen()
        if "yes" in answer.split():
            self.register_member(frame)

    def member_interaction(self, frame, member):
        while True:
            self.communicator.say(f"Hello, {member.name[0].capitalize() + member.name[1:]}")
            if not self.is_member_still_here(frame, member):
                break
            notes = self.get_notes_to(member)
            if len(notes) == 0:
                self.communicator.say(f"There are no notes left for you")
            else:
                self.communicator.say(f"I have found {len(notes)} notes for you, do you want to hear them?")
                answer = self.communicator.listen()
                if "yes" in answer.split():
                    self.tell_notes(notes)
            self.communicator.say(f"What can I do for you, {member.name[0].capitalize() + member.name[1:]}?")
            answer = self.communicator.listen()
            action = self.get_most_probable_action(answer)
            self.communicator.say(f"So, do you want to {action} a note?")
            answer = self.communicator.listen()
            if "yes" in answer:
                if action == "leave":
                    self.leave_note_interaction(member)
                else:
                    self.note_interaction(action, member)

    def leave_note_interaction(self, member):
        self.communicator.say(f"Who is the recipient of your note? ")
        to_who = self.communicator.listen()
        recipient = self.search_member_named(to_who)
        if recipient is None:
            self.communicator.say(f"Sorry I couldn't find any member named {to_who}")
        else:
            self.communicator.say(f"What do you want to say to {recipient.name}?")
            content = self.communicator.listen()
            self.add_note(member, recipient, content)

    def note_interaction(self, mode, member):
        assert mode == "edit" or mode == "remove"
        self.communicator.say(f"Which member is the recipient? ")
        to_who = self.communicator.listen()
        # check to_who is a member
        recipient = self.search_member_named(to_who)
        if recipient is None:
            self.communicator.say(f"Sorry I couldn't find any member with such name")
        else:
            notes_to_who = self.get_notes_from_to(member, recipient)
            self.communicator.say(f"I have found {len(notes_to_who)} from you to {recipient.name}")
            if len(notes_to_who) == 0:
                print("ERROR: there are no notes!! ")
                return
            if len(notes_to_who) == 1:
                # there is just one note
                if mode == "edit":
                    self.edit_note(notes_to_who[0])
                else:
                    self.remove_note(notes_to_who[0])
            else:
                self.communicator.say(f"You need to be more specific. Try typing some words in the note\n")
                words = self.communicator.listen()
                most_prob_note = self.get_most_probable_note(notes_to_who, words.split())
                self.communicator.say(f"Do you want to edit this note? \"{most_prob_note.content}\"")
                answer = self.communicator.listen()
                if answer == "yes":
                    if mode == "edit":
                        self.edit_note(most_prob_note)
                    else:
                        self.remove_note(most_prob_note)

    def tell_notes(self, notes):
        for note in notes:
            self.communicator.say(f"Note from {note.sender.name}:\n{note.content}")
            self.remove_note(note)

    def detect_presence(self, frame):
        # load and instantiate haar cascade classifier
        face_cascade = cv2.CascadeClassifier(os.path.join(cv2.data.haarcascades, 'haarcascade_frontalface_default.xml'))
        # convert input frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        # detect faces
        faces = face_cascade.detectMultiScale(gray, minNeighbors=6, minSize=(60, 60), flags=cv2.CASCADE_SCALE_IMAGE)
        return faces is not None

    def is_member_still_here(self, frame, member):
        return self.detect_presence(frame) and (self.recognize_member(frame) == member)

    '''Members'''

    def recognize_member(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # encodings = face_recognition.face_encodings(rgb)
        self.communicator.say(f"Authentication\nWhat is your name?")
        name = self.communicator.listen()
        return self.search_member_named(name)

    def register_member(self, frame):
        self.communicator.say(f"Registration\nWhat is your name?")
        name = self.communicator.listen()
        os.mkdir(os.path.join("..", "data", name.lower()))
        cv2.imwrite(os.path.join("..", "data", name.lower(), "00.jpg"), frame)
        pictures = [frame]
        newMember = Member(name.lower(), pictures)
        self.members.append(newMember)
        self.store_members()
        self.communicator.say("Registration completed")

    def store_members(self):
        members_dict = {}
        for member in self.members:
            members_dict[member.name] = member.pictures
        pickle.dump(members_dict, open(os.path.join("..", "data", "members.pkl", "wb")))

    def load_members(self):
        self.members = []
        if os.path.getsize(os.path.join("..", "data", "members.pkl")) > 0:
            members_dict = pickle.load(open(os.path.join("..", "data", "members.pkl", "rb")))
            for name in members_dict:
                self.members += [Member(name, members_dict[name])]
        self.load_notes()

    def search_member_named(self, name):
        for member in self.members:
            if member.name == name:
                return member
        return None

    '''Notes'''

    def store_notes(self):
        # esempio: {"Antonio": [NoteObj, NoteObj],, "Fabio": [NoteObj, NoteObj]}
        notes_dict = {}
        for note in self.notes:
            if note.sender.name in notes_dict.keys():
                notes_dict[note.recipient.name] += [{'sender': note.sender.name, 'content': note.content}]
            else:
                notes_dict[note.recipient.name] = [{'sender': note.sender.name, 'content': note.content}]

        pickle.dump(notes_dict, open(os.path.join("..", "data", "notes.pkl", "wb")))

    def load_notes(self):
        self.notes = []
        if os.path.getsize(os.path.join("..", "data", "notes.pkl")) > 0:
            notes_dict = pickle.load(open(os.path.join("..", "data", "notes.pkl", "rb")))
            for member in self.members:
                if member.name in notes_dict.keys():
                    notes_to_member = notes_dict[member.name]
                    for note in notes_to_member:
                        self.notes += [Note(self.search_member_named(note['sender']), member, note['content'])]

    def add_note(self, sender, receipient, content):
        newNote = Note(sender, receipient, content)
        self.notes.append(newNote)
        self.store_notes()

    def remove_note(self, note):
        self.notes.remove(note)
        self.store_notes()

    def edit_note(self, edit_note):
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
            recipient = self.search_member_named(to_who)
            edit_note.recipient = recipient
        self.store_notes()

    def get_notes_to(self, recipient):
        notes = []
        for note in self.notes:
            if note.recipient == recipient:
                notes.append(note)
        return notes

    def get_notes_from(self, sender):
        notes = []
        for note in self.notes:
            if note.sender == sender:
                notes.append(sender)
        return notes

    def get_notes_from_to(self, sender, recipient):
        notes = []
        for note in self.notes:
            if note.sender == sender and note.recipient == recipient:
                notes += [note]
        return notes

    def get_most_probable_note(self, notes_to_who, words):
        max_note = notes_to_who[0]
        top = len([word for word in words if word in max_note.content])
        for note in notes_to_who:
            if len([word for word in words if word in note.content]) > top:
                max_note = note
                top = len([word for word in words if word in note.content])
        return max_note

    def get_most_probable_action(self, text):
        words = text.split()
        prob = {"edit": len([w for w in words if w in ["edit", "modity", "change"]]) / len(words),
                "remove": len([w for w in words if w in ["delete", "remove", "forget"]]) / len(words),
                "leave": len([w for w in words if w in ["new", "leave", "say", "tell"]]) / len(words)}
        return max(prob, key=lambda key: prob[key])

    def save_frame(self, frame, member):
        name = member.get_name()
        pictures = member.get_pictures()
        cv2.imwrite(os.path.join("..", "data", name.lower(), str(len(pictures)) + ".jpg"), frame)
        member.set_pictures(pictures.append(frame))
