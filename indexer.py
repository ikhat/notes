"""
Generate a markdown index tree of markdown files.

Original usage is to create a SUMMARY.md file for a gitbook. 
    
From the command line

    $ python indexer.py

will generate a  markdown index of all markdown files in the current working
directory and its sub folders, other than excluded files and folders, and write
output to `SUMMARY.md`, by default.

In getting the names of files, expects files to begin

`# NAME OF FILE`

and outputs links of the form

`  - [NAME OF FILE.md](./example/file.md)`

for a file `file.md' in the sub-folder `example` in the cwd. 

Options:
output file name can be specified
 $ python md_file_tree.py README.md

author: Ivan Khatchatourian
credit: re-worked from elfnor's code here:
        https://gist.github.com/elfnor/bc2176b3fad8581c678b771afb1e3b3e
        elfnor.com
"""
import os
import argparse

LIST_PREFIX = "-"
INDENT_SPACES = 2

def excluded_file(file):
    """Determine whether to exclude file from the index.
    Includes checking if file is a markdown file.
    """
    md_exts = ['.markdown', '.mdown', '.mkdn', '.mkd', '.md']
    if file[0] == '.': return True
    if os.path.splitext(file)[-1] not in md_exts: return True
    if file == "README.md" or file == "SUMMARY.md": return True
    return False


def get_page_name(file):
    """Get text to use as article name in index.
    Expects markdown files to have '# NAME' as their first line.
    """
    with open(file, 'r') as data:
        title_line = data.readline()
        title_line = title_line.rstrip()
        return title_line[2:]


def create_index(cwd):
    """Create markdown index of all included files in cwd and subfolders.
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
        dirs[:] = sorted([d for d in dirs if not (d[0] == '.' or os.path.relpath(os.path.join(root, d), cwd) in excluded_dirs)])
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
    """Find preexisting index in filename and replace it with the lines in new_index.
    If there is no preexisting index in filename, place new index at end of filename.
    If filename does not exist, create it and add new index to it with a 
    'Table of Contents' header.
    Only replace the first index block in file.
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
    """Generate index, optional cmd line arguments."""
    parser = argparse.ArgumentParser(
        description=('Generate a markdown index tree of markdown files in '
                     'current working directory and its sub folders. '
                     'Designed for making SUMMARY.md for GitBooks.'))

    parser.add_argument('filename',
                        nargs='?',
                        default='SUMMARY.md',
                        help="Desired name of markdown output file.")

    args = parser.parse_args()
    print('Creating index!')
    cwd = os.getcwd()
    output_lines = create_index(cwd)

    md_out_fn = os.path.join(cwd, args.filename)
    replace_index(md_out_fn, output_lines)

if __name__ == "__main__":
    main()