# -*- coding: utf-8 -*-
"""
https://gist.github.com/elfnor/bc2176b3fad8581c678b771afb1e3b3e

Generate a file tree table of contents for a directory of markdown files
run from command line:
    $ python md_file_tree.py
will generate a  markdown index of all markdown files in the current working
directory and its sub folders and insert it into  a file `index.md`.
If a previous index exists in the file it will be replaced,
otherwise a new index will be created at the end of the file
or a new file created.
The index will be linked to the files
eg.
`  - [how_to_take_notes.md](./notetaking/how_to_take_notes.md)`
for a link to a file `how_to_take_notes.md` in the sub-folder `notetaking`
Options:
the filename can be explicitly specified
 $ python md_file_tree.py README.md
-f:  The headers in each file will be listed under the file link
-w:  Wikilink syntax `[[./notetaking/how_to_take_notes.md]]`
     will be used instead of common markdown
author: elfnor <elfnor.com>
credit : the code in get_headers comes from
         https://github.com/amaiorano/md-to-toc
"""
import os
import argparse

LIST_PREFIX = "-"
INDENT_SPACES = 2

def excluded_file(file):
    md_exts = ['.markdown', '.mdown', '.mkdn', '.mkd', '.md']
    return file[0] == '.' or os.path.splitext(file)[-1] not in md_exts or file == "README.md" or file == "SUMMARY.md"


def get_page_name(file):
    """get text after the first header in the file, to use as article name
    """
    with open(file, 'r') as data:
        title_line = data.readline()
        title_line = title_line.rstrip()
        return title_line[2:]


def create_index(cwd):
    """create markdown index of all markdown files in cwd and sub folders
    """
    excluded_dirs = []
    try:
        with open(".gitignore") as file:
            for line in file.readlines():
                line = line.strip()
                if line[-1] == "/":
                    excluded_dirs.append(line[:-1])
    except FileNotFoundError:
        pass

    base_level = cwd.count(os.sep)
    output_lines = []
    output_lines.append('<!-- index start -->\n\n')
    for root, dirs, files in os.walk(cwd):
        files = sorted([f for f in files if not excluded_file(f)])
        dirs[:] = sorted([d for d in dirs if not (d[0] == '.' or os.path.relpath(os.path.join(root, d), cwd) in excluded_dirs )])
        if len(files) > 0:
            level = root.count(os.sep) - base_level
            if root != cwd:
                folder_page = os.path.join(root, "-" + os.path.basename(root) + ".md")
                page_name = get_page_name(folder_page)
                indent = ' ' * INDENT_SPACES * (level - 1)
                output_lines.append('{0}{3} [{1}]({2})\n'.format(indent,
                                                                 page_name,
                                                                 os.path.relpath(folder_page, cwd),
                                                                 LIST_PREFIX))
            for md_filename in files:
                if md_filename[0] != "-":
                    md_file = os.path.join(root, md_filename)
                    indent = ' ' * INDENT_SPACES * level
                    output_lines.append('{0}{3} [{1}]({2})\n'.format(indent,
                                                                     get_page_name(md_file),
                                                                     os.path.relpath(md_file, cwd),
                                                                     LIST_PREFIX))

    output_lines.append('\n<!-- index end -->\n')
    return output_lines


def replace_index(filename, new_index):
    """Finds the old index in filename and replaces it with the lines in new_index.
    If there is no existing index in filename, places new index at end of filename.
    If filename doesn't exist, creates it and adds new index to it with a 
    'Table of Contents' header.
    Only replaces the first index block in file.
    """
    lines_before_index = []
    lines_after_index = []
    before = True
    after = False
    try:
        with open(filename, 'r') as md_in:
            for line in md_in:
                if '<!-- index start' in line:
                    before = False
                if '<!-- index end' in line:
                    after = True
                if before:
                    lines_before_index.append(line)
                if after:
                    lines_after_index.append(line)
    except FileNotFoundError:
        new_index.insert(0, '# Table of Contents\n\n')
        print("{0} does not exist. Created it!".format(os.path.split(filename)[1]))

    with open(filename, 'w') as md_out:
        md_out.writelines(lines_before_index)
        md_out.writelines(new_index)
        md_out.writelines(lines_after_index[1:])


def main():
    """generate index optional cmd line arguments"""
    parser = argparse.ArgumentParser(
        description=('Generate a markdown index tree of markdown files in '
                     'current working directory and its sub folders. '
                     'Designed for making SUMMARY.md for GitBooks.'))

    parser.add_argument('filename',
                        nargs='?',
                        default='SUMMARY.md',
                        help="Desired name of markdown output file.")
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help='More verbose output.')

    args = parser.parse_args()
    cwd = os.getcwd()
    output_lines = create_index(cwd)

    md_out_fn = os.path.join(cwd, args.filename)
    replace_index(md_out_fn, output_lines)


if __name__ == "__main__":
    main()