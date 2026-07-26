import argparse
import pymupdf


BAD_BLOCK = (0,0,0,0)

def main():
    parser = argparse.ArgumentParser(description="Gwen CLI")

    parser.add_argument("--config", "-c", help="Path to configuration file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")

    parser.add_argument("--input-path", "-i", help="Path to input file")
    parser.add_argument("--output-path", "-o")


    args = parser.parse_args()


    pdf = pymupdf.open(args.input_path)



    for p in range(len(pdf)):
        page = pdf.load_page(p)
        raw_dict = page.get_text("dict")

        if not isinstance(raw_dict, dict):
            raise ValueError("Invalid text dictionary format")

        blocks = raw_dict.get("blocks", [])

        page_blocks = blocks[:]


        page_blocks.sort(key=lambda x: x["bbox"][1])

        page_width = page.rect.width
        for b in blocks:
            t = b.get("type", -1)

            x0, y0, x1, y1 = b.get("bbox", BAD_BLOCK)
            if (x0, y0, x1, y1) == BAD_BLOCK:
                raise ValueError("BAD BLOCK")


            if (x1 - x0) > page_width * 0.7:
                # Single column
                middle_page_block.append(b)
            elif (x1 - x0) > page_width * 0.5:
                right_page_block.append(b)
            else:
                left_page_block.append(b)


        left_page_block.sort(key=lambda xb: xb["bbox"][1])
        right_page_block.sort(key=lambda xb: xb["bbox"][1])








            match t:
                case 0:
                    pass
                case 1:
                    pass
                case _:
                    print("unknow block type passing")
                    continue
            pass















    # TODO: Implement command handling
    print("Gwen CLI initialized")



if __name__ == "__main__":
    main()
