from flask import Flask, request, render_template
import os
import string
from ctypes import windll

app = Flask(__name__)
username = os.environ['username']
home = os.path.abspath(f'C:\\Users\\{username}\\')
# reference
# https://stackoverflow.com/questions/827371/is-there-a-way-to-list-all-the-available-windows-drives
drives = []
bitmask = windll.kernel32.GetLogicalDrives()
for letter in string.ascii_uppercase:
    drive_root_path = str(letter + ':')
    if bitmask & 1:
        drives.append((drive_root_path, drive_root_path))
    bitmask >>= 1
# reference end


def get_folder(path):
    path_split = path.split('\\')
    path_cascade = []
    for i in range(len(path_split)):
        path_cascade.append((
            path_split[i],
            r'\\'.join(path_split[:i+1])
        ))
    if path.endswith(':'):  # root directory of a disk
        # os.listdir('C:') will return current folder
        # os.listdir('C:\\') is correct
        path += '\\'
    if os.path.isdir(path):
        sub_folders = []
        isdir = True
        try:
            for x in os.listdir(path):
                x_full_path = r'\\'.join(path_split) + r'\\' + x
                if os.path.isdir(x_full_path) or os.path.isfile(x_full_path):
                    sub_folders.append((x, x_full_path))
        except PermissionError:
            sub_folders = None
            isdir = False
    elif os.path.isfile(path):
        sub_folders = None
        isdir = False
    else:
        sub_folders = None
        isdir = False
    return {'path_cascade': path_cascade, 'sub_folders': sub_folders, 'isdir': isdir,
            'current_folder': path, 'drives': drives}


@app.route('/')
def main():
    return render_template('main.html')


@app.route('/fs', methods=['GET'])
def new_article():
    path = request.args.get('path', type=str, default=home)
    kwargs = get_folder(path)
    return render_template(
        'fs_widget.html',
        container_id='new_article', web_path='/fs', **kwargs
    )


if __name__ == '__main__':
    app.run()
