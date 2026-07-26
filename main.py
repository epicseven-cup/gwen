import argparse
import json
import os
import re

import markdown as md_lib
import pymupdf.layout  # noqa: F401  must be imported first to activate the layout engine
import pymupdf4llm

from ebooklib import epub

IMAGE_DIR = "images"

PICTURE_TEXT_RE = re.compile(
    r"<!-- Start of picture text -->.*?<!-- End of picture text -->\s*",
    re.DOTALL,
)


def strip_picture_text(md_text):
    """pymupdf4llm dumps the raw text it detects inside picture/figure regions
    as these comment-wrapped blocks, often duplicating content that's already
    extracted properly elsewhere (e.g. as a real table) or that belongs to a
    figure with no other faithful representation. Drop it either way."""
    return PICTURE_TEXT_RE.sub("", md_text)


def prompt_for_metadata():
    identifier = input("Book identifier: ").strip()
    title = input("Book title: ").strip()
    language = input("Language [en]: ").strip() or "en"

    authors = []
    print("Enter authors (leave name blank to stop):")
    while True:
        name = input("  Author name: ").strip()
        if not name:
            break
        file_as = input("  File as [same as name]: ").strip() or None
        role = input("  Role [aut]: ").strip() or None
        uid = input("  UID [auto]: ").strip() or None
        authors.append({"name": name, "file_as": file_as, "role": role, "uid": uid})

    description = input("Description [none]: ").strip() or None
    publisher = input("Publisher [none]: ").strip() or None

    metadata = {"identifier": identifier, "title": title, "language": language, "authors": authors}
    if description:
        metadata["description"] = description
    if publisher:
        metadata["publisher"] = publisher
    return metadata


def main():
    parser = argparse.ArgumentParser(description="Gwen CLI")

    parser.add_argument("--config", "-c", help="Path to configuration file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")

    parser.add_argument("--input-path", "-i", default="input.pdf", help="Path to input file (default: input.pdf)")
    parser.add_argument("--output-path", "-o", default="output.epub", help="Path to output epub file (default: output.epub)")
    parser.add_argument("--metadata", "-m", help="Path to JSON file with book metadata")
    parser.add_argument(
        "--interactive", "-I", action="store_true",
        help="Prompt for book metadata one field at a time instead of reading --metadata",
    )

    args = parser.parse_args()

    if args.interactive:
        metadata = prompt_for_metadata()
    elif args.metadata:
        with open(args.metadata) as f:
            metadata = json.load(f)
    else:
        parser.error("the following arguments are required: --metadata/-m (or pass --interactive/-I)")

    os.makedirs(IMAGE_DIR, exist_ok=True)
    md_text = pymupdf4llm.to_markdown(args.input_path, write_images=True, image_path=IMAGE_DIR)
    md_text = strip_picture_text(md_text)

    book = epub.EpubBook()

    # Set metadata
    book.set_identifier(metadata["identifier"])
    book.set_title(metadata["title"])
    book.set_language(metadata.get("language", "en"))

    for author in metadata.get("authors", []):
        author_kwargs = {}
        if author.get("file_as"):
            author_kwargs["file_as"] = author["file_as"]
        if author.get("role"):
            author_kwargs["role"] = author["role"]
        if author.get("uid"):
            author_kwargs["uid"] = author["uid"]
        book.add_author(author["name"], **author_kwargs)

    if "description" in metadata:
        book.add_metadata("DC", "description", metadata["description"])
    if "publisher" in metadata:
        book.add_metadata("DC", "publisher", metadata["publisher"])

    style = epub.EpubItem(
        uid="style",
        file_name="style/style.css",
        media_type="text/css",
        content=(
            "body { margin: 1em; line-height: 1.4; }\n"
            "p { margin: 0 0 1em 0; text-align: justify; }\n"
            "h1, h2, h3, h4, h5, h6 { margin: 1em 0 0.5em 0; text-align: left; line-height: 1.2; }\n"
            "img { max-width: 100%; height: auto; display: block; margin: 1em auto; }\n"
            "pre { background: #2b2b2b; color: #f0f0f0; padding: 0.75em; margin: 0 0 1em 0;"
            " overflow-x: auto; border-radius: 4px; }\n"
            "pre code { font-family: monospace; white-space: pre; }\n"
            "table { border-collapse: collapse; width: 100%; margin: 0 0 1em 0; }\n"
            "th, td { border: 1px solid #999; padding: 0.4em 0.6em; text-align: left; }\n"
            "th { background: #eee; font-weight: bold; }\n"
        ),
    )
    book.add_item(style)

    pages = md_text.split("\n\n-----\n\n")

    chapters = []
    for i, page_md in enumerate(pages):
        html_body = md_lib.markdown(page_md, extensions=["tables", "fenced_code"])

        chapter = epub.EpubHtml(
            title=f"Page {i + 1}",
            file_name=f"page_{i + 1}.xhtml",
            lang="en",
        )
        chapter.content = html_body
        chapter.add_item(style)

        chapters.append(chapter)
        book.add_item(chapter)

    for fname in sorted(os.listdir(IMAGE_DIR)):
        path = os.path.join(IMAGE_DIR, fname)
        if not os.path.isfile(path):
            continue
        with open(path, "rb") as f:
            content = f.read()
        ext = fname.rsplit(".", 1)[-1]
        image_item = epub.EpubImage(
            uid=fname,
            file_name=f"{IMAGE_DIR}/{fname}",
            media_type=f"image/{ext}",
            content=content,
        )
        book.add_item(image_item)

    book.toc = tuple(chapters)
    book.add_item(epub.EpubNav())
    book.add_item(epub.EpubNcx())
    book.spine = ["nav"] + chapters

    epub.write_epub(args.output_path, book)

    print(f"Wrote {args.output_path}")


if __name__ == "__main__":
    main()
