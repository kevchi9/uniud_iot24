from data_parser import parse_data

def read_file_on_enter(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        print("Press Enter to read the next line (Ctrl+C to exit):")
        
        for line in lines:
            input()
            print(parse_data(1, '123,' + line.strip()))

    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':

    read_file_on_enter('source_data/electrics_to_serial.txt')