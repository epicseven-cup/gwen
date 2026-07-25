import argparse

def main():
    parser = argparse.ArgumentParser(description="Gwen CLI")

    parser.add_argument("--config", "-c", help="Path to configuration file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")

    parser.add_argument("--input-path", "-i", help="Path to input file")
    parser.add_argument("--output-path", "-o")


    args = parser.parse_args()


    with open("r", args.input_path) as f:
        f.read()










    # TODO: Implement command handling
    print("Gwen CLI initialized")



if __name__ == "__main__":
    main()
