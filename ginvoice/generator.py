# GinVoice - Creating LaTeX invoices with a GTK GUI
# Copyright (C) 2021  Erik Nijenhuis <erik@xerdi.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import argparse
import json
import os
import re
import sys

from ginvoice.environment import image_dir

filename = 'generated_vars.tex'

cmd_template = '\\newcommand{\\%s}{%s}\n'
global_cmd_template = '\\global\\def\\%s{%s}\n'
bool_template = '\\newbool{%s}\n\\global\\bool%s{%s}'


def to_roman(n):
    """ Convert an integer to a Roman numeral. """

    if not isinstance(n, type(1)):
        raise "expected integer, got %s" % type(n)
    if not 0 < n < 4000:
        raise "Argument must be between 1 and 3999"
    ints = (1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1)
    nums = ('M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I')
    result = []
    for i in range(len(ints)):
        count = int(n / ints[i])
        result.append(nums[i] * count)
        n -= ints[i] * count
    return ''.join(result)


pre_escape_chars = {
    '&': r'\&',
    '%': r'\%',
    '$': r'\$',
    '#': r'\#',
    '_': r'\_',
    # '{': r'\{',
    # '}': r'\}',
    '~': r'\textasciitilde{}',
    '^': r'\^{}',
    '\\\\': r'\textbackslash{}'
}

post_escape_chars = {
    '<': r'\textless{}',
    '>': r'\textgreater{}'
}


def escape_tex(text, conv):
    regex = re.compile('|'.join(re.escape(str(key)) for key in sorted(conv.keys(), key=lambda item: - len(item))))
    return regex.sub(lambda match: conv[match.group()], text)


def format_tex(text):
    text = escape_tex(text, pre_escape_chars)
    text = re.sub(r'(.*?)<b>(.*?)</b>(.*?)', r'\1\\textbf{\2}\3', text)
    text = re.sub(r'(.*?)<u>(.*?)</u>(.*?)', r'\1\\underline{\2}\3', text)
    text = re.sub(r'(.*?)<i>(.*?)</i>(.*?)', r'\1\\textit{\2}\3', text)
    text = escape_tex(text, post_escape_chars)
    return text


GENERATORS = dict()


def generator(label):
    def _decorator(func):
        global GENERATORS
        GENERATORS[label] = func
        return func

    return _decorator


def parse_map(data):
    return "\n" + "\n".join(["\t%s & %s \\\\" % (format_tex(x['key']), format_tex(x['val'])) for x in data]) + "\n"


@generator("languages")
def generate_languages(f, data):
    f.write("\\usepackage[%s]{babel}" % ','.join(data))


@generator("header")
def generate_header(f, data):
    f.write(global_cmd_template % ('subtitle', format_tex(data['subtitle'])))


@generator("addressee")
def generate_addressee(f, data):
    f.write(cmd_template % ('addressee', '\\\\'.join([format_tex(x) for x in data])))


@generator("customer_info")
def generate_customer_info(f, data):
    f.write(cmd_template % ('customerinfo', parse_map(data)))


@generator("supplier_info")
def generate_customer_info(f, data):
    f.write(cmd_template % ('supplierinfo', parse_map(data)))


@generator("table")
def generate_table(f, data):
    columns = data['columns']
    column_count = len(columns)

    buf = []
    f.write("\\newlength{\\rowsize}\n")
    f.write("\\setlength{\\rowsize}{\\linewidth}\n")
    for i, c in enumerate(columns):
        if isinstance(c['width'], str):
            f.write("\\newlength{\\c%ssize}\n" % to_roman(i))
            f.write("\\settowidth{\\c%ssize}{%s}\n" % (to_roman(i), format_tex(c['width'])))
            f.write("\\addtolength{\\rowsize}{-\\c%ssize}\n" % to_roman(i))
            f.write("\\addtolength{\\rowsize}{-2\\tabcolsep}\n")
            buf.append("%s{%s}" % (c['type'], "\\c%ssize" % to_roman(i)))
        else:
            buf.append("%s{%.2f\\rowsize-2\\tabcolsep}" % (c['type'], c['width']))

    f.write(cmd_template % ('columncount', column_count))
    f.write("\\newcolumntype\\columndef{%s}\n" % ' '.join(buf))

    f.write(cmd_template % ('tableheader', '%s\\\\' % (
        '&'.join("\\rowheadercolor{}%s" % (format_tex(c['title'])) for c in columns)
    )))

    def format_cells(row):
        new_row = list()
        for idx, cell in enumerate(row):
            c = columns[idx]
            if c['type'] == 'F':
                new_row.append("\\currency\\hfill\\financial{%.2f}" % cell)
            else:
                new_row.append(format_tex(cell))
        return new_row

    f.write(cmd_template % ('tablerecords',
                            ''.join([
                                "\n\t%s\\\\" % " & ".join(format_cells(x)) for x in data['records']
                            ])))

    f.write(cmd_template % ('cumoffset', '& '.join('' for x in range(column_count - 1))))
    cum_row = ""
    # cum_row = "\\cline{%d-%d}\n" % (column_count-1, column_count)
    f.write(cmd_template % ('tablefooter',
                            cum_row.join(
                                ["\\cum{%s}{%.2f}\n" % (format_tex(r['key']), r['val']) for r in data['cumulative']])))


@generator("footer")
def generate_footer(f, data):
    graphics_extensions = ["pdf", "png", "jpg", "mps", "jpeg", "jbig2", "jb2", "PDF", "PNG", "JPG", "JPEG",
                           "JBIG2", "JB2", "eps"]
    f.write(cmd_template % ('theending', format_tex(data['ending'])))

    def include_graphics(file):
        fn, ext = file.split('.')
        if ext in graphics_extensions:
            return "\t\\includegraphics[width=.1\\textwidth]{%s}\n" % fn
        elif ext == 'svg':
            return "\t\\includesvg[width=.1\\textwidth]{%s}\n" % fn

    # Don't forget to add trailing slash
    f.write("\\graphicspath{{%s/}}\n" % image_dir)
    images = [include_graphics(os.path.basename(x)) for x in data['images']]
    f.write(cmd_template % ('images', '\n' + '\t\\hspace{1.5em}\n'.join(images)))
    f.write("\n")


def generate_color(name, target, value):
    color_def_template = "\\definecolor{%s}{HTML}{%s}\n"
    color_let_template = "\\colorlet{%s}{%s}\n"

    return "%s%s" % (
        color_def_template % (name, value[1:]),  # Remove hash from color data
        color_let_template % (target, name)
    )


@generator("style")
def generate_style(f, data):
    f.write(generate_color('backgroundcolor', 'bgcolor', data['background_color']))
    f.write(generate_color('accentcolor', 'textcolor', data['accent_color']))
    f.write("\n")
    if 'main_font' in data:
        if data['main_font']:
            f.write("\\setmainfont{%s}\n" % data['main_font'])
    if 'mono_font' in data:
        if data['mono_font']:
            f.write("\\setmonofont{%s}\n" % data['mono_font'])
    key_name = 'styletable'
    f.write(bool_template % (key_name, 'true' if data['style_table'] else 'false', key_name))
    f.write("\n")


@generator("misc")
def generate_misc(f, data):
    for k, v in data.items():
        f.write(global_cmd_template % (k, format_tex(v)))


def main():
    parser = argparse.ArgumentParser(prog="gingen",
                                     usage="%(prog)s [options] []",
                                     description="%(prog)s - generate an invoice"
                                     )
    parser.add_argument('-d', '--directory', nargs='?', default='.',
                        help="Set the LaTeX Invoice Template directory. Defaults to current working directory.")
    parser.add_argument('request', nargs='?', type=argparse.FileType('r'), default=sys.stdin,
                        help="JSON formatted request payload. Use a JSON file or pass it using a stdin.")

    args = parser.parse_args(sys.argv[1:])
    os.chdir(args.directory)

    tex_file_mapping = {
        "languages.tex": ["languages"],
        "header.tex": ["header"],
        "customer_info.tex": ["customer_info"],
        "supplier_info.tex": ["supplier_info"],
        "addressee.tex": ["addressee"],
        "table.tex": ["table"],
        "footer.tex": ["footer"],
        "style.tex": ["style"],
        "meta.tex": ["misc"]
    }
    data = json.load(args.request)
    for file, sections in tex_file_mapping.items():
        with open(file, mode='w', encoding='utf-8') as tex_file:
            for section in sections:
                if section not in data:
                    print("Error: No such key %s provided in request" % section)
                    continue
                if section not in GENERATORS:
                    print("Error: No such generator registered by name %s" % section)
                    continue
                GENERATORS[section](tex_file, data[section])


if __name__ == '__main__':
    main()
