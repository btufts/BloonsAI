import time
import sys
import src.AI.RunBTD6GeneticAlgo as training



def main():
    print("BloonsAI!\n\nOptions:\nTrain: T\nRun Best: R\n")
    option = ''
    option = input("What would you like to do? ")

    match option:
        case "T":
            training.train()
        case 'R':
            print("Run Best Algo so far (not implimented)")
    




if __name__=="__main__":
    main()