import Member

class HomeAssistant:
    def __init__(self):
        # load data from db
        notes = self.loadNotes()
        members = self.loadMembers()



    def start(self):
        # start camera:Gabriel

        while True:
            if self.detectPresence():
                member = self.recognizeMember()
                if member == None:
                    # registrazione nuovo membro

                else:
                    # controlla messaggi
                    notes = self.checkNotes(member)
                    if notes == None:
                        # comunica non ci sono note
                        # Giulio
                    else:
                        # comunica che ci sono note
                        # Giulio
                    # capisci cosa vuole l'utente ????

    def detectPresence(self):
        # Gabriel
        pass

    def recognizeMember(self):
        # Gabriel
        # chiedi se è già membro
        pass

    def registerMember(self):
        # ask name
        # take pictures
        newMember = Member(name, pictures);
        pass

    def storeMember(self, member):
        # Giulio
        pass

    def loadMembers(self):
        # Giulio
        pass

    def storeNote(self, note):
        # Giulio
        # esempio: {"Antonio": [NoteObj, NoteObj],, "Fabio": [NoteObj, NoteObj]}
        pass
    def loadNotes(self):
        # Giulio
        pass
    def addNote(self, note):
        # Giulio
        # creare l'ogg nota e aggiungerlo al dizionario
        self.storeNote(note)
        pass
    def removeNote(self, note):
        # Giulio
        # creare l'ogg nota e aggiungerlo al dizionario
        pass
    def editNote(self, note):
        # Giulio
        # creare l'ogg nota e aggiungerlo al dizionario
        pass