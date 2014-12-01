class BColors:
        REDTEXT = "\033[31m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        HEADER = "\033[95m"
        BLUE = "\033[94m"
        WARNING = "\033[93m"
        RED = "\033[91m"
        ENDC = "\033[0m"
        BOLD = "\033[1m"
        BLUE = "\033[34m"
        TEST = "\033[34m"

        def makeHeader(self,entryText):
                return self.HEADER + entryText + self.ENDC
        def makeGreen(self,entryText):
                return self.GREEN + entryText+ self.ENDC

        def makeBlue(self,entryText):
                return self.BLUE + entryText+ self.ENDC

        def makeRed(self,entryText):
                return self.RED + self.BOLD + entryText+ self.ENDC
        
        def makeRedText(self,entryText):
                return self.REDTEXT + entryText+ self.ENDC
        
        def makeYellow(self,entryText):
                return self.YELLOW + entryText+ self.ENDC
        
        def makeTest(self,entryText):
                return self.TEST + entryText+ self.ENDC
        
        def makeBlue(self,entryText):
                return self.BLUE + entryText+ self.ENDC
        
        
        def makeError(self,entryText):
                return self.WARNING + entryText+ self.ENDC

def main():
    BC = BColors()
    print(BC.makeHeader("makeHeader"))
    print(BC.makeGreen("makeGreen"))
    print(BC.makeBlue("makeBlue"))
    print(BC.makeRed("makeRed"))
    print(BC.makeRedText("makeRedText"))
    print(BC.makeYellow("makeRedText"))
    print(BC.makeTest("makeTest"))
    print(BC.makeError("makeError"))
    

if __name__ == "__main__":
    main()
