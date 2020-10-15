def getInput(birds, coco):
    print("How many ounces of birds are carrying the coconuts? ")
    birds = input()
    print("How many pounds of coconuts are there? ")
    coco = input()
    return birds, coco

def main():
    birds = 0
    coco = 0
    [birds, coco] = getInput(birds, coco)
    
    if (float(birds) / float(coco) >= 5.5):
        print("Yes! Carrying the coconuts is possible.")
    else:
        print("No.")

if __name__ == '__main__':
    main()