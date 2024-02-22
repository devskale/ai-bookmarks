import json
import os
import platform
import datetime


def find_bookmarks_path():
    system = platform.system()
    if system == "Windows":
        return os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'Bookmarks')
    elif system == "Darwin":  # macOS
        return os.path.join(os.environ['HOME'], 'Library', 'Application Support', 'Google', 'Chrome', 'Default', 'Bookmarks')
    elif system == "Linux":
        return os.path.join(os.environ['HOME'], '.config', 'google-chrome', 'Default', 'Bookmarks')
    else:
        raise Exception("Unsupported operating system.")


def convert_bookmarks_to_html(bookmarks_json_path, output_html_path):
    # Load bookmarks from the JSON file
    with open(bookmarks_json_path, 'r', encoding='utf-8') as file:
        bookmarks = json.load(file)

    # Start the HTML file content
    html_content = '<!DOCTYPE NETSCAPE-Bookmark-file-1>\n'
    html_content += '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">\n'
    html_content += '<TITLE>Bookmarks</TITLE>\n'
    html_content += '<H1>Bookmarks</H1>\n'
    html_content += '<DL><p>\n'

    def traverse_bookmarks(node, depth=0):
        nonlocal html_content
        if node['type'] == 'folder':
            html_content += '\t' * depth + '<DT><H3>' + \
                node['name'] + '</H3></DT>\n'
            html_content += '\t' * depth + '<DL><p>\n'
            for child in node.get('children', []):
                traverse_bookmarks(child, depth + 1)
            html_content += '\t' * depth + '</DL><p>\n'
        elif node['type'] == 'url':
            html_content += '\t' * depth + '<DT><A HREF="' + \
                node['url'] + '">' + node['name'] + '</A>\n'

    # Traverse the bookmarks tree starting from 'bookmark_bar' and 'other'
    for key in ['bookmark_bar', 'other']:
        traverse_bookmarks(bookmarks['roots'][key])

    html_content += '</DL><p>\n'

    # Save the HTML content to the specified output file
    with open(output_html_path, 'w', encoding='utf-8') as file:
        file.write(html_content)


# Use the find_bookmarks_path function to automatically determine the bookmarks file path
bookmarks_json_path = find_bookmarks_path()
# Update this to your desired output HTML file path
# filename shall be chromebookmarks+date.html
# get current date in the format YYYY-MM-DD
#
current_date = datetime.datetime.now().strftime('%Y-%m-%d')
output_html_path = './data/chromebookmarks' + current_date + '.html'
convert_bookmarks_to_html(bookmarks_json_path, output_html_path)
