#!/usr/bin/env python3
import os
import sys

class DataProcessor:
    def __init__(self):
        self.data = []
    
    def process_data(self):
        # TODO: implement error handling
        for item in self.data:
            print(f"Processing {item}")
    
    def calculate_sum(self, numbers):
        return sum(numbers)

def main():
    processor = DataProcessor()
    processor.process_data()
    
    # Test function call
    result = processor.calculate_sum([1, 2, 3, 4, 5])
    print(f"Sum: {result}")

if __name__ == "__main__":
    main()
