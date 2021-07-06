from HomeAssistant import HomeAssistant

if __name__ == "__main__":
    HA = HomeAssistant(False, False, True)
    HA.start()
