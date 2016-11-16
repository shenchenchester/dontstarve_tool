from __future__ import print_function
import os
import shutil
from datetime import datetime
import time
import stat
import save_reader as sr
import json

SAVE_DIR = 'C:/Users/ld/Documents/Klei/DoNotStarveTogether/Cluster_1/Master/save'
BACKUP_DIR = 'C:/Users/ld/Documents/Klei/helper/save'
INTERVAL = 8*60 # seconds
MAX_BACKUPS = 10

try:
    input = raw_input
except NameError:
    pass

def copytree(src, dst, symlinks = False, ignore = None):
    if not os.path.exists(dst):
        os.makedirs(dst)
        shutil.copystat(src, dst)
    lst = os.listdir(src)
    if ignore:
        excl = ignore(src, lst)
        lst = [x for x in lst if x not in excl]
    for item in lst:
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if symlinks and os.path.islink(s):
            if os.path.lexists(d):
                os.remove(d)
            os.symlink(os.readlink(s), d)
            try:
                st = os.lstat(s)
                mode = stat.S_IMODE(st.st_mode)
                os.lchmod(d, mode)
            except:
                pass # lchmod not available
        elif os.path.isdir(s):
            copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

def remove(d):
    if os.path.exists(d):
        shutil.rmtree(d)
        print('removed', d)

def backup(dst=None, trunc=True):
    if not dst:
        t = datetime.now()
        dirname = t.strftime('%y%m%d_%H%M%S')
        dst = BACKUP_DIR + '/' + dirname

    copytree(SAVE_DIR, dst)
    print('backup to', dst)

    # remove old backups
    if trunc:
        backups = get_backups()
        print(backups)
        if len(backups) > MAX_BACKUPS:
            to_remove = backups[:len(backups) - MAX_BACKUPS]
            for b in to_remove:
                d = BACKUP_DIR +'/' + b
                remove(d)

def loop():
    print('running backup')
    lasttime = time.time()
    while True:
        time.sleep(INTERVAL)
        save_path = SAVE_DIR
        session = sr.load_saveindex(save_path, use_cache=False)
        if session and session['time'] - lasttime > 0:
            t = datetime.fromtimestamp(session['time'])
            dirname = '{}_{}'.format(t.strftime('%y%m%d_%H%M%S'), session['summary']['days'])
            dst = os.path.join(BACKUP_DIR, dirname)
            backup(dst)
            lasttime = session['time']
        else:
            print('save not updated, skip backup')

def get_backups():
    if not os.path.exists(BACKUP_DIR):
        return []
    return list(sorted(os.listdir(BACKUP_DIR)))

def restore(b):
    d = BACKUP_DIR +'/' + b
    tmp = BACKUP_DIR + '/restore'
    remove(tmp)
    backup(dst=tmp, trunc=False)
    shutil.rmtree(SAVE_DIR)
    copytree(d, SAVE_DIR)
    print('restore', d)

def menu():
    print('1. start backup every {:.1f} minutes\n\
2. restore a previous backup\n\
3. exit'.format(INTERVAL/60.0))
    n = input('input number(1 by default):')
    if n=='1' or n == '':
        loop()
    elif n=='2':
        print(0, 'current')
        save_path = SAVE_DIR
        session = sr.load_saveindex(save_path, use_cache=False)
        if session:
            print(' ', session['summary']['title'])
        else:
            print('not available')
        backups = get_backups()
        for i, d in enumerate(backups):
            print(i+1, d)
            save_path = os.path.join(BACKUP_DIR, d)
            session = sr.load_saveindex(save_path, use_cache=True)
            if session:
                print(' ', session['summary']['title'])
            else:
                print('not available')
        k = input('input number:')
        print(k, len(backups))
        to_restore = 0
        try:
            if int(k)==0:
                print('keep current')
                return
            to_restore = backups[int(k)-1]
        except:
            print('invalid input!')
            return
        restore(to_restore)
    elif n=='3':
        return
    else:
        print('invalid input!')

def main():
    menu()
    print('exit')
    time.sleep(0.5)

main()
