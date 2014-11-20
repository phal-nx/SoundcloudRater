class BColors:
        HEADER = "\033[95m"
        BLUE = "\033[94m"
        GREEN = "\033[92m"
        WARNING = "\033[93m"
        RED = "\033[91m"
        ENDC = "\033[0m"
        BOLD = "\033[1m"


        def makeHeader(self,entryText):
                return self.HEADER + entryText + self.ENDC
        def makeGreen(self,entryText):
                return self.GREEN + entryText+ self.ENDC

        def makeBlue(self,entryText):
                return self.BLUE + entryText+ self.ENDC

        def makeRed(self,entryText):
                return self.RED + self.BOLD + entryText+ self.ENDC
        
        def makeError(self,entryText):
                return self.WARNING + entryText+ self.ENDC
