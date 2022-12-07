import time
import sys
import src.AI.RunBTD6GeneticAlgo as training
import src.AI.RunBTD6Best as testing



def main():
    print("BloonsAI!\n\nOptions:\nTrain: T\nRun Best: R\n")
    option = ''
    option = input("What would you like to do? ")

    match option:
        case "T":
            training.train()
        case 'R':
            testing.test()
    




if __name__=="__main__":
    main()