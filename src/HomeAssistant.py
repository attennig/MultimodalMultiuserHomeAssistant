import os
import pickle
from time import sleep

import cv2  # detection
import face_recognition  # recognition

from CommunicationHandler import CommunicationHandler
from Member import Member
from Note import Note


class HomeAssistant:
    def __init__(self, blind=False, deaf=False, mute=False):
        # load data from db
        self.members = []
        self.notes = []
        self.load_members()
        self.communicator = CommunicationHandler(blind, deaf, mute)
        self.camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.detector = cv2.CascadeClassifier(
            os.path.join(cv2.data.haarcascades, 'haarcascade_frontalface_default.xml'))

    def start(self):
        while True:
            # capture next frame and detect eventual face/s
            _, frame = self.camera.read()
            if self.detect_presence(frame):
                # attempt recognition
                member = self.recognize_member(frame)
                if member is None:
                    _, frame = self.camera.read()
                    if self.is_member_still_here(frame):
                        self.non_member_interaction(frame)
                else:
                    self.member_interaction(member)
                    self.save_frame(frame, member)  # saves initial detection frame
                sleep(30)  # avoids performing new interactions immediately after terminating one

    def detect_presence(self, frame):
        # convert input frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        # detect faces
        faces = self.detector.detectMultiScale(gray, minNeighbors=6, minSize=(60, 60), flags=cv2.CASCADE_SCALE_IMAGE)
        return faces is not None

    def recognize_member(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(rgb)
        for encoding in encodings:
            for member in self.members:
                for picture in member.pictures:
                    matches = face_recognition.compare_faces([picture], encoding)
                    if matches:
                        return member
        self.communicator.say(f"Ciao, non ti riconosco. Chi sei?")
        answer = self.communicator.listen().split()
        members = [self.search_member_named(name) for name in answer if self.search_member_named(name) is not None]
        if len(members) > 0:
            return members[0]

    def register_member(self, frame):
        self.communicator.say("Registrazione\n Come ti chiami?")
        name = self.communicator.listen()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb, model="cnn")
        pictures = face_recognition.face_encodings(rgb, boxes)
        newMember = Member(name.lower(), pictures)
        self.members.append(newMember)
        self.store_members()
        self.communicator.say("Registrazione completata")

    def is_member_still_here(self, member):
        _, frame = self.camera.read()
        return self.detect_presence(frame) and self.recognize_member(frame) == member

    '''Interactions'''

    def non_member_interaction(self, frame):
        self.communicator.say("Sembra che tu non faccia parte di questo Clan, vuoi registrarti?")
        answer = self.communicator.listen()
        if "no" in answer.split():
            self.communicator.say("Arrivederci!")
        if "sì" in answer.split():
            self.register_member(frame)

    def member_interaction(self, member):
        said_hi = False
        while True:
            if not said_hi:
                self.communicator.say(f"Ciao, {member.name[0].capitalize() + member.name[1:]}")
                if not self.is_member_still_here(member):
                    return False
                notes = self.get_notes_to(member)
                if len(notes) == 0:
                    self.communicator.say("Non ci sono note per te")
                else:
                    self.communicator.say(f"Ho trovato {len(notes)} note per te, vuoi ascoltarle?")
                    answer = self.communicator.listen()
                    if "sì" in answer.split():
                        self.tell_notes(notes)
                said_hi = True
            self.communicator.say(f"Cosa posso fare per te, {member.name[0].capitalize() + member.name[1:]}?")
            answer = self.communicator.listen()
            action = self.get_most_probable_action(answer)
            if action is None:
                continue
            # recipent = self.get_most_probable_recipent(answer)
            # if recipent
            self.communicator.say(f"Confermi l'azione {action}?")
            answer = self.communicator.listen()
            if "sì" in answer.split():
                if action == "termina":
                    return True
                elif action == "nuova nota":
                    self.leave_note_interaction(member)
                else:
                    self.note_interaction(action, member)

    def leave_note_interaction(self, member):
        # note in breadcast
        self.communicator.say("Per chi è la nota? ")
        to_who = self.communicator.listen()
        if len([word for word in to_who.split() if word in ["tutti", "tutto", "altri"]]) > 0:
            recipients = [recipient for recipient in self.members if recipient != member]
        else:
            recipients = [self.search_member_named(name) for name in to_who.split() if
                          type(self.search_member_named(to_who)) == type(member)]
        if len(recipients) == 0:
            self.communicator.say(f"Mi dispiace non ho trovato nessun membro che corrisponde alla richiesta")
        else:
            self.communicator.say(f"Cosa vuoi dire a {recipients}?")
            content = self.communicator.listen()
            for recipient in recipients:
                self.add_note(member, recipient, content)


    def note_interaction(self, mode, member):
        assert mode == "modifica" or mode == "rimuovi"
        self.communicator.say("Chi è il destinatario? ")
        to_who = self.communicator.listen()
        # check to_who is a member
        recipient = self.search_member_named(to_who)
        if recipient is None:
            self.communicator.say(f"Mi dispiace non ho trovato nessun membro chiamato {recipient}")
        else:
            notes_to_who = self.get_notes_from_to(member, recipient)
            self.communicator.say(f"Ho trovato {len(notes_to_who)} tue note per {recipient.name}")
            if len(notes_to_who) == 0:
                print("ERROR: there are no notes!! ")
                return
            if len(notes_to_who) == 1:
                # there is just one note
                if mode == "modifica":
                    self.edit_note(notes_to_who[0])
                else:
                    self.remove_note(notes_to_who[0])
            else:
                self.communicator.say(f"Puoi darmi dei dattagli sul contenuto della nota? \n")
                words = self.communicator.listen()
                most_prob_note = self.get_most_probable_note(notes_to_who, words.split())
                if mode == "modifica":
                    self.communicator.say(f"Vuoi modificale la seguente nota? \"{most_prob_note.content}\"")
                else:
                    self.communicator.say(f"Vuoi eliminare la seguente nota? \"{most_prob_note.content}\"")
                answer = self.communicator.listen()
                if "sì" in answer.split():
                    if mode == "modifica":
                        self.edit_note(most_prob_note)
                    else:
                        self.remove_note(most_prob_note)

    def tell_notes(self, notes):
        for note in notes:
            self.communicator.say(f"Nota da {note.sender.name}:\n{note.content}")
            self.remove_note(note)

    def get_most_probable_action(self, text):
        # hot words
        # grammatica con diverse alternativa per il verbo con sinonimi, e poi l'ogetto con sinonimi.
        # per ogni azione definire sin verbi e obj
        words = text.split()
        prob = {
            "modifica": len([w for w in words if w in ["modifica", "modificare", "cambia", "cambiare"]]) / len(words),
            "rimuovi": len([w for w in words if
                            w in ["rimuovere", "rimuovi", "cancella", "cancellare", "elimina", "eliminare"]]) / len(
                words),
            "nuova nota": len([w for w in words if w in ["nuova", "lasciare", "dire", "riferire", "lascia"]]) / len(
                words),
            "termina": len([w for w in words if
                            w in ["stop", "termina", "esci", "abbandona", "smetti", "spegni", "chiudi", "uscire",
                                  "chiudere", "abbandonare", "nulla", "niente"]]) / len(
                words)}
        return max(prob, key=lambda key: prob[key]) if max(prob.values()) != 0 else None

    '''Members'''

    def search_member_named(self, name):
        for member in self.members:
            if member.name == name:
                return member
        return None

    '''Notes'''

    def add_note(self, sender, receipient, content):
        newNote = Note(sender, receipient, content)
        self.notes.append(newNote)
        print(f"# notes: {len(self.notes)}")
        self.store_notes()

    def remove_note(self, note):
        self.notes.remove(note)
        self.store_notes()

    def edit_note(self, edit_note):
        self.communicator.say("Vuoi cambiare il contenuto? ")
        answer = self.communicator.listen()
        if "sì" in answer.split():
            self.communicator.say("Dimmi il nuovo contenuto")
            edit_note.content = self.communicator.listen()
        self.communicator.say("Vuoi cambiare il destinatario? ")
        answer = self.communicator.listen()
        if "sì" in answer.split():
            self.communicator.say("Dimmi il nome del nuovo destinatario")
            to_who = self.communicator.listen()
            recipient = self.search_member_named(to_who)
            if recipient is None:
                self.communicator.say(f"Mi dispiace non ho trovato nessun membro chiamato {recipient}")
            else:
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

    '''Persistance'''

    def store_members(self):
        members_dict = {}
        for member in self.members:
            members_dict[member.name] = member.pictures
        pickle.dump(members_dict, open(os.path.join("..", "data", "members.pkl"), "wb"))

    def load_members(self):
        if os.path.getsize(os.path.join("..", "data", "members.pkl")) > 0:
            members_dict = pickle.load(open(os.path.join("..", "data", "members.pkl"), "rb"))
            for name in members_dict:
                self.members += [Member(name, members_dict[name])]
        self.load_notes()

    def store_notes(self):
        notes_dict = {}
        for note in self.notes:
            print(notes_dict.keys())
            if note.recipient.name in notes_dict.keys():
                notes_dict[note.recipient.name] += [{'sender': note.sender.name, 'content': note.content}]
                print(f"{note.sender.name} ha già note")
            else:
                notes_dict[note.recipient.name] = [{'sender': note.sender.name, 'content': note.content}]
                print(f"{note.sender.name} non ha note")
        print(notes_dict)
        pickle.dump(notes_dict, open(os.path.join("..", "data", "notes.pkl"), "wb"))
        print(f"stored {len(self.notes)} notes")

    def load_notes(self):
        if os.path.getsize(os.path.join("..", "data", "notes.pkl")) > 0:
            notes_dict = pickle.load(open(os.path.join("..", "data", "notes.pkl"), "rb"))
            print(notes_dict)
            for member in self.members:
                if member.name in notes_dict.keys():
                    notes_to_member = notes_dict[member.name]
                    for note in notes_to_member:
                        self.notes += [Note(self.search_member_named(note['sender']), member, note['content'])]
        print(f"load {len(self.notes)} notes")

    def save_frame(self, frame, member):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb, model="cnn")
        member.pictures.append(face_recognition.face_encodings(rgb, boxes))
        self.store_members()
