import os
import sys

class DataProcessor:
    def __init__(self):
        self.data = []
    
    def process(self):
        # TODO: add error handling
        for item in self.data:
            print(f"Processing {item}")

def main():
    processor = DataProcessor()
    processor.process()

if __name__ == "__main__":
    main()