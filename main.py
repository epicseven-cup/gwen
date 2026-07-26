import argparse
import pymupdf

from ebooklib import epub

BAD_BLOCK = (0,0,0,0)

def main():
    parser = argparse.ArgumentParser(description="Gwen CLI")

    parser.add_argument("--config", "-c", help="Path to configuration file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")

    parser.add_argument("--input-path", "-i", help="Path to input file")
    parser.add_argument("--output-path", "-o")


    args = parser.parse_args()


    pdf = pymupdf.open(args.input_path)

    new_pdf_blocks = []



    for p in range(len(pdf)):
        page = pdf.load_page(p)
        raw_dict = page.get_text("dict")

        if not isinstance(raw_dict, dict):
            raise ValueError("Invalid text dictionary format")

        blocks = raw_dict.get("blocks", [])

        page_blocks = blocks[:]
        # Sorting by the y axis
        page_blocks.sort(key=lambda x: x["bbox"][1])


        new_page_blocks = []
        right_blocks = []

        page_width = page.rect.width
        for b in page_blocks:
            x0, y0, x1, y1 = b.get("bbox", BAD_BLOCK)
            if (x0, y0, x1, y1) == BAD_BLOCK:
                raise ValueError("BAD BLOCK")
            if x0 > page_width * 0.7:
                # Single column
                new_page_blocks.append(b)
            elif x0 > page_width * 0.5:
                right_blocks.append(b)
            else:
                new_page_blocks.append(b)

        new_page_blocks.extend(right_blocks)
        new_pdf_blocks.append(new_page_blocks)


    book = epub.EpubBook()

    # Set metadata
    book.set_identifier("GB33BUKB20201555555555")
    book.set_title("The Book of the Mysterious")
    book.set_language("en")

    book.add_author("John Smith")
    book.add_author(
        "Hans Müller",
        file_as="Dr. Hans Müller",
        role="ill",
        uid="coauthor",
    )

    book.add_metadata("DC", "description", "A mysterious journey into hidden secrets")
    book.add_metadata("DC", "publisher", "Mystic Books Publishing House")


    for i in range(len(new_pdf_blocks)):
        chapter = epub.EpubHtml(title=f"Chapter {i}", file_name=f"Chapter {i}.xhtml", lang="en")
        content = new_pdf_blocks[i]





    # TODO: Implement command handling
    print("Gwen CLI initialized")



if __name__ == "__main__":
    main()
